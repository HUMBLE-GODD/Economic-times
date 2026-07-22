# Dataset Survey

This survey records public sources reviewed for Phase 1 of the Industrial Safety AI Platform. The selection prioritizes trusted provenance, machine-readability, relevance to industrial safety, and whether the source can support repeatable AI workflows without fabricating data.

## Selected Sources

| Dataset | Source | Domain Fit | Rows / Assets | Use In Platform | Caveat |
|---|---|---|---:|---|---|
| AI4I 2020 Predictive Maintenance | UCI ML Repository | Predictive maintenance, failure modes | 10,000 rows | Equipment health scoring, failure classification prototype | Synthetic; not evidence of plant performance |
| NASA C-MAPSS | NASA Open Data / Prognostics Center | RUL, degradation, time series | 265,256 engineered rows | Remaining useful life and degradation modeling | Simulated turbofan, not factory equipment |
| SECOM | UCI ML Repository | Manufacturing quality and process sensors | 1,567 rows, 590 sensors | Quality/yield anomaly analysis | Missing values and license not declared by UCI API |
| Gas Sensor Array Drift | UCI ML Repository | Gas sensing and drift compensation | 13,910 measurements | Gas-classification and drift-robust exposure models | No spatial/site context |
| Air Quality | UCI ML Repository | Gas/environmental time series | 9,357 cleaned rows | Gas exposure trend features | Uses missing sentinel values and non-US urban context |
| OSHA Severe Injury Reports | OSHA | Real incident narratives and geospatial fields | 105,318 parsed rows | Incident pattern intelligence, geospatial risk, narrative RAG | Federal OSHA only, not fatalities |
| OSHA ITA 2025 Summary / Case Detail | OSHA | Work-related injury/illness establishment and case records | 383,283 summary rows, 697,201 case rows | Establishment risk, DART/TCR, case narrative analytics | OSHA warns unresolved errors may remain |
| OSHA Regulation Pages | OSHA | Compliance rules | 3 HTML sources | RAG, audit checklists, permit rule extraction | Needs HTML section normalization |
| NIST SP 800-82r3 | NIST | OT/ICS security | 1 PDF | SCADA/ICS risk controls and RAG | Needs PDF chunking and citation metadata |

## Sources Held Or Rejected

| Need | Source Type Reviewed | Decision | Reason |
|---|---|---|---|
| Hydraulic condition monitoring | UCI Condition Monitoring of Hydraulic Systems | Hold | Downloaded archive is incomplete/corrupt; reacquire before use |
| PPE / CCTV worker safety | Kaggle, GitHub, generic CV datasets | Gap | Many useful datasets are auth-gated, small, or license-unclear for commercial demos |
| Permit-to-work records | Public government and GitHub searches | Gap | Real permit records are operationally sensitive and rarely public |
| Plant layouts / hazard zones | Open maps, public facility docs | Gap | Detailed plant maps are security-sensitive |
| SCADA attack/process telemetry | SWaT/WADI/Tennessee Eastman family | Gap/Hold | Some are registration-gated or redistribution-restricted; do not store until license is explicit |
| OISD/DGMS/Factories Act sources | Public regulatory portals | Future RAG | Useful for India-specific compliance but requires dedicated legal-source normalization |

## Dataset Coverage Matrix

| Capability | Covered Now | Dataset(s) |
|---|---|---|
| Compound Risk Detection | Partial | OSHA incidents, ITA, AI4I, air quality |
| Geospatial Safety Intelligence | Strong for US incident data | OSHA severe injury latitude/longitude, city/state/NAICS |
| Incident Pattern Intelligence | Strong | OSHA severe injury and ITA case narratives |
| Digital Permit Intelligence | Schema/RAG only | OSHA LOTO, PSM, reporting regulations; no real permit records |
| Emergency Response Orchestration | Partial | Incident locations, hazard categories, NIST OT context |
| Quality & Compliance Auditing | Moderate | SECOM, OSHA ITA rates, OSHA/NIST sources |
| Predictive Maintenance | Strong for prototypes | AI4I, NASA C-MAPSS; hydraulic on hold |
| Gas/Exposure Monitoring | Moderate | Gas sensor drift, air quality |
| PPE Detection | Gap | Needs licensed image/video source or site data |

## Source Links

- UCI AI4I: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset
- NASA C-MAPSS: https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data
- UCI SECOM: https://archive.ics.uci.edu/dataset/179/secom
- UCI Gas Sensor Drift: https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset
- UCI Air Quality: https://archive.ics.uci.edu/dataset/360/air+quality
- OSHA Severe Injury Reports: https://www.osha.gov/severe-injury-reports
- OSHA ITA Data: https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data
- OSHA Regulations: https://www.osha.gov/laws-regs/regulations
- NIST SP 800-82r3: https://csrc.nist.gov/publications/detail/sp/800-82/rev-3/final

