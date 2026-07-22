#!/usr/bin/env python3
"""Clean and engineer first-pass datasets for the Industrial Safety AI platform."""

from __future__ import annotations

import math
import pathlib
import re
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = pathlib.Path(__file__).resolve().parents[2]


def out(path: str) -> pathlib.Path:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def clean_col(name: str) -> str:
    name = re.sub(r"[^0-9a-zA-Z]+", "_", str(name)).strip("_").lower()
    return re.sub(r"_+", "_", name)


def normalize_numeric(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    lo, hi = numeric.quantile(0.01), numeric.quantile(0.99)
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return ((numeric.clip(lo, hi) - lo) / (hi - lo)).fillna(0)


def split_train_validation(df: pd.DataFrame, base_name: str, stratify_col: str | None = None) -> None:
    rng = np.random.default_rng(42)
    if stratify_col and stratify_col in df.columns:
        train_parts = []
        valid_parts = []
        for _, part in df.groupby(stratify_col, dropna=False):
            mask = rng.random(len(part)) < 0.8
            train_parts.append(part.loc[mask])
            valid_parts.append(part.loc[~mask])
        train = pd.concat(train_parts).sample(frac=1, random_state=42)
        valid = pd.concat(valid_parts).sample(frac=1, random_state=42)
    else:
        mask = rng.random(len(df)) < 0.8
        train = df.loc[mask]
        valid = df.loc[~mask]
    train.to_csv(out(f"datasets/training/{base_name}_train.csv"), index=False)
    valid.to_csv(out(f"datasets/validation/{base_name}_validation.csv"), index=False)


def build_ai4i() -> None:
    src = ROOT / "datasets/raw/predictive_maintenance/uci_ai4i_2020/ai4i2020.csv"
    if not src.exists():
        return
    df = pd.read_csv(src)
    df.columns = [clean_col(c) for c in df.columns]
    df["air_temperature_c"] = df["air_temperature_k"] - 273.15
    df["process_temperature_c"] = df["process_temperature_k"] - 273.15
    df["temperature_delta_k"] = df["process_temperature_k"] - df["air_temperature_k"]
    df["power_proxy"] = df["torque_nm"] * df["rotational_speed_rpm"] * 2 * math.pi / 60
    df["failure_mode_count"] = df[["twf", "hdf", "pwf", "osf", "rnf"]].sum(axis=1)
    stress = (
        0.30 * normalize_numeric(df["tool_wear_min"])
        + 0.25 * normalize_numeric(df["torque_nm"])
        + 0.25 * normalize_numeric(df["temperature_delta_k"])
        + 0.20 * normalize_numeric(df["power_proxy"])
    )
    df["equipment_health_score"] = (100 - 80 * stress - 20 * df["machine_failure"]).clip(0, 100).round(2)
    df["maintenance_priority"] = pd.cut(
        100 - df["equipment_health_score"],
        bins=[-0.1, 30, 55, 100],
        labels=["low", "medium", "high"],
    ).astype(str)
    df.to_csv(out("datasets/processed/predictive_maintenance/ai4i_clean.csv"), index=False)
    df.to_csv(out("datasets/engineered/predictive_maintenance/equipment_health_features.csv"), index=False)
    split_train_validation(df, "ai4i_failure", "machine_failure")


def cmapss_columns() -> list[str]:
    return (
        ["engine_id", "cycle", "operational_setting_1", "operational_setting_2", "operational_setting_3"]
        + [f"sensor_{i:02d}" for i in range(1, 22)]
    )


def read_cmapss(path: pathlib.Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=r"\s+", header=None, engine="python")
    df = df.dropna(axis=1, how="all")
    df.columns = cmapss_columns()[: len(df.columns)]
    return df


def build_cmapss() -> None:
    folder = ROOT / "datasets/raw/predictive_maintenance/nasa_cmapss"
    if not (folder / "train_FD001.txt").exists():
        return
    processed_parts = []
    engineered_parts = []
    for scenario in ["FD001", "FD002", "FD003", "FD004"]:
        train_path = folder / f"train_{scenario}.txt"
        test_path = folder / f"test_{scenario}.txt"
        rul_path = folder / f"RUL_{scenario}.txt"
        if not train_path.exists() or not test_path.exists() or not rul_path.exists():
            continue

        train = read_cmapss(train_path)
        train["scenario"] = scenario
        train["split"] = "train"
        train["max_cycle"] = train.groupby("engine_id")["cycle"].transform("max")
        train["remaining_useful_life"] = train["max_cycle"] - train["cycle"]

        test = read_cmapss(test_path)
        test["scenario"] = scenario
        test["split"] = "test"
        true_rul = pd.read_csv(rul_path, sep=r"\s+", header=None, names=["true_rul_at_last_cycle"], engine="python")
        true_rul["engine_id"] = np.arange(1, len(true_rul) + 1)
        test = test.merge(true_rul, on="engine_id", how="left")
        test["max_cycle"] = test.groupby("engine_id")["cycle"].transform("max")
        test["remaining_useful_life"] = test["true_rul_at_last_cycle"] + (test["max_cycle"] - test["cycle"])

        combined = pd.concat([train, test], ignore_index=True)
        sensor_cols = [c for c in combined.columns if c.startswith("sensor_")]
        combined["sensor_signal_mean"] = combined[sensor_cols].mean(axis=1)
        combined["sensor_signal_std"] = combined[sensor_cols].std(axis=1)
        combined["cycle_progress"] = combined["cycle"] / combined["max_cycle"].replace(0, np.nan)
        combined["equipment_health_score"] = (100 * (1 - normalize_numeric(combined["cycle_progress"]))).clip(0, 100).round(2)
        combined["maintenance_priority"] = pd.cut(
            combined["remaining_useful_life"],
            bins=[-1, 30, 90, np.inf],
            labels=["high", "medium", "low"],
        ).astype(str)
        processed_parts.append(combined)
        engineered_parts.append(combined)

    if processed_parts:
        all_cmapss = pd.concat(processed_parts, ignore_index=True)
        all_cmapss.to_csv(out("datasets/processed/predictive_maintenance/cmapss_clean.csv"), index=False)
        all_cmapss.to_csv(out("datasets/engineered/predictive_maintenance/cmapss_rul_features.csv"), index=False)
        train = all_cmapss[all_cmapss["split"] == "train"]
        valid_engines = train[["scenario", "engine_id"]].drop_duplicates().sample(frac=0.2, random_state=42)
        valid_keys = set(map(tuple, valid_engines[["scenario", "engine_id"]].to_numpy()))
        mask = train.apply(lambda r: (r["scenario"], r["engine_id"]) in valid_keys, axis=1)
        train.loc[~mask].to_csv(out("datasets/training/cmapss_rul_train.csv"), index=False)
        train.loc[mask].to_csv(out("datasets/validation/cmapss_rul_validation.csv"), index=False)
        all_cmapss[all_cmapss["split"] == "test"].to_csv(out("datasets/inference/cmapss_test_inference.csv"), index=False)


def build_air_quality() -> None:
    src = ROOT / "datasets/raw/gas_sensors/uci_air_quality/AirQualityUCI.csv"
    if not src.exists():
        return
    df = pd.read_csv(src, sep=";", encoding="latin1", low_memory=False)
    df = df.dropna(axis=1, how="all").dropna(how="all")
    df.columns = [clean_col(c) for c in df.columns]
    for col in df.columns:
        if col not in {"date", "time"}:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ".", regex=False), errors="coerce")
            df[col] = df[col].replace(-200, np.nan)
    df["timestamp"] = pd.to_datetime(df["date"] + " " + df["time"].str.replace(".", ":", regex=False), dayfirst=True, errors="coerce")
    gas_cols = [c for c in ["co_gt", "c6h6_gt", "nox_gt", "no2_gt", "pt08_s5_o3"] if c in df.columns]
    df["sensor_missing_count"] = df[gas_cols].isna().sum(axis=1)
    exposure = sum(normalize_numeric(df[c]) for c in gas_cols) / max(len(gas_cols), 1)
    df["gas_exposure_index"] = (100 * exposure).round(2)
    df["risk_trend_24h"] = df["gas_exposure_index"].rolling(24, min_periods=1).mean().round(2)
    df.to_csv(out("datasets/processed/gas_sensors/air_quality_clean.csv"), index=False)
    df.to_csv(out("datasets/engineered/gas_sensors/gas_exposure_features.csv"), index=False)
    split_train_validation(df.dropna(subset=["timestamp"]), "air_quality_exposure")


def parse_gas_drift_line(line: str) -> dict:
    parts = line.strip().split()
    row = {"gas_class": int(parts[0]) if parts else None}
    for item in parts[1:]:
        key, value = item.split(":", 1)
        row[f"sensor_feature_{int(key):03d}"] = float(value)
    return row


def iter_gas_drift_files() -> Iterable[pathlib.Path]:
    folder = ROOT / "datasets/raw/gas_sensors/uci_gas_sensor_drift/Dataset"
    if not folder.exists():
        return []
    return sorted(folder.glob("batch*.dat"), key=lambda p: int(re.search(r"\d+", p.name).group()))


def build_gas_drift() -> None:
    rows = []
    for path in iter_gas_drift_files():
        batch = int(re.search(r"\d+", path.name).group())
        with path.open() as handle:
            for line in handle:
                if line.strip():
                    row = parse_gas_drift_line(line)
                    row["batch"] = batch
                    rows.append(row)
    if not rows:
        return
    df = pd.DataFrame(rows).sort_values(["batch"]).reset_index(drop=True)
    feature_cols = [c for c in df.columns if c.startswith("sensor_feature_")]
    df["sensor_signal_mean"] = df[feature_cols].mean(axis=1)
    df["sensor_signal_std"] = df[feature_cols].std(axis=1)
    df["drift_batch_index"] = df["batch"]
    df.to_csv(out("datasets/processed/gas_sensors/gas_sensor_drift_clean.csv"), index=False)
    df.to_csv(out("datasets/engineered/gas_sensors/gas_sensor_drift_features.csv"), index=False)
    split_train_validation(df, "gas_sensor_drift", "gas_class")


def build_secom() -> None:
    data_path = ROOT / "datasets/raw/manufacturing/uci_secom/secom.data"
    labels_path = ROOT / "datasets/raw/manufacturing/uci_secom/secom_labels.data"
    if not data_path.exists() or not labels_path.exists():
        return
    x = pd.read_csv(data_path, sep=r"\s+", header=None, engine="python")
    labels = pd.read_csv(labels_path, sep=r"\s+", header=None, engine="python", names=["yield_label", "date", "time"])
    x.columns = [f"process_sensor_{i:03d}" for i in range(x.shape[1])]
    df = pd.concat([labels, x], axis=1)
    df["timestamp"] = pd.to_datetime(df["date"] + " " + df["time"], dayfirst=True, errors="coerce")
    df["is_yield_failure"] = (df["yield_label"] == 1).astype(int)
    sensor_cols = [c for c in df.columns if c.startswith("process_sensor_")]
    df["sensor_missing_rate"] = df[sensor_cols].isna().mean(axis=1).round(4)
    df["process_signal_mean"] = df[sensor_cols].mean(axis=1)
    df["process_signal_std"] = df[sensor_cols].std(axis=1)
    imputed = df.copy()
    medians = imputed[sensor_cols].median()
    imputed[sensor_cols] = imputed[sensor_cols].fillna(medians)
    imputed.to_csv(out("datasets/processed/manufacturing/secom_clean.csv"), index=False)
    imputed.to_csv(out("datasets/engineered/manufacturing/secom_quality_features.csv"), index=False)
    split_train_validation(imputed, "secom_yield", "is_yield_failure")


def build_osha_severe() -> None:
    src = ROOT / "datasets/raw/incidents/osha_severe_injury/January2015toOctober2025.csv"
    if not src.exists():
        return
    df = pd.read_csv(src, low_memory=False)
    df.columns = [clean_col(c) for c in df.columns]
    df["event_date"] = pd.to_datetime(df["eventdate"], errors="coerce")
    for col in ["hospitalized", "amputation", "loss_of_eye"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["incident_year"] = df["event_date"].dt.year
    df["incident_month"] = df["event_date"].dt.month
    df["geospatial_valid"] = df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)
    df["injury_severity_score"] = (
        2 * df["hospitalized"] + 4 * df["amputation"] + 5 * df["loss_of_eye"]
    ).clip(0, 10)
    df["narrative_length"] = df.get("final_narrative", pd.Series("", index=df.index)).fillna("").str.len()
    df["hazard_density_key"] = df["state"].fillna("UNK").astype(str) + "_" + df["primary_naics"].fillna("UNK").astype(str)
    df.to_csv(out("datasets/processed/incidents/osha_severe_injury_clean.csv"), index=False)
    incident_cols = [
        "id", "event_date", "employer", "city", "state", "zip", "latitude", "longitude",
        "primary_naics", "hospitalized", "amputation", "loss_of_eye", "injury_severity_score",
        "naturetitle", "part_of_body_title", "eventtitle", "sourcetitle", "final_narrative",
        "geospatial_valid", "hazard_density_key",
    ]
    incident_cols = [c for c in incident_cols if c in df.columns]
    df[incident_cols].to_csv(out("datasets/engineered/incidents/incident_intelligence.csv"), index=False)
    split_train_validation(df[incident_cols], "osha_severe_incident")


def build_osha_ita() -> None:
    folder = ROOT / "datasets/raw/incidents/osha_ita_2025"
    summary_path = folder / "summary_2025.csv"
    case_path = folder / "case_detail_2025.csv"
    if summary_path.exists():
        summary = pd.read_csv(summary_path, low_memory=False)
        summary.columns = [clean_col(c) for c in summary.columns]
        for col in ["annual_average_employees", "total_hours_worked", "total_injuries", "total_deaths", "total_dafw_cases", "total_djtr_cases"]:
            summary[col] = pd.to_numeric(summary[col], errors="coerce").fillna(0)
        denominator = summary["total_hours_worked"].replace(0, np.nan)
        summary["total_case_rate"] = ((summary["total_injuries"] * 200000) / denominator).replace([np.inf, -np.inf], np.nan).round(3)
        summary["dart_rate"] = (((summary["total_dafw_cases"] + summary["total_djtr_cases"]) * 200000) / denominator).replace([np.inf, -np.inf], np.nan).round(3)
        summary["inspection_compliance_score"] = (100 - normalize_numeric(summary["dart_rate"].fillna(0)) * 80).clip(0, 100).round(2)
        summary.to_csv(out("datasets/processed/incidents/osha_ita_summary_2025_clean.csv"), index=False)
        summary.to_csv(out("datasets/engineered/incidents/establishment_risk_features.csv"), index=False)

    if case_path.exists():
        cases = pd.read_csv(case_path, low_memory=False)
        cases.columns = [clean_col(c) for c in cases.columns]
        keep = [
            "id", "establishment_id", "establishment_name", "city", "state", "zip_code",
            "naics_code", "industry_description", "case_number", "job_description",
            "soc_code", "soc_description", "date_of_incident", "incident_outcome",
            "type_of_incident", "new_incident_location", "new_incident_description",
            "new_nar_before_incident", "new_nar_what_happened", "new_nar_injury_illness",
            "new_nar_object_substance",
        ]
        keep = [c for c in keep if c in cases.columns]
        cases = cases[keep]
        cases["date_of_incident"] = pd.to_datetime(cases["date_of_incident"], errors="coerce")
        narrative_cols = [c for c in cases.columns if c.startswith("new_")]
        cases["case_narrative"] = cases[narrative_cols].fillna("").agg(" ".join, axis=1).str.strip()
        cases["case_narrative_length"] = cases["case_narrative"].str.len()
        cases.to_csv(out("datasets/processed/incidents/osha_ita_case_detail_2025_clean.csv"), index=False)
        cases.to_csv(out("datasets/engineered/incidents/osha_ita_case_text_features.csv"), index=False)


def build_master_indexes() -> None:
    severe = ROOT / "datasets/engineered/incidents/incident_intelligence.csv"
    establishment = ROOT / "datasets/engineered/incidents/establishment_risk_features.csv"
    if severe.exists():
        incidents = pd.read_csv(severe, low_memory=False)
        kg_incidents = pd.DataFrame({
            "subject": "incident:" + incidents["id"].astype(str),
            "predicate": "occurred_in_state",
            "object": "state:" + incidents["state"].fillna("UNK").astype(str),
        })
        kg_incidents.to_csv(out("datasets/engineered/knowledge_graph/incident_state_edges.csv"), index=False)
    if establishment.exists():
        est = pd.read_csv(establishment, low_memory=False, usecols=lambda c: c in {"establishment_id", "naics_code", "dart_rate", "total_case_rate", "inspection_compliance_score"})
        est.to_csv(out("datasets/inference/establishment_risk_inference_schema.csv"), index=False)


def main() -> int:
    build_ai4i()
    build_cmapss()
    build_air_quality()
    build_gas_drift()
    build_secom()
    build_osha_severe()
    build_osha_ita()
    build_master_indexes()
    print("processed and engineered datasets written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
