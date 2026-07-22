# AI Documentation

## Trained Models

Run:

```bash
python3 ai/training/train_models.py
```

Current models:

- `equipment_failure_ai4i_v1`
- `cmapss_rul_v1`
- `secom_quality_failure_v1`
- `incident_high_severity_v1`
- `gas_exposure_anomaly_v1`
- `osha_compliance_review_v1`

Each model writes:

- JSON artifact in `models/trained/`
- Model card in `models/model_cards/`
- Registry entry in `models/model_registry.json`

## RAG

Run:

```bash
python3 rag/build_rag_index.py
```

The local index chunks OSHA regulations, NIST placeholder citation metadata, Phase 1 reports, and NASA documentation. Answers include evidence, source, confidence, and references.

## Agents

Agent execution is exposed through `/api/agents/{agent_id}/run`. Agents use bounded tools: risk engine, local RAG, audit log, digital twin, model registry, and simulation.

