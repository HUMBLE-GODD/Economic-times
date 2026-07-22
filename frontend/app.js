const state = {
  token: localStorage.getItem("safety_token"),
  refresh: localStorage.getItem("safety_refresh"),
  user: null,
  zones: [],
  assets: [],
  roles: {},
  twin: null,
  simulation: null,
  twinAnimation: null,
};

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const headers = options.headers || {};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  if (options.body && !headers["Content-Type"]) headers["Content-Type"] = "application/json";
  const res = await fetch(path, { ...options, headers });
  if (res.status === 401) {
    if (!options._retried && state.refresh) {
      const refreshed = await refreshAccessToken();
      if (refreshed) return api(path, { ...options, _retried: true });
    }
    localStorage.removeItem("safety_token");
    localStorage.removeItem("safety_refresh");
    state.token = null;
    state.refresh = null;
    showLogin();
    throw new Error("Session expired. Sign in again and retry.");
  }
  if (!res.ok) {
    const text = await res.text();
    let message = text;
    try {
      const parsed = JSON.parse(text);
      message = parsed.detail || text;
    } catch {}
    throw new Error(message);
  }
  return res.json();
}

async function refreshAccessToken() {
  try {
    const res = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: state.refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    state.token = data.access_token;
    localStorage.setItem("safety_token", state.token);
    return true;
  } catch {
    return false;
  }
}

function showResult(el, value) {
  el.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
}

function safeList(value) {
  return Array.isArray(value) ? value : [];
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function statusPill(value) {
  const text = String(value || "unknown");
  return `<span class="pill ${escapeHtml(text)}">${escapeHtml(text.replaceAll("_", " "))}</span>`;
}

function niceLabel(value) {
  return String(value ?? "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, char => char.toUpperCase());
}

function formatNumber(value, digits = 1) {
  const number = Number(value);
  if (!Number.isFinite(number)) return String(value ?? "-");
  if (Number.isInteger(number)) return number.toLocaleString();
  return number.toFixed(digits).replace(/\.?0+$/, "");
}

function formatMetricValue(value) {
  if (typeof value === "number") return formatNumber(value, value < 1 ? 3 : 2);
  if (value && typeof value === "object") {
    return Object.entries(value).map(([key, nested]) => `${key.toUpperCase()} ${formatMetricValue(nested)}`).join(" · ");
  }
  return String(value ?? "-");
}

function metricChips(metrics) {
  return Object.entries(metrics || {}).map(([key, value]) => `<span class="metric-chip"><b>${escapeHtml(niceLabel(key))}</b> ${escapeHtml(formatMetricValue(value))}</span>`).join("");
}

function summarizeAuditDetails(details) {
  if (!details) return "";
  try {
    const parsed = typeof details === "string" ? JSON.parse(details) : details;
    return Object.entries(parsed).slice(0, 4).map(([key, value]) => `${niceLabel(key)}: ${formatMetricValue(value)}`).join(" · ");
  } catch {
    return String(details).slice(0, 160);
  }
}

function roleLabel(role, roles) {
  return roles?.[role]?.label || niceLabel(role);
}

function moduleTags(modules) {
  return safeList(modules).map(module => `<span>${escapeHtml(niceLabel(module))}</span>`).join("");
}

function renderMiniGrid(el, data) {
  el.innerHTML = Object.entries(data || {}).map(([key, value]) => `<div><span>${escapeHtml(key.replaceAll("_", " "))}</span><strong>${escapeHtml(value ?? 0)}</strong></div>`).join("");
}

function renderList(title, values) {
  const items = safeList(values).map(v => `<div class="result-row">${escapeHtml(v)}</div>`).join("");
  return `<strong>${escapeHtml(title)}</strong><div class="result-list">${items || "<span class='muted'>None</span>"}</div>`;
}

function downloadText(filename, text) {
  const blob = new Blob([text], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function showLogin() {
  $("loginView").classList.remove("hidden");
  $("appView").classList.add("hidden");
}

function showApp() {
  $("loginView").classList.add("hidden");
  $("appView").classList.remove("hidden");
}

function scoreClass(value) {
  if (value >= 80) return "score crit";
  if (value >= 55) return "score warn";
  return "score";
}

function renderTable(el, rows, cols) {
  if (!rows || !rows.length) {
    el.innerHTML = "<p class='muted'>No records</p>";
    return;
  }
  const keys = cols || Object.keys(rows[0]).slice(0, 8);
  el.innerHTML = `<table><thead><tr>${keys.map(k => `<th>${k}</th>`).join("")}</tr></thead><tbody>${
    rows.map(r => `<tr>${keys.map(k => {
      const value = r[k];
      if (["status", "health_status", "maintenance_priority"].includes(k)) return `<td>${statusPill(value)}</td>`;
      return `<td>${escapeHtml(String(value ?? "").slice(0, 180))}</td>`;
    }).join("")}</tr>`).join("")
  }</tbody></table>`;
}

function renderItems(el, rows, mapFn) {
  el.innerHTML = (rows || []).map(row => `<div class="item">${mapFn(row)}</div>`).join("");
}

async function login(email, password) {
  const data = await api("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  state.token = data.access_token;
  state.refresh = data.refresh_token;
  state.user = data.user;
  localStorage.setItem("safety_token", state.token);
  localStorage.setItem("safety_refresh", state.refresh);
  $("userLabel").textContent = `${data.user.name} · ${data.user.role}`;
  showApp();
  await loadAll();
}

async function loadMission() {
  const data = await api("/api/mission-control");
  const m = data.metrics;
  $("statusStrip").innerHTML = `Average risk ${m.avg_risk ?? 0} · Max risk ${m.max_risk ?? 0} · Open maintenance ${m.maintenance_open} · Pending permits ${m.permits_pending} · Compliance reviews ${m.compliance_reviews}`;
  $("kpiGrid").innerHTML = Object.entries(m).map(([k, v]) => `<div class="kpi"><span>${k.replaceAll("_", " ")}</span><strong>${v ?? 0}</strong></div>`).join("");
  renderItems($("topRisks"), data.top_risks, r => `<strong>${r.title}</strong><small>${r.category} · <span class="${scoreClass(r.compound_risk_score)}">${r.compound_risk_score}</span> · ${r.status}</small><small>${r.reasoning}</small>`);
  renderItems($("alerts"), data.alerts, r => `<strong>${r.title}</strong><small>${r.severity} · ${r.channel} · ${r.status}</small><small>${r.message}</small>`);
}

async function loadPlants() {
  const data = await api("/api/plants");
  state.zones = data.zones;
  const zoneOptions = data.zones.map(z => `<option value="${escapeHtml(z.id)}">${escapeHtml(z.name)}</option>`).join("");
  $("permitZone").innerHTML = zoneOptions;
  $("simulationZone").innerHTML = zoneOptions;
  if (data.zones.some(z => z.id === "zone_tank_farm")) $("simulationZone").value = "zone_tank_farm";
  const plant = data.plants?.[0];
  if (plant) {
    $("statusStrip").dataset.plant = `${plant.name} · ${plant.city}, ${plant.state}`;
  }
}

function populatePermitAssets() {
  const zoneId = $("permitZone").value;
  const assets = state.assets.filter(asset => !zoneId || asset.zone_id === zoneId).slice(0, 80);
  $("permitEquipment").innerHTML = `<option value="">No specific asset</option>` + assets.map(asset => `<option value="${escapeHtml(asset.id)}">${escapeHtml(asset.name)} · ${escapeHtml(asset.health_status)} · ${escapeHtml(asset.zone_name)}</option>`).join("");
}

async function loadOperations(q = "") {
  const data = await api(`/api/incidents${q ? `?q=${encodeURIComponent(q)}` : ""}`);
  renderTable($("incidentTable"), data.incidents, ["id", "event_date", "state", "city", "severity_score", "event_title", "source_title", "narrative"]);
}

async function loadTwin() {
  state.twin = await api("/api/digital-twin");
  renderItems($("zoneList"), state.twin.zones, z => `<strong>${escapeHtml(z.name)}</strong><small>${escapeHtml(z.zone_type)} · Risk ${escapeHtml(z.risk_score)} · Hazards ${escapeHtml(Math.round(z.hazard_density || 0))}</small>`);
  renderTwinSummary();
  drawTwin();
  startTwinAnimation();
}

function getTwinIntensity() {
  const control = $("simulationIntensity");
  return Math.min(1, Math.max(0.1, Number(control?.value || 0.8)));
}

function getTwinMinute() {
  const control = $("simulationTime");
  return Math.max(0, Number(control?.value || 30));
}

function updateTwinControls() {
  if ($("simulationIntensityValue")) $("simulationIntensityValue").textContent = `${getTwinIntensity().toFixed(1)}x`;
  if ($("simulationTimeValue")) $("simulationTimeValue").textContent = `${getTwinMinute()} min`;
}

function activeSimulationMatchesControls() {
  const sourceId = $("simulationZone")?.value;
  return Boolean(
    state.simulation?.propagation?.length
    && (!sourceId || state.simulation.source_zone?.id === sourceId)
    && Math.abs(Number(state.simulation.intensity ?? getTwinIntensity()) - getTwinIntensity()) < 0.01
  );
}

function currentSimulationStep() {
  if (!activeSimulationMatchesControls()) return null;
  const minute = getTwinMinute();
  return safeList(state.simulation.propagation).reduce((closest, point) => (
    Math.abs(point.minute - minute) < Math.abs(closest.minute - minute) ? point : closest
  ), state.simulation.propagation[0]);
}

function renderTwinSummary() {
  updateTwinControls();
  const el = $("twinSummary");
  if (!el) return;
  const selectedId = $("simulationZone")?.value;
  const selected = safeList(state.twin?.zones).find(z => z.id === selectedId) || safeList(state.twin?.zones)[0] || {};
  const step = currentSimulationStep();
  const simMode = step ? "calculated" : "preview";
  el.innerHTML = `
    <div><span>Source</span><strong>${escapeHtml(selected.name || "Factory")}</strong></div>
    <div><span>Intensity</span><strong>${escapeHtml(getTwinIntensity().toFixed(1))}x</strong></div>
    <div><span>Timeline</span><strong>${escapeHtml(getTwinMinute())} min</strong></div>
    <div><span>Affected</span><strong>${escapeHtml(step ? safeList(step.affected_zones).length : "preview")}</strong></div>
    <div><span>Mode</span><strong>${escapeHtml(simMode)}</strong></div>
    <div><span>Gas Peak</span><strong>${escapeHtml(state.twin?.gas_status?.peak_value ?? 0)}</strong></div>`;
}

function syncSimulationTimeline() {
  const timeline = $("simulationTime");
  if (!timeline || !state.simulation?.propagation?.length) return;
  const maxMinute = Math.max(...state.simulation.propagation.map(point => Number(point.minute || 0)));
  timeline.max = String(maxMinute);
  timeline.value = String(maxMinute);
  updateTwinControls();
}

function startTwinAnimation() {
  if (state.twinAnimation) return;
  const tick = () => {
    if ($("twin")?.classList.contains("active")) {
      drawTwin();
    }
    state.twinAnimation = requestAnimationFrame(tick);
  };
  state.twinAnimation = requestAnimationFrame(tick);
}

function drawTwin() {
  const canvas = $("twinCanvas");
  if (!canvas) return;
  updateTwinControls();
  const ctx = canvas.getContext("2d");
  const nowMs = typeof performance !== "undefined" ? performance.now() : Date.now();
  const pulse = 0.5 + Math.sin(nowMs / 420) * 0.5;
  const intensity = getTwinIntensity();
  const minute = getTwinMinute();
  const zones = state.twin?.zones || [];
  const zoneLayout = Object.fromEntries(zones.map(z => [z.id, z.layout || {}]));
  const selectedZoneId = $("simulationZone")?.value || zones[0]?.id;
  const selectedZone = zones.find(z => z.id === selectedZoneId) || zones[0] || {};
  const activeStep = currentSimulationStep();
  const affectedById = new Map(safeList(activeStep?.affected_zones).map(z => [z.zone_id, z]));

  const zoneCenter = (zoneId) => {
    const layout = zoneLayout[zoneId] || {};
    return {
      x: Number(layout.x || 0) + Number(layout.width || 0) / 2,
      y: Number(layout.y || 0) + Number(layout.height || 0) / 2,
    };
  };

  const fitText = (text, x, y, maxWidth) => {
    let output = String(text ?? "");
    while (output.length > 4 && ctx.measureText(output).width > maxWidth) output = `${output.slice(0, -4)}...`;
    ctx.fillText(output, x, y);
  };

  const pointOnCurve = (start, mid, end, t) => {
    const mt = 1 - t;
    return {
      x: mt * mt * start.x + 2 * mt * t * mid.x + t * t * end.x,
      y: mt * mt * start.y + 2 * mt * t * mid.y + t * t * end.y,
    };
  };

  const previewPlume = () => {
    const layout = zoneLayout[selectedZoneId] || {};
    const source = zoneCenter(selectedZoneId);
    const drift = minute * (3.0 + intensity * 5.0);
    return {
      minute,
      risk: Math.round(Math.min(100, Number(selectedZone?.risk_score || 50) + intensity * 40 + minute * intensity * 0.9)),
      center: { x: (source.x || Number(layout.x || 90) + 80) + drift, y: (source.y || Number(layout.y || 90) + 60) - minute * (0.4 + intensity) },
      radius: Math.round(34 + minute * (3.4 + intensity * 3.6) + pulse * 12),
      affected_zones: [],
      preview: true,
    };
  };

  const plume = activeStep || previewPlume();

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#f4f7fb";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#dde5ef";
  ctx.lineWidth = 1;
  for (let x = 40; x < canvas.width; x += 40) {
    ctx.beginPath();
    ctx.moveTo(x, 70);
    ctx.lineTo(x, canvas.height - 46);
    ctx.stroke();
  }
  for (let y = 80; y < canvas.height - 40; y += 40) {
    ctx.beginPath();
    ctx.moveTo(30, y);
    ctx.lineTo(canvas.width - 30, y);
    ctx.stroke();
  }

  ctx.fillStyle = "#1d2939";
  ctx.font = "700 17px system-ui";
  fitText(state.twin?.plant?.name || "Apex Unit-01 Factory Twin", 34, 34, 640);
  ctx.font = "12px system-ui";
  ctx.fillStyle = "#667085";
  const gas = state.twin?.gas_status || {};
  fitText(`Intensity ${intensity.toFixed(1)}x · Time ${minute} min · Gas avg ${gas.average_value ?? 0} · Peak ${gas.peak_value ?? 0} · Critical assets ${state.twin?.asset_health_summary?.critical ?? 0}`, 34, 54, 760);

  const drawArrow = (route, dashed = false, index = 0) => {
    const from = zoneLayout[route.from] || {};
    const to = zoneLayout[route.to] || {};
    if (!from.x || !to.x) return;
    const start = zoneCenter(route.from);
    const end = zoneCenter(route.to);
    const mid = { x: (start.x + end.x) / 2, y: (start.y + end.y) / 2 - 18 - (index % 3) * 8 };
    const color = route.status === "critical" ? "#b42318" : route.status === "watch" || route.status === "monitor" ? "#a15c00" : "#8091a7";
    ctx.save();
    ctx.setLineDash(dashed ? [8, 6] : []);
    ctx.strokeStyle = color;
    ctx.lineWidth = route.status === "critical" ? 3 : 2;
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.quadraticCurveTo(mid.x, mid.y, end.x, end.y);
    ctx.stroke();
    const angle = Math.atan2(end.y - mid.y, end.x - mid.x);
    ctx.beginPath();
    ctx.moveTo(end.x, end.y);
    ctx.lineTo(end.x - 11 * Math.cos(angle - 0.5), end.y - 11 * Math.sin(angle - 0.5));
    ctx.lineTo(end.x - 11 * Math.cos(angle + 0.5), end.y - 11 * Math.sin(angle + 0.5));
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
    if (!dashed) {
      const t = ((nowMs / 2200) + index * 0.17) % 1;
      const marker = pointOnCurve(start, mid, end, t);
      ctx.fillStyle = route.status === "watch" || route.status === "monitor" ? "#f79009" : "#1f5eff";
      ctx.beginPath();
      ctx.arc(marker.x, marker.y, 4 + pulse * 1.5, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  };

  (state.twin?.routes || []).forEach((route, index) => drawArrow(route, false, index));
  (state.twin?.emergency_routes || []).forEach((route, index) => drawArrow({ ...route, status: "critical" }, true, index));

  zones.forEach((z) => {
    const layout = z.layout || {};
    const x = Number(layout.x || 80);
    const y = Number(layout.y || 80);
    const w = Number(layout.width || 170);
    const h = Number(layout.height || 120);
    ctx.fillStyle = "rgba(15, 23, 42, 0.06)";
    ctx.beginPath();
    ctx.roundRect(x + 5, y + 6, w, h, 8);
    ctx.fill();
  });

  zones.forEach((z, i) => {
    const layout = z.layout || {};
    const x = Number(layout.x || (80 + (i % 4) * 210));
    const y = Number(layout.y || (70 + Math.floor(i / 4) * 190));
    const w = Number(layout.width || 170);
    const h = Number(layout.height || 120);
    const risk = Number(z.risk_score || 0);
    const affected = affectedById.get(z.id);
    const selected = z.id === selectedZoneId;
    const riskColor = risk >= 80 ? "#b42318" : risk >= 55 ? "#a15c00" : "#187044";
    ctx.fillStyle = affected ? "rgba(255, 241, 240, 0.96)" : risk >= 80 ? "#fff1f0" : risk >= 55 ? "#fff8e6" : "#eefaf4";
    ctx.strokeStyle = selected ? "#1f5eff" : affected ? "#b42318" : riskColor;
    ctx.lineWidth = selected || affected ? 3 : 2;
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, 8);
    ctx.fill();
    ctx.stroke();
    if (selected) {
      ctx.strokeStyle = `rgba(31, 94, 255, ${0.25 + pulse * 0.45})`;
      ctx.lineWidth = 8;
      ctx.stroke();
    }
    ctx.fillStyle = riskColor;
    ctx.fillRect(x, y, 7, h);
    ctx.fillStyle = "#17202a";
    ctx.font = "700 14px system-ui";
    fitText(z.name, x + 12, y + 27, w - 24);
    ctx.font = "12px system-ui";
    ctx.fillStyle = "#475467";
    fitText(`${z.zone_type} · Risk ${formatNumber(risk)}`, x + 12, y + 48, w - 24);
    if (affected) {
      ctx.fillStyle = "#b42318";
      fitText(`Plume risk ${formatNumber(affected.risk)}`, x + 12, y + 66, w - 24);
    }
    ctx.fillStyle = riskColor;
    ctx.fillRect(x + 12, y + h - 22, Math.max(10, (w - 24) * Math.min(100, risk) / 100), 8);
    ctx.strokeStyle = "#ffffff";
    ctx.strokeRect(x + 12, y + h - 22, w - 24, 8);
  });

  const assetsByZone = {};
  (state.twin?.equipment || []).slice(0, 100).forEach((eq) => {
    assetsByZone[eq.zone_id] = assetsByZone[eq.zone_id] || [];
    assetsByZone[eq.zone_id].push(eq);
  });
  Object.entries(assetsByZone).forEach(([zoneId, assets]) => {
    const layout = zoneLayout[zoneId] || {};
    assets.slice(0, 18).forEach((eq, localIndex) => {
      const x = Number(layout.x || 80) + 20 + (localIndex % 7) * 26;
      const y = Number(layout.y || 80) + 74 + Math.floor(localIndex / 7) * 22;
      ctx.fillStyle = eq.health_status === "critical" ? "#b42318" : eq.health_status === "watch" ? "#a15c00" : "#1f5eff";
      ctx.beginPath();
      ctx.arc(x, y, eq.health_status === "critical" ? 8 : 6, 0, Math.PI * 2);
      ctx.fill();
      if (eq.health_status === "critical") {
        ctx.strokeStyle = `rgba(180, 35, 24, ${0.25 + pulse * 0.45})`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(x, y, 12 + pulse * 5, 0, Math.PI * 2);
        ctx.stroke();
      }
    });
  });

  if (plume?.center) {
    const radius = Math.max(18, Number(plume.radius || 0));
    const alpha = plume.preview ? 0.12 + intensity * 0.12 : 0.18 + intensity * 0.12;
    const gradient = ctx.createRadialGradient(plume.center.x, plume.center.y, 8, plume.center.x, plume.center.y, radius);
    gradient.addColorStop(0, `rgba(180, 35, 24, ${Math.min(0.42, alpha + 0.12)})`);
    gradient.addColorStop(0.5, `rgba(247, 144, 9, ${alpha})`);
    gradient.addColorStop(1, "rgba(180, 35, 24, 0)");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(plume.center.x, plume.center.y, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = plume.preview ? "rgba(161, 92, 0, 0.62)" : "rgba(180, 35, 24, 0.68)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(plume.center.x, plume.center.y, radius * (0.72 + pulse * 0.08), 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillStyle = plume.preview ? "#a15c00" : "#b42318";
    ctx.font = "700 13px system-ui";
    fitText(`${plume.preview ? "Preview" : "Gas plume"} ${plume.minute} min · risk ${formatNumber(plume.risk)}`, plume.center.x - 78, plume.center.y, 210);
  }

  const source = zoneCenter(selectedZoneId);
  if (source.x && source.y) {
    ctx.strokeStyle = `rgba(31, 94, 255, ${0.35 + pulse * 0.45})`;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(source.x, source.y, 20 + pulse * 8, 0, Math.PI * 2);
    ctx.stroke();
  }

  ctx.fillStyle = "#ffffff";
  ctx.strokeStyle = "#d0d8e3";
  ctx.lineWidth = 1;
  ctx.fillRect(canvas.width - 292, 16, 258, 92);
  ctx.strokeRect(canvas.width - 292, 16, 258, 92);
  ctx.fillStyle = "#17202a";
  ctx.font = "700 12px system-ui";
  ctx.fillText("Factory Twin Legend", canvas.width - 274, 38);
  ctx.font = "12px system-ui";
  ctx.fillStyle = "#1f5eff";
  ctx.beginPath();
  ctx.arc(canvas.width - 274, 58, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#475467";
  ctx.fillText("asset", canvas.width - 262, 62);
  ctx.strokeStyle = "#8091a7";
  ctx.beginPath();
  ctx.moveTo(canvas.width - 218, 58);
  ctx.lineTo(canvas.width - 184, 58);
  ctx.stroke();
  ctx.fillText("flow", canvas.width - 176, 62);
  ctx.strokeStyle = "#b42318";
  ctx.setLineDash([7, 5]);
  ctx.beginPath();
  ctx.moveTo(canvas.width - 136, 58);
  ctx.lineTo(canvas.width - 102, 58);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillText("emergency", canvas.width - 96, 62);
  ctx.fillStyle = "#a15c00";
  ctx.fillRect(canvas.width - 274, 78, 64 * intensity, 8);
  ctx.strokeStyle = "#d0d8e3";
  ctx.strokeRect(canvas.width - 274, 78, 64, 8);
  ctx.fillStyle = "#475467";
  ctx.fillText(`intensity ${intensity.toFixed(1)}x`, canvas.width - 200, 86);
  ctx.fillStyle = "#17202a";
  ctx.font = "12px system-ui";
  ctx.fillText("Live controls redraw source, routes, plume, affected zones, and asset pulses", 34, canvas.height - 22);
}

async function loadRisk() {
  const data = await api("/api/risk/compound");
  $("riskPanel").innerHTML = `<h3>Factory Compound Risk <span class="${scoreClass(data.compound_risk_score)}">${data.compound_risk_score}</span></h3><p>Confidence ${data.confidence}</p><p>${safeList(data.reasoning).join(" · ")}</p><p>${safeList(data.recommended_actions).join(" · ")}</p>`;
  const geo = await api("/api/risk/geospatial");
  renderTable($("geoPanel"), geo.zones, ["id", "name", "zone_type", "hazard_density", "risk_score", "source_dataset"]);
}

async function loadPermits() {
  const data = await api("/api/permits");
  renderTable($("permitTable"), data.permits, ["id", "zone_name", "equipment_name", "permit_type", "status", "risk_score", "controls", "explanation"]);
}

async function loadMaintenance() {
  const data = await api("/api/maintenance");
  renderTable($("maintenanceTable"), data.maintenance, ["id", "zone_name", "equipment_name", "event_type", "priority", "status", "due_at", "health_score", "recommendation"]);
}

async function loadAssets() {
  const data = await api("/api/assets");
  state.assets = data.assets || [];
  renderMiniGrid($("assetSummary"), data.summary || {});
  renderTable($("assetTable"), state.assets, ["id", "zone_name", "name", "health_score", "health_status", "risk_score", "maintenance_priority", "recommended_action", "latest_metric"]);
  populatePermitAssets();
}

async function loadWorkers() {
  const data = await api("/api/workers");
  const profile = data.current_profile || {};
  const roleDef = profile.role_definition || {};
  $("workerProfile").innerHTML = `<strong>${escapeHtml(profile.user?.name || "Current user")}</strong><br>${escapeHtml(roleDef.label || profile.user?.role || "Role")}<br><span class="muted">${escapeHtml(safeList(roleDef.permissions).join(" · "))}</span>${renderList("Matching factory profiles", safeList(profile.matching_worker_profiles).map(w => `${w.role_name}: ${w.risk_profile}`))}`;
  renderTable($("workerTable"), data.workers, ["id", "department_name", "role_name", "risk_profile", "source_dataset"]);
}

async function loadCompliance() {
  const data = await api("/api/compliance");
  renderTable($("complianceTable"), data.records, ["id", "regulation", "subject", "score", "status", "evidence"]);
}

async function loadReports() {
  const data = await api("/api/reports");
  renderTable($("reportTable"), data.reports, ["id", "report_type", "title", "created_at"]);
}

async function loadAgents() {
  const data = await api("/api/agents");
  $("agentSelect").innerHTML = data.agents.map(a => `<option value="${a.id}">${a.name}</option>`).join("");
}

async function loadAdmin() {
  const models = await api("/api/models");
  renderItems($("modelRegistry"), models.models || [], m => `
    <strong>${escapeHtml(niceLabel(m.id))}</strong>
    <small>${escapeHtml(niceLabel(m.type))} · ${statusPill(m.status)} · ${escapeHtml(m.dataset || "dataset unavailable")}</small>
    <div class="metric-row">${metricChips(m.metrics)}</div>`);
  try {
    const users = await api("/api/admin/users");
    state.roles = users.roles || {};
    renderRoleCatalog(users.roles || {});
    renderUserAdmin(users.users || [], users.roles || {});
    $("newUserRole").innerHTML = Object.entries(users.roles || {}).map(([role, def]) => `<option value="${escapeHtml(role)}">${escapeHtml(def.label)}</option>`).join("");
    const audit = await api("/api/admin/audit-logs");
    renderItems($("auditLogs"), audit.audit_logs || [], a => `<strong>${escapeHtml(niceLabel(a.action))}</strong><small>${escapeHtml(a.actor)} · ${escapeHtml(niceLabel(a.entity_type))} · ${escapeHtml(a.created_at)}</small><small>${escapeHtml(summarizeAuditDetails(a.details))}</small>`);
  } catch (err) {
    $("userAdminTable").innerHTML = `<p class="muted">Admin user controls require an administrator account.</p>`;
    $("roleCatalog").innerHTML = "";
    $("auditLogs").innerHTML = `<p class="muted">${escapeHtml(err.message)}</p>`;
  }
  const cv = await api("/api/computer-vision/status");
  renderComputerVision(cv);
}

function renderComputerVision(cv, message = "") {
  const pipeline = cv.pipeline || {};
  const summary = cv.summary || {};
  const cameras = safeList(cv.cameras);
  const detections = safeList(cv.detections);
  const activeDetections = detections.filter(d => d.severity !== "clear");
  $("cvStatus").innerHTML = `
    ${message ? `<div class="notice">${escapeHtml(message)}</div>` : ""}
    <div class="vision-status-head">
      <div>
        <strong>${escapeHtml(pipeline.model || "factory vision pipeline")}</strong>
        <small>${escapeHtml(niceLabel(pipeline.mode || "demo inference"))} · Last run ${escapeHtml(pipeline.last_run || "not run")}</small>
      </div>
      ${statusPill(cv.enabled ? pipeline.status || "enabled" : "not_enabled")}
    </div>
    <div class="mini-grid vision-summary">
      <div><span>Cameras</span><strong>${escapeHtml(summary.connected_cameras ?? cameras.length)}</strong></div>
      <div><span>Coverage</span><strong>${escapeHtml(summary.coverage_percent ?? 0)}%</strong></div>
      <div><span>Active</span><strong>${escapeHtml(summary.active_detections ?? activeDetections.length)}</strong></div>
      <div><span>Critical</span><strong>${escapeHtml(summary.critical_detections ?? 0)}</strong></div>
      <div><span>FPS</span><strong>${escapeHtml(pipeline.frame_rate_fps ?? 0)}</strong></div>
    </div>
    <div class="vision-grid">
      <section>
        <h3>Camera Coverage</h3>
        <div class="data-list compact">${cameras.map(camera => `
          <div class="item">
            <strong>${escapeHtml(camera.name)}</strong>
            <small>${escapeHtml(camera.zone_name)} · ${statusPill(camera.stream_status)} · ${escapeHtml(camera.coverage_percent)}% coverage · ${escapeHtml(camera.latency_ms)} ms</small>
            <div class="module-tags">${safeList(camera.tasks).map(task => `<span>${escapeHtml(task)}</span>`).join("")}</div>
          </div>`).join("") || "<p class='muted'>No cameras mapped</p>"}</div>
      </section>
      <section>
        <h3>Latest Detections</h3>
        <div class="data-list compact">${detections.slice(0, 8).map(detection => `
          <div class="item detection-${escapeHtml(detection.severity)}">
            <strong>${escapeHtml(detection.zone_name)} ${statusPill(detection.severity)}</strong>
            <small>${escapeHtml(detection.task)} · Confidence ${escapeHtml(formatNumber(detection.confidence * 100, 1))}% · Risk ${escapeHtml(detection.risk_score)}</small>
            <small>${escapeHtml(detection.label)}${detection.asset ? ` · Asset ${escapeHtml(detection.asset)}` : ""}</small>
            <small>Action: ${escapeHtml(detection.recommended_action)}</small>
          </div>`).join("") || "<p class='muted'>No detections</p>"}</div>
      </section>
    </div>
    ${renderList("Vision Response Actions", safeList(cv.recommended_actions))}
    <span class="muted">${escapeHtml(cv.reason || "")}</span>`;
}

function renderRoleCatalog(roles) {
  const el = $("roleCatalog");
  if (!el) return;
  el.innerHTML = Object.entries(roles).map(([role, def]) => `
    <div class="role-card">
      <strong>${escapeHtml(def.label || niceLabel(role))}</strong>
      <small>${escapeHtml(role)}</small>
      <div class="module-tags">${moduleTags(def.modules)}</div>
      <p>${escapeHtml(safeList(def.permissions).join(" · ") || "No permissions assigned")}</p>
    </div>`).join("");
}

function renderUserAdmin(users, roles) {
  const roleOptions = (selected) => Object.entries(roles).map(([role, def]) => `<option value="${escapeHtml(role)}" ${role === selected ? "selected" : ""}>${escapeHtml(def.label)}</option>`).join("");
  if (!users.length) {
    $("userAdminTable").innerHTML = "<p class='muted'>No users</p>";
    return;
  }
  $("userAdminTable").innerHTML = `<table class="admin-table"><thead><tr><th>User</th><th>Current Access</th><th>Edit Role</th><th>Status</th><th>Password Reset</th><th>Action</th></tr></thead><tbody>${
    users.map(user => `<tr data-user-id="${escapeHtml(user.id)}">
      <td><input data-user-field="name" value="${escapeHtml(user.name)}" /><small>${escapeHtml(user.email)}</small></td>
      <td><span class="role-pill">${escapeHtml(roleLabel(user.role, roles))}</span><div class="module-tags">${moduleTags(user.role_definition?.modules)}</div></td>
      <td><select data-user-field="role">${roleOptions(user.role)}</select></td>
      <td><label class="inline-check"><input data-user-field="active" type="checkbox" ${user.active ? "checked" : ""} /> ${escapeHtml(user.active ? "Active" : "Inactive")}</label></td>
      <td><input data-user-field="password" placeholder="Leave blank" /></td>
      <td><button data-save-user="${escapeHtml(user.id)}" type="button">Save</button></td>
    </tr>`).join("")
  }</tbody></table>`;
}

async function loadAll() {
  await loadPlants();
  await Promise.all([loadMission(), loadOperations(), loadTwin(), loadRisk(), loadPermits(), loadMaintenance(), loadAssets(), loadWorkers(), loadCompliance(), loadReports(), loadAgents(), loadAdmin()]);
}

document.addEventListener("click", async (event) => {
  const tab = event.target.closest("[data-module]");
  if (!tab) return;
  document.querySelectorAll(".topnav button").forEach(b => b.classList.toggle("active", b === tab));
  document.querySelectorAll(".module").forEach(m => m.classList.toggle("active", m.id === tab.dataset.module));
});

$("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("loginError").textContent = "";
  const form = new FormData(event.currentTarget);
  try {
    await login(form.get("email"), form.get("password"));
  } catch (err) {
    $("loginError").textContent = "Login failed";
  }
});

$("refreshMission").addEventListener("click", loadMission);
$("incidentSearch").addEventListener("input", (e) => loadOperations(e.target.value));
$("evaluateRisk").addEventListener("click", loadRisk);
$("permitZone").addEventListener("change", populatePermitAssets);
$("simulationZone").addEventListener("change", () => {
  renderTwinSummary();
  drawTwin();
});
$("simulationIntensity").addEventListener("input", () => {
  renderTwinSummary();
  drawTwin();
});
$("simulationTime").addEventListener("input", () => {
  renderTwinSummary();
  drawTwin();
});
$("runSimulation").addEventListener("click", async () => {
  try {
    const intensity = Number($("simulationIntensity").value || 0.8);
    const data = await api("/api/simulations/run", {
      method: "POST",
      body: JSON.stringify({
        scenario: "gas_leak",
        zone_id: $("simulationZone").value || "zone_tank_farm",
        intensity,
      }),
    });
    data.intensity = data.intensity ?? intensity;
    state.simulation = data;
    syncSimulationTimeline();
    renderTwinSummary();
    drawTwin();
    $("simulationOutput").innerHTML = `Simulation ${escapeHtml(data.simulation_id)}
Source: ${escapeHtml(data.source_zone?.name)}
Intensity: ${escapeHtml(formatNumber(data.intensity))}x
Wind: ${escapeHtml(data.wind?.direction)} · ${escapeHtml(data.wind?.speed_mps)} m/s
Status: ${escapeHtml(data.status)}

Affected zones:
${safeList(data.affected_zones).map(z => `- ${escapeHtml(z.zone_name)}: peak ${escapeHtml(z.peak_risk)}, ETA ${escapeHtml(z.eta_minutes)} min`).join("\n") || "- none"}

Response:
${safeList(data.response).map(a => `- ${escapeHtml(a)}`).join("\n")}`;
  } catch (err) {
    showResult($("simulationOutput"), `Simulation failed: ${err.message}`);
  }
});
$("permitForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const body = {
    permit_type: form.get("permit_type"),
    zone_id: form.get("zone_id"),
    equipment_id: form.get("equipment_id") || null,
    work_description: form.get("work_description"),
    gas_test_value: Number(form.get("gas_test_value")),
    simultaneous_work: form.get("simultaneous_work") === "on",
    controls: String(form.get("controls")).split(",").map(s => s.trim()).filter(Boolean),
  };
  try {
    const data = await api("/api/permits/review", { method: "POST", body: JSON.stringify(body) });
    $("permitResult").innerHTML = `<strong>Permit ${escapeHtml(data.status_label || data.status)}</strong><br>
Zone: ${escapeHtml(data.zone || "Selected zone")}<br>
Asset: ${escapeHtml(data.equipment || "No specific asset")}<br>
Risk: <span class="${scoreClass(data.risk_score)}">${escapeHtml(data.risk_score)}</span><br>
Reviewer role: ${escapeHtml(data.reviewer_role)}<br>
${renderList("Missing controls", data.missing_controls)}
${renderList("Required controls", data.required_controls)}
${renderList("Recommended actions", data.recommended_actions)}
Evidence: ${safeList(data.evidence).map(e => escapeHtml(e.title)).join(" · ")}`;
    await Promise.all([loadPermits(), loadRisk(), loadMission(), loadTwin()]);
  } catch (err) {
    showResult($("permitResult"), `Permit review failed: ${err.message}`);
  }
});
$("askCompliance").addEventListener("click", async () => {
  const query = $("regulationQuestion").value || "lockout tagout process safety permit severe injury reporting";
  try {
    const data = await api("/api/knowledge/query", { method: "POST", body: JSON.stringify({ query, limit: 4 }) });
    $("knowledgeAnswer").innerHTML = `<strong>Answer</strong><br>${escapeHtml(data.answer)}${renderList("Required controls", data.required_controls)}${renderList("Next steps", data.next_steps)}<br><strong>Evidence</strong><br>${safeList(data.evidence).map(e => `${escapeHtml(e.title)} (${escapeHtml(e.source)})`).join("<br>")}`;
  } catch (err) {
    showResult($("knowledgeAnswer"), `Regulation query failed: ${err.message}`);
  }
});
$("generateReport").addEventListener("click", async () => {
  try {
    const data = await api("/api/reports/generate", { method: "POST", body: JSON.stringify({ report_type: "executive" }) });
    const token = encodeURIComponent(state.token);
    $("reportOutput").innerHTML = `<strong>Created ${escapeHtml(data.title)}</strong><br>
Plant: ${escapeHtml(data.summary?.plant)}<br>
Average risk: ${escapeHtml(data.summary?.overall_risk)} · Max risk: ${escapeHtml(data.summary?.max_risk)} · Open permits: ${escapeHtml(data.summary?.open_permits)}<br>
Focus: ${escapeHtml(data.summary?.recommended_focus)}<br>
<a href="${data.pdf}?access_token=${token}" target="_blank">Download PDF</a> · <a href="${data.xlsx}?access_token=${token}" target="_blank">Download Excel</a>`;
    await loadReports();
  } catch (err) {
    showResult($("reportOutput"), `Report generation failed: ${err.message}`);
  }
});
$("agentForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  try {
    const data = await api(`/api/agents/${form.get("agent_id")}/run`, { method: "POST", body: JSON.stringify({ goal: form.get("goal"), context: { zone_id: $("simulationZone").value || state.zones[0]?.id } }) });
    $("agentOutput").innerHTML = `${escapeHtml(data.summary)}

Primary action: ${escapeHtml(data.display?.primary_action)}
Status: ${escapeHtml(data.display?.status)}

Next actions:
${safeList(data.outputs?.next_actions).map(a => `- ${escapeHtml(a)}`).join("\n")}

Reasoning:
${safeList(data.reasoning).map(r => `- ${escapeHtml(r)}`).join("\n")}

Evidence:
${safeList(data.outputs?.evidence).map(e => `- ${escapeHtml(e.title)}`).join("\n")}`;
  } catch (err) {
    showResult($("agentOutput"), `Agent failed: ${err.message}`);
  }
});

$("factoryUploadForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = $("factoryDatasetFile").files[0];
  if (!file) {
    showResult($("uploadResult"), "Choose a CSV file first.");
    return;
  }
  try {
    const csvText = await file.text();
    const form = new FormData(event.currentTarget);
    const data = await api("/api/factory/upload-dataset", {
      method: "POST",
      body: JSON.stringify({
        filename: file.name,
        csv_text: csvText,
        replace_uploaded: form.get("replace_uploaded") === "on",
      }),
    });
    $("uploadResult").innerHTML = `<strong>Processed ${data.rows_processed} rows from ${escapeHtml(data.filename)}</strong><br>Factory: ${escapeHtml(data.factory?.name || "Current factory")}<br>Complete factory upload: ${escapeHtml(data.factory?.complete_factory_upload ? "yes" : "no")}<br>Zones created: ${escapeHtml(data.inserted?.zones ?? 0)} · Assets: ${escapeHtml(data.inserted?.equipment ?? 0)} · Risks: ${escapeHtml(data.inserted?.risk_events ?? 0)}<br>Average uploaded risk: ${escapeHtml(data.risk_summary.average_uploaded_risk)}<br>Max uploaded risk: ${escapeHtml(data.risk_summary.max_uploaded_risk)}<br>Detected columns: ${Object.entries(data.columns_detected).map(([k, v]) => `${escapeHtml(k)}=${escapeHtml(v || "not found")}`).join(" · ")}`;
    await loadAll();
  } catch (err) {
    showResult($("uploadResult"), `Upload failed: ${err.message}`);
  }
});

$("loadDemoDataset").addEventListener("click", async () => {
  try {
    const demo = await api("/api/factory/demo-dataset");
    const data = await api("/api/factory/upload-dataset", {
      method: "POST",
      body: JSON.stringify({
        filename: demo.filename,
        csv_text: demo.csv_text,
        replace_uploaded: true,
      }),
    });
    $("uploadResult").innerHTML = `<strong>Loaded demo factory: ${escapeHtml(data.factory?.name)}</strong><br>Rows: ${escapeHtml(data.rows_processed)} · Zones: ${escapeHtml(data.inserted?.zones)} · Assets: ${escapeHtml(data.inserted?.equipment)} · Permits: ${escapeHtml(data.inserted?.permits)} · Risks: ${escapeHtml(data.inserted?.risk_events)}<br>Max uploaded risk: ${escapeHtml(data.risk_summary.max_uploaded_risk)}<br>The whole platform has been refreshed from the demo CSV.`;
    await loadAll();
  } catch (err) {
    showResult($("uploadResult"), `Demo load failed: ${err.message}`);
  }
});

$("downloadDemoDataset").addEventListener("click", async () => {
  try {
    const demo = await api("/api/factory/demo-dataset");
    downloadText(demo.filename, demo.csv_text);
    $("uploadResult").textContent = `Downloaded ${demo.filename}. You can re-upload it with Process Dataset to rebuild the site from that factory.`;
  } catch (err) {
    showResult($("uploadResult"), `Demo download failed: ${err.message}`);
  }
});

$("runCvInspection").addEventListener("click", async () => {
  const button = $("runCvInspection");
  button.disabled = true;
  button.textContent = "Running...";
  try {
    const data = await api("/api/computer-vision/run", { method: "POST" });
    renderComputerVision(data, `Inspection ${data.inspection_id} completed with ${data.summary?.active_detections ?? 0} active detections.`);
    await loadMission();
    try {
      const audit = await api("/api/admin/audit-logs");
      renderItems($("auditLogs"), audit.audit_logs || [], a => `<strong>${escapeHtml(niceLabel(a.action))}</strong><small>${escapeHtml(a.actor)} · ${escapeHtml(niceLabel(a.entity_type))} · ${escapeHtml(a.created_at)}</small><small>${escapeHtml(summarizeAuditDetails(a.details))}</small>`);
    } catch {}
  } catch (err) {
    showResult($("cvStatus"), `Vision audit failed: ${err.message}`);
  } finally {
    button.disabled = false;
    button.textContent = "Run Vision Audit";
  }
});

$("analyzeCctvBtn").addEventListener("click", async () => {

  const fileInput = $("cctvFileInput");
  const zoneSelect = $("cctvZoneSelect");
  const outputDiv = $("cctvAnalysisResult");
  const btn = $("analyzeCctvBtn");

  if (!fileInput.files || !fileInput.files[0]) {
    alert("Please select a CCTV image frame or screenshot first.");
    return;
  }

  const file = fileInput.files[0];
  btn.disabled = true;
  btn.textContent = "Analyzing Frame...";
  outputDiv.style.display = "block";
  outputDiv.innerHTML = "<p>Processing image with pretrained YOLO model & CCTV incident engine...</p>";

  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const base64Data = e.target.result;
      const zoneId = zoneSelect.value;
      const zoneName = zoneSelect.options[zoneSelect.selectedIndex].text;

      const res = await api("/api/computer-vision/analyze-file", {
        method: "POST",
        body: JSON.stringify({
          image_base64: base64Data,
          camera_id: "cctv_upload_user",
          camera_name: "CCTV Studio Feed",
          zone_id: zoneId,
          zone_name: zoneName,
          zone_type: zoneId.includes("tank") ? "hazard_storage" : zoneId.includes("reactor") ? "production" : "logistics"
        })
      });

      const summary = res.summary || {};
      const primary = res.primary_incident || {};
      const severity = summary.overall_severity || "clear";

      outputDiv.innerHTML = `
        <div class="cctv-preview-container">
          <div style="display:flex; justify-content:space-between; width:100%; align-items:center;">
            <strong>CCTV Frame Analysis Result: <span class="cctv-incident-badge badge-${escapeHtml(severity)}">${escapeHtml(severity.toUpperCase())}</span></strong>
            <small>Detector: ${escapeHtml(res.engine_info?.detector || "YOLOv8")} · Latency: ${escapeHtml(res.latency_ms)} ms</small>
          </div>
          <img class="cctv-preview-img" src="${res.snapshot_base64 || res.snapshot_url}" alt="Annotated CCTV Incident Frame" />
          <div style="width:100%; text-align:left;">
            <h4>Detected Incident: ${escapeHtml(primary.label || "No critical incident")}</h4>
            <p><strong>Recommendation:</strong> ${escapeHtml(primary.recommendation || "Maintain standard safety surveillance.")}</p>
            <div class="mini-grid vision-summary">
              <div><span>Persons</span><strong>${escapeHtml(summary.total_persons_detected ?? 0)}</strong></div>
              <div><span>Vehicles</span><strong>${escapeHtml(summary.total_vehicles_detected ?? 0)}</strong></div>
              <div><span>Risk Score</span><strong>${escapeHtml(summary.risk_score ?? 15)} / 100</strong></div>
              <div><span>Incidents</span><strong>${escapeHtml(summary.active_incidents_count ?? 0)}</strong></div>
            </div>
          </div>
        </div>
      `;
    } catch (err) {
      outputDiv.innerHTML = `<p class="error">CCTV Analysis failed: ${escapeHtml(err.message)}</p>`;
    } finally {
      btn.disabled = false;
      btn.textContent = "🔍 Analyze CCTV Frame";
    }
  };
  reader.readAsDataURL(file);
});


$("adminUserForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  try {
    const data = await api("/api/admin/users", {
      method: "POST",
      body: JSON.stringify({
        name: form.get("name"),
        email: form.get("email"),
        role: form.get("role"),
        password: form.get("password") || "SafetyDemo!2026",
        active: true,
      }),
    });
    $("adminUserResult").textContent = `Created ${data.user.name} as ${data.user.role_definition.label}`;
    await loadAdmin();
  } catch (err) {
    showResult($("adminUserResult"), `Create user failed: ${err.message}`);
  }
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-save-user]");
  if (!button) return;
  const row = button.closest("tr");
  const userId = button.dataset.saveUser;
  const name = row.querySelector('[data-user-field="name"]').value;
  const role = row.querySelector('[data-user-field="role"]').value;
  const active = row.querySelector('[data-user-field="active"]').checked;
  const password = row.querySelector('[data-user-field="password"]').value;
  const body = { name, role, active };
  if (password) body.password = password;
  try {
    const data = await api(`/api/admin/users/${encodeURIComponent(userId)}`, { method: "PATCH", body: JSON.stringify(body) });
    $("adminUserResult").textContent = `Saved ${data.user.name} as ${data.user.role_definition.label}`;
    await loadAdmin();
  } catch (err) {
    showResult($("adminUserResult"), `Save user failed: ${err.message}`);
  }
});

if (state.token) {
  showApp();
  api("/api/auth/me").then(user => {
    state.user = user;
    $("userLabel").textContent = `${user.name} · ${user.role}`;
    loadAll();
  }).catch(showLogin);
} else {
  showLogin();
}
