PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS organizations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  source TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plants (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  name TEXT NOT NULL,
  city TEXT,
  state TEXT,
  latitude REAL,
  longitude REAL,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS departments (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  name TEXT NOT NULL,
  function TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS zones (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  name TEXT NOT NULL,
  zone_type TEXT NOT NULL,
  latitude REAL,
  longitude REAL,
  hazard_density REAL DEFAULT 0,
  risk_score REAL DEFAULT 0,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL REFERENCES organizations(id),
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  token_hash TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS equipment (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  zone_id TEXT REFERENCES zones(id),
  name TEXT NOT NULL,
  equipment_type TEXT NOT NULL,
  health_score REAL,
  maintenance_priority TEXT,
  failure_probability REAL DEFAULT 0,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sensors (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  zone_id TEXT REFERENCES zones(id),
  equipment_id TEXT REFERENCES equipment(id),
  name TEXT NOT NULL,
  sensor_type TEXT NOT NULL,
  unit TEXT,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workers (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  department_id TEXT REFERENCES departments(id),
  role_name TEXT NOT NULL,
  risk_profile TEXT NOT NULL,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS telemetry (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sensor_id TEXT NOT NULL REFERENCES sensors(id),
  equipment_id TEXT REFERENCES equipment(id),
  zone_id TEXT REFERENCES zones(id),
  ts TEXT NOT NULL,
  metric TEXT NOT NULL,
  value REAL NOT NULL,
  risk_score REAL DEFAULT 0,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS maintenance_events (
  id TEXT PRIMARY KEY,
  equipment_id TEXT NOT NULL REFERENCES equipment(id),
  event_type TEXT NOT NULL,
  priority TEXT NOT NULL,
  status TEXT NOT NULL,
  due_at TEXT,
  health_score REAL,
  recommendation TEXT,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS permits (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  zone_id TEXT REFERENCES zones(id),
  equipment_id TEXT REFERENCES equipment(id),
  permit_type TEXT NOT NULL,
  status TEXT NOT NULL,
  risk_score REAL NOT NULL,
  controls TEXT NOT NULL,
  explanation TEXT NOT NULL,
  source_dataset TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS incidents (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  zone_id TEXT REFERENCES zones(id),
  event_date TEXT,
  employer TEXT,
  city TEXT,
  state TEXT,
  latitude REAL,
  longitude REAL,
  naics TEXT,
  severity_score REAL,
  event_title TEXT,
  source_title TEXT,
  narrative TEXT,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hazards (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  zone_id TEXT REFERENCES zones(id),
  name TEXT NOT NULL,
  hazard_type TEXT NOT NULL,
  severity REAL NOT NULL,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS risk_events (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  zone_id TEXT REFERENCES zones(id),
  equipment_id TEXT REFERENCES equipment(id),
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  compound_risk_score REAL NOT NULL,
  confidence REAL NOT NULL,
  reasoning TEXT NOT NULL,
  recommended_actions TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS compliance_records (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  regulation TEXT NOT NULL,
  subject TEXT NOT NULL,
  score REAL NOT NULL,
  status TEXT NOT NULL,
  evidence TEXT NOT NULL,
  source_dataset TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  doc_type TEXT NOT NULL,
  source_path TEXT NOT NULL,
  source_url TEXT,
  summary TEXT
);

CREATE TABLE IF NOT EXISTS kg_nodes (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  type TEXT NOT NULL,
  properties TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kg_edges (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  target_id TEXT NOT NULL,
  relation TEXT NOT NULL,
  weight REAL DEFAULT 1,
  properties TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions (
  id TEXT PRIMARY KEY,
  model_id TEXT NOT NULL,
  subject_type TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  prediction REAL NOT NULL,
  confidence REAL NOT NULL,
  explanation TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id TEXT PRIMARY KEY,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT,
  detail TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  severity TEXT NOT NULL,
  channel TEXT NOT NULL,
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS simulations (
  id TEXT PRIMARY KEY,
  plant_id TEXT NOT NULL REFERENCES plants(id),
  scenario TEXT NOT NULL,
  result TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reports_generated (
  id TEXT PRIMARY KEY,
  report_type TEXT NOT NULL,
  title TEXT NOT NULL,
  pdf_path TEXT,
  xlsx_path TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_incidents_state ON incidents(state);
CREATE INDEX IF NOT EXISTS idx_incidents_geo ON incidents(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_risk_events_score ON risk_events(compound_risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry(ts DESC);
CREATE INDEX IF NOT EXISTS idx_equipment_priority ON equipment(maintenance_priority);
CREATE INDEX IF NOT EXISTS idx_permits_status ON permits(status);
CREATE INDEX IF NOT EXISTS idx_compliance_status ON compliance_records(status);
CREATE INDEX IF NOT EXISTS idx_kg_source ON kg_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_kg_target ON kg_edges(target_id);
