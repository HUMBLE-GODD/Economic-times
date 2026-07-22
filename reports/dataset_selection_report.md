# Dataset Selection Report

## Selection Criteria

Datasets were selected when they met most of these criteria:

- Trusted source: government, UCI, NASA, NIST, or comparable primary source.
- Useful for at least one industrial safety workflow.
- Downloadable without fabricating data or bypassing access controls.
- Machine-readable or useful as RAG source material.
- Quality issues are measurable and correctable.
- License/usage status can be tracked clearly even when commercial use needs manual clearance.

## Accepted For Phase 1 Engineering

| Dataset | Decision | Why It Was Kept |
|---|---|---|
| OSHA Severe Injury Reports | Keep | Real incident records with event taxonomy, narratives, employer/location fields, and latitude/longitude |
| OSHA ITA 2025 | Keep | Real establishment summary and case-detail injury/illness records; supports compliance and risk scoring |
| NASA C-MAPSS | Keep | Canonical public RUL benchmark with train/test/RUL splits |
| UCI AI4I | Keep with synthetic label | Small, clean predictive maintenance benchmark for explainable tabular prototypes |
| UCI SECOM | Keep with imputation | Real manufacturing sensor dataset useful for quality and feature selection |
| UCI Gas Sensor Drift | Keep | Strong fit for gas classification and drift compensation |
| UCI Air Quality | Keep with cleaning | Useful for exposure-index and missing-sensor handling |
| OSHA / NIST Regulatory Sources | Keep | Trusted RAG/audit material for compliance, OT, and incident workflows |

## Held Or Excluded

| Dataset / Need | Decision | Reason |
|---|---|---|
| UCI Hydraulic Systems | Hold | Archive download is incomplete/corrupt in this run |
| PPE detection image sets | Exclude for now | License and commercial-use ambiguity; many sources require Kaggle authentication |
| Real permit-to-work data | Gap | Public records are rare and security-sensitive |
| Plant layouts and hazard zones | Gap | Detailed facility maps are rarely public and can expose security-sensitive information |
| SWaT/WADI-style SCADA datasets | Hold | Useful but often request-gated or redistribution-restricted |

## Commercial And Educational Use

Government sources from OSHA, NASA, and NIST are treated as high-credibility public sources, but deployment teams should still review agency terms, privacy implications, and attribution requirements before commercial use.

UCI datasets downloaded through the UCI API did not expose an explicit license field in this run. They are kept for research and educational prototyping with citation, but commercial use should be manually cleared before product demos or customer deployment.

## Production Readiness

Production-ready public datasets in this repository:

- OSHA Severe Injury Reports
- OSHA ITA 2025 Summary and Case Detail
- OSHA regulation pages
- NIST SP 800-82r3

Research/prototype-ready datasets:

- NASA C-MAPSS
- UCI AI4I
- UCI SECOM
- UCI Gas Sensor Drift
- UCI Air Quality

Blocked until reacquisition:

- UCI Hydraulic Systems

