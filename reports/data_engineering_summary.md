# Data Engineering Summary

## What Was Built

The Phase 1 pipeline now turns raw public sources into processed, engineered, training, validation, inference, and starter knowledge-graph datasets.

Run:

```bash
python3 scripts/data_engineering/validate_datasets.py
python3 scripts/data_engineering/build_processed_datasets.py
```

## Generated Dataset Families

| Output | Purpose |
|---|---|
| `datasets/processed/predictive_maintenance/ai4i_clean.csv` | Normalized AI4I failure table |
| `datasets/engineered/predictive_maintenance/equipment_health_features.csv` | Equipment health and maintenance priority features |
| `datasets/processed/predictive_maintenance/cmapss_clean.csv` | Combined C-MAPSS train/test cycle data |
| `datasets/engineered/predictive_maintenance/cmapss_rul_features.csv` | RUL, cycle progress, health, and priority features |
| `datasets/processed/gas_sensors/air_quality_clean.csv` | Cleaned air-quality time series |
| `datasets/engineered/gas_sensors/gas_exposure_features.csv` | Gas exposure and 24-hour trend features |
| `datasets/processed/gas_sensors/gas_sensor_drift_clean.csv` | Parsed gas drift batches |
| `datasets/engineered/gas_sensors/gas_sensor_drift_features.csv` | Drift-batch and signal summary features |
| `datasets/processed/manufacturing/secom_clean.csv` | Imputed SECOM process/yield table |
| `datasets/engineered/manufacturing/secom_quality_features.csv` | Quality/yield feature table |
| `datasets/processed/incidents/osha_severe_injury_clean.csv` | Cleaned OSHA severe injury records |
| `datasets/engineered/incidents/incident_intelligence.csv` | Incident severity, taxonomy, geospatial, narrative features |
| `datasets/processed/incidents/osha_ita_summary_2025_clean.csv` | Cleaned OSHA ITA establishment summary |
| `datasets/engineered/incidents/establishment_risk_features.csv` | DART/TCR and compliance-score features |
| `datasets/processed/incidents/osha_ita_case_detail_2025_clean.csv` | Cleaned OSHA ITA case detail records |
| `datasets/engineered/incidents/osha_ita_case_text_features.csv` | Case narrative text features |
| `datasets/engineered/knowledge_graph/incident_state_edges.csv` | Starter incident-to-state graph edges |

## Quality Constraints

- Raw datasets are retained unchanged.
- Synthetic datasets are marked as synthetic in metadata.
- UCI commercial usage is not assumed because the API did not expose explicit license fields.
- OSHA ITA and Severe Injury datasets are real public data, but OSHA's own quality caveats must be preserved in product UX.
- The UCI Hydraulic Systems archive failed validation and is excluded from processing.

