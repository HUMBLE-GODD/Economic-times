# Phase 1 Research And Planning

This document covers the required pre-implementation planning for a greenfield Industrial Safety Intelligence Platform.

## 1. Problem Analysis

Industrial safety risk is rarely caused by a single isolated signal. Serious incidents often emerge from overlapping conditions: degraded equipment, unsafe work permits, abnormal gas readings, worker density, missing isolation, production pressure, and weak compliance controls.

The platform should detect and explain these overlapping risks before they become incidents. It should also help after an incident by connecting narratives, assets, locations, regulations, and response procedures.

Core problems:

- Compound Risk Detection: identify multi-factor risk combinations across equipment, people, permits, environment, and time.
- Geospatial Safety Intelligence: map incidents, hazard density, facility zones, and emergency constraints.
- Incident Pattern Intelligence: cluster incident narratives, root causes, job roles, sources, injuries, and NAICS patterns.
- Digital Permit Intelligence: validate hot work, confined space, electrical isolation, LOTO, and simultaneous operations.
- Emergency Response Orchestration: recommend response steps using live context, maps, assets, and procedures.
- Quality & Compliance Auditing: track OSHA/industry compliance, inspection gaps, DART/TCR rates, and SOP adherence.

## 2. Industrial Workflow Analysis

Current safety workflows are usually split across EHS systems, maintenance systems, SCADA/historians, permit-to-work tools, spreadsheets, inspections, and paper SOPs.

Common workflow:

1. Operations detects abnormal condition or schedules work.
2. Maintenance raises work order and permit.
3. EHS reviews hazards, isolations, gas tests, PPE, and approvals.
4. Work is executed with toolbox talks and field supervision.
5. Incidents/near misses are reported separately.
6. Compliance teams audit forms, training, inspections, and rates.

Gaps where AI can help:

- Linking signals that live in separate systems.
- Detecting unsafe simultaneous operations.
- Ranking assets/zones by dynamic risk.
- Turning incident narratives into structured taxonomies.
- Retrieving exact regulatory/SOP clauses for permit and audit decisions.
- Explaining why a risk score changed.

## 3. Dataset Survey

See `reports/dataset_survey.md`.

Phase 1 selected OSHA, NASA, NIST, and UCI sources. The strongest real safety datasets are OSHA Severe Injury Reports and OSHA ITA. The strongest predictive maintenance benchmark is NASA C-MAPSS. UCI datasets fill prototype gaps for gas sensors, process quality, and synthetic failure modes.

## 4. Dataset Selection Report

See `reports/dataset_selection_report.md`.

Accepted datasets were chosen for source credibility, relevance, data quality, and repeatable acquisition. UCI Hydraulic Systems is currently held because the downloaded archive is incomplete.

## 5. Dataset Quality Report

See `reports/dataset_quality_report.md`.

Quality checks include existence, archive validity, row/column counts, duplicate rows, missing-cell percentage, and parse status. Full-pass highlights:

- OSHA ITA case detail: 697,201 rows, 39 columns.
- OSHA ITA summary: 383,283 rows, 32 columns.
- OSHA severe injury: 105,318 rows, 28 columns.
- NASA C-MAPSS engineered output: 265,256 rows.
- Gas sensor drift: 13,910 parsed measurements, 129 columns per batch file.
- Hydraulic archive: failed archive validation and must not be used yet.

## 6. Data Engineering Plan

Pipeline stages:

1. Acquire from vetted URLs in `metadata/datasets.yml`.
2. Validate archives and tabular files.
3. Normalize column names and encodings.
4. Parse dates, units, sensor columns, and missing sentinels.
5. Create processed datasets under `datasets/processed/`.
6. Engineer features under `datasets/engineered/`.
7. Create training/validation/inference splits.
8. Generate knowledge-graph edge extracts and RAG source manifests.

Implemented scripts:

- `scripts/acquire_datasets.py`
- `scripts/data_engineering/validate_datasets.py`
- `scripts/data_engineering/build_processed_datasets.py`

## 7. Feature Engineering Plan

Implemented or planned features:

- Equipment Health Score: AI4I and C-MAPSS stress/RUL proxy.
- Remaining Useful Life: C-MAPSS cycle-level RUL targets.
- Maintenance Priority: high/medium/low from RUL or health score.
- Gas Exposure Index: normalized gas sensor concentration proxy.
- Risk Trend: rolling exposure trend.
- Sensor Drift Batch Index: UCI gas drift batch feature.
- Manufacturing Quality Features: SECOM missing rate, signal mean/std, yield label.
- Injury Severity Score: hospitalization, amputation, and loss-of-eye weighted score.
- Incident Narrative Length: proxy for text feature availability.
- Hazard Density Key: state plus NAICS grouping.
- DART and Total Case Rate: OSHA ITA establishment risk features.
- Inspection Compliance Score: normalized DART-derived score.
- Knowledge Graph Edges: incident-to-state starter graph.

Future features:

- Permit Overlap Index.
- Worker Density and Zone Occupancy.
- Hazard Density by plant zone.
- Failure Propagation Score from asset graph topology.
- Regulatory Violation Score from audit findings.
- Emergency Response Criticality from asset/zone/person dependency graph.

## 8. AI Model Selection Report

Do not train models unnecessarily.

Recommended strategy:

- Incident pattern intelligence: embeddings plus clustering, weak supervision, and LLM-assisted taxonomy extraction.
- Geospatial safety intelligence: spatial aggregation, kernel density, Bayesian risk smoothing, and map-based analytics.
- Predictive maintenance: start with XGBoost/LightGBM/Random Forest for tabular AI4I; LSTM/TCN/Transformer only for sequence-heavy C-MAPSS after baselines.
- RUL: survival models, gradient boosting, and temporal deep learning if sequence baselines justify it.
- Gas exposure: anomaly detection, drift-aware classifiers, and threshold/rule hybrids.
- Digital permit intelligence: rule engine plus RAG; LLM only for explanation and document extraction.
- Compliance auditing: deterministic checks first, LLM-assisted evidence retrieval second.
- Computer vision/PPE: use pretrained object detectors and fine-tune only with licensed site imagery.
- Multi-agent AI: use agents for orchestration, not as substitutes for deterministic safety checks.

## 9. Knowledge Graph Plan

Initial node types:

- Incident
- Employer / Establishment
- Asset / Equipment
- Sensor
- Zone
- Worker Role
- Permit
- Hazard
- Regulation
- SOP
- Control
- Emergency Resource

Initial edges:

- incident occurred_in zone/state
- incident involved source/event/nature
- establishment belongs_to NAICS
- asset located_in zone
- sensor monitors asset/zone
- permit authorizes work_on asset/zone
- regulation requires control
- SOP mitigates hazard
- incident similar_to incident

Storage:

- Prototype: relational tables plus CSV edge exports.
- Production: Neo4j, Memgraph, or Postgres plus Apache AGE, depending on stack preference.

## 10. Digital Twin Plan

The digital twin should represent assets, zones, workers, permits, sensors, and emergency routes.

Phase 1 twin scope:

- Logical twin: asset/zone/sensor/permit graph.
- Spatial twin: latitude/longitude for public incident data; plant coordinates for customer data later.
- Temporal twin: incident times, permit windows, maintenance cycles, sensor frequencies.
- Risk twin: dynamic risk score per asset/zone/time window.

Public plant layouts are a data gap. For demos, synthetic layouts may be created only if clearly labeled synthetic and derived from documented assumptions.

## 11. RAG Knowledge Sources

Current RAG sources:

- OSHA 1904.39 severe injury reporting.
- OSHA 1910.147 lockout/tagout.
- OSHA 1910.119 process safety management.
- NIST SP 800-82r3 OT/ICS security.
- OSHA ITA data dictionaries.
- NASA C-MAPSS readme and paper.

Future RAG sources:

- OSHA confined spaces, PPE, hazard communication, walking-working surfaces.
- NFPA standards where licensing allows.
- OISD/DGMS/Factories Act sources for India-specific deployments.
- Company SOPs, maintenance manuals, permit templates, emergency plans.

RAG requirements:

- Preserve source URL, document title, section heading, page number, and extraction timestamp.
- Never answer compliance questions without citations.
- Separate regulations from internal SOPs and model-generated suggestions.

## 12. Multi-Agent Design

Recommended agents:

- Safety Risk Agent: combines incident, asset, sensor, permit, and zone context.
- Permit Intelligence Agent: checks permit completeness, conflicts, and required controls.
- Incident Intelligence Agent: classifies narratives, similar cases, and root-cause themes.
- Maintenance Agent: evaluates asset health, RUL, and work-order priority.
- Compliance Agent: retrieves regulatory/SOP evidence and creates audit findings.
- Emergency Agent: composes response recommendations from scenario, location, and resources.
- Data Steward Agent: monitors dataset quality, lineage, and schema drift.

Guardrail: deterministic rules and source-grounded retrieval must override free-form agent suggestions for safety-critical decisions.

## 13. Database Design

Recommended storage:

- Object storage: raw files and source documents.
- Postgres: normalized operational entities, incidents, permits, users, audits.
- TimescaleDB or a time-series store: telemetry and SCADA-like measurements.
- Vector database: regulation, SOP, manual, and incident narrative chunks.
- Graph database: incident/asset/permit/regulation relationships.

Core tables:

- datasets, dataset_files, validation_results
- incidents, incident_taxonomy, incident_locations
- establishments, naics_codes
- assets, sensors, zones
- permits, permit_controls, isolations
- work_orders, maintenance_events
- regulations, rag_chunks, citations
- risk_scores, alerts, audit_findings

## 14. Backend Architecture

Backend modules:

- Ingestion service: dataset/API/file ingestion.
- Validation service: schema, quality, and lineage checks.
- Feature service: reusable feature definitions.
- Risk service: scoring and explanation.
- RAG service: citation-grounded retrieval.
- Agent orchestration service: task routing and tool calls.
- API gateway: auth, rate limits, tenancy.
- Audit service: immutable safety-relevant decisions and evidence.

Preferred stack:

- Python/FastAPI for data and AI services.
- Postgres/TimescaleDB for structured and telemetry data.
- Background jobs with Celery, Dramatiq, or Temporal.
- Object storage compatible with S3.

## 15. Frontend Architecture

The product should feel like an operations console, not a marketing page.

Primary views:

- Safety command center.
- Plant/zone risk map.
- Incident intelligence explorer.
- Permit review workspace.
- Asset health and maintenance priority board.
- Compliance audit workspace.
- Emergency response panel.
- Data quality and lineage dashboard.

Design priorities:

- Dense, scannable, low-drama UI.
- Explainable risk scores with source evidence.
- Filters by date, site, zone, NAICS, asset, permit, event type, and severity.
- Clear separation between observed facts, model predictions, and AI recommendations.

## 16. API Design

Representative endpoints:

- `POST /datasets/acquire`
- `POST /datasets/validate`
- `GET /datasets/{id}/quality`
- `GET /incidents/search`
- `GET /incidents/patterns`
- `GET /risk/zones`
- `GET /risk/assets/{asset_id}`
- `POST /permits/review`
- `POST /rag/query`
- `POST /agents/safety-risk`
- `GET /audits/findings`
- `POST /emergency/plan`

API responses should include trace IDs, source references, model version, feature version, and confidence/explanation fields.

## 17. Deployment Strategy

Phase 1:

- Local data repository and scripts.
- Batch processing with CSV outputs.
- Manual source/license review.

Phase 2:

- Containerized ingestion and feature services.
- Managed Postgres, object storage, and vector DB.
- Scheduled validation and dataset refresh.

Phase 3:

- Site-specific deployment with tenant isolation.
- Streaming telemetry ingestion.
- Role-based access control and audit logging.
- Observability and incident-response runbooks.

## 18. Security Plan

Safety data is sensitive even when it is not personal data.

Controls:

- RBAC by site, role, and workflow.
- Immutable audit logs for permit/compliance decisions.
- Encrypt data at rest and in transit.
- Redact personal identifiers from incident narratives where required.
- Separate public benchmark data from customer operational data.
- Keep plant layouts, SCADA tags, and emergency routes under stricter access controls.
- Validate all uploaded documents before indexing.
- Use NIST SP 800-82r3 principles for OT/ICS boundary design.

## 19. Testing Strategy

Test layers:

- Dataset acquisition tests: URL reachable, checksum changes detected.
- Validation tests: row counts, schema, missingness, duplicates, archive integrity.
- Processing tests: output schemas, feature ranges, date parsing, split integrity.
- Model tests: leakage checks, baseline comparisons, drift monitoring.
- RAG tests: citation correctness and refusal on missing evidence.
- Agent tests: deterministic rule precedence, tool-call auditability.
- API tests: authorization, input validation, error handling.
- UI tests: critical workflow coverage and accessibility.

## 20. Development Roadmap

Week 1:

- Finish dataset source review and license clearance.
- Reacquire or replace hydraulic telemetry.
- Add RAG chunking for OSHA/NIST PDFs/HTML.

Week 2:

- Build database schema and import processed datasets.
- Implement incident search, establishment risk, and asset health APIs.
- Add baseline models for AI4I, C-MAPSS, SECOM, and gas drift.

Week 3:

- Build safety command center UI.
- Add geospatial incident analytics.
- Add RAG-backed compliance assistant with citations.

Week 4:

- Add permit intelligence schema and rule engine.
- Add multi-agent orchestration.
- Add audit logging and deployment scripts.

Post-hackathon:

- Acquire licensed PPE/video, permit, plant layout, and SCADA data.
- Integrate customer CMMS/EHS/SCADA sources.
- Validate models with domain experts before operational use.

