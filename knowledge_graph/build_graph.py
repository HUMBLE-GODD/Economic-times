#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "knowledge_graph" / "graph.json"


def node(node_id: str, label: str, typ: str, **props) -> dict:
    return {"id": node_id, "label": label, "type": typ, "properties": props}


def edge(source: str, target: str, relation: str, weight: float = 1.0, **props) -> dict:
    return {"id": f"{source}->{relation}->{target}", "source_id": source, "target_id": target, "relation": relation, "weight": weight, "properties": props}


def main() -> int:
    incidents = pd.read_csv(ROOT / "datasets/engineered/incidents/incident_intelligence.csv", nrows=1500, low_memory=False)
    equipment = pd.read_csv(ROOT / "datasets/engineered/predictive_maintenance/equipment_health_features.csv", nrows=250, low_memory=False)
    compliance = pd.read_csv(ROOT / "datasets/engineered/incidents/establishment_risk_features.csv", nrows=500, low_memory=False)
    nodes = {}
    edges = {}

    def add_node(n: dict) -> None:
        nodes[n["id"]] = n

    def add_edge(e: dict) -> None:
        edges[e["id"]] = e

    add_node(node("org_public_safety", "Public Industrial Safety Dataset Twin", "Organization"))
    add_node(node("plant_dataset_twin", "Dataset-Derived Industrial Safety Twin", "Plant"))
    add_edge(edge("org_public_safety", "plant_dataset_twin", "owns"))

    for state, count in incidents["state"].fillna("UNKNOWN").value_counts().head(12).items():
        zid = f"zone:{state}"
        add_node(node(zid, f"{state} incident zone", "Zone", incident_count=int(count)))
        add_edge(edge("plant_dataset_twin", zid, "contains", float(count)))

    for _, r in incidents.head(500).iterrows():
        iid = f"incident:{r['id']}"
        state = str(r.get("state") or "UNKNOWN")
        event = f"hazard:{str(r.get('eventtitle') or 'Unclassified')[:90]}"
        add_node(node(iid, f"Incident {r['id']}", "Incident", severity=float(r.get("injury_severity_score") or 0), narrative=str(r.get("final_narrative") or "")[:400]))
        add_node(node(event, str(r.get("eventtitle") or "Unclassified"), "Hazard"))
        add_edge(edge(iid, f"zone:{state}", "occurred_in"))
        add_edge(edge(iid, event, "involved"))

    for _, r in equipment.iterrows():
        eid = f"equipment:{int(r['udi'])}"
        add_node(node(eid, str(r["product_id"]), "Equipment", health_score=float(r.get("equipment_health_score") or 0), priority=str(r.get("maintenance_priority"))))
        add_edge(edge("plant_dataset_twin", eid, "operates"))
        if str(r.get("maintenance_priority")) == "high":
            add_edge(edge(eid, "hazard:equipment failure", "at_risk_for", 2.0))

    for _, r in compliance.head(200).iterrows():
        cid = f"compliance:{int(r['id']) if pd.notna(r.get('id')) else len(nodes)}"
        add_node(node(cid, str(r.get("establishment_name") or "Establishment"), "ComplianceRecord", score=float(r.get("inspection_compliance_score") or 0), dart=float(r.get("dart_rate") or 0)))
        add_edge(edge(cid, "regulation:OSHA ITA", "measured_against"))

    add_node(node("regulation:OSHA ITA", "OSHA Injury Tracking Application", "Regulation"))
    add_node(node("regulation:OSHA 1910.147", "OSHA Lockout/Tagout", "Regulation"))
    add_node(node("regulation:NIST SP 800-82r3", "NIST OT Security", "Guidance"))
    add_edge(edge("regulation:OSHA 1910.147", "hazard:equipment failure", "mitigates"))
    add_edge(edge("regulation:NIST SP 800-82r3", "plant_dataset_twin", "supports"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"created_at": datetime.now(timezone.utc).isoformat(), "nodes": list(nodes.values()), "edges": list(edges.values())}, indent=2))
    print(f"graph nodes={len(nodes)} edges={len(edges)} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

