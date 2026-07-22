#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models" / "trained"
CARD_DIR = ROOT / "models" / "model_cards"
REGISTRY = ROOT / "models" / "model_registry.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))


def standardize(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = np.nanmean(x, axis=0)
    std = np.nanstd(x, axis=0)
    std[std == 0] = 1
    return np.nan_to_num((x - mean) / std), mean, std


def train_logistic(x: np.ndarray, y: np.ndarray, lr: float = 0.08, epochs: int = 500, l2: float = 0.001) -> np.ndarray:
    x = np.c_[np.ones(len(x)), x]
    w = np.zeros(x.shape[1])
    for _ in range(epochs):
        pred = sigmoid(x @ w)
        grad = x.T @ (pred - y) / len(y)
        grad[1:] += l2 * w[1:]
        w -= lr * grad
    return w


def predict_logistic(w: np.ndarray, x: np.ndarray) -> np.ndarray:
    return sigmoid(np.c_[np.ones(len(x)), x] @ w)


def binary_metrics(y: np.ndarray, p: np.ndarray, threshold: float = 0.5) -> dict:
    pred = (p >= threshold).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    accuracy = (tp + tn) / max(len(y), 1)
    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "threshold": threshold,
    }


def best_binary_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    best = None
    for threshold in np.linspace(0.05, 0.95, 37):
        metrics = binary_metrics(y, p, float(threshold))
        if best is None or metrics["f1"] > best["f1"]:
            best = metrics
    return best


def ridge_regression(x: np.ndarray, y: np.ndarray, l2: float = 1.0) -> np.ndarray:
    x = np.c_[np.ones(len(x)), x]
    reg = np.eye(x.shape[1]) * l2
    reg[0, 0] = 0
    return np.linalg.pinv(x.T @ x + reg) @ x.T @ y


def regression_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    err = p - y
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    denom = float(np.sum((y - y.mean()) ** 2)) or 1.0
    r2 = 1 - float(np.sum(err ** 2)) / denom
    return {"mae": round(mae, 4), "rmse": round(rmse, 4), "r2": round(r2, 4)}


def split(df: pd.DataFrame, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    mask = rng.random(len(df)) < 0.8
    return df.loc[mask].copy(), df.loc[~mask].copy()


def write_model(model_id: str, artifact: dict, card: str, metrics: dict, dataset: str, model_type: str) -> dict:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / f"{model_id}.json"
    card_path = CARD_DIR / f"{model_id}.md"
    artifact["model_id"] = model_id
    artifact["created_at"] = now()
    artifact["metrics"] = metrics
    model_path.write_text(json.dumps(artifact, indent=2))
    card_path.write_text(card)
    return {
        "id": model_id,
        "type": model_type,
        "dataset": dataset,
        "artifact": str(model_path.relative_to(ROOT)),
        "model_card": str(card_path.relative_to(ROOT)),
        "metrics": metrics,
        "created_at": artifact["created_at"],
        "status": "trained",
    }


def train_ai4i() -> dict:
    df = pd.read_csv(ROOT / "datasets/training/ai4i_failure_train.csv")
    valid = pd.read_csv(ROOT / "datasets/validation/ai4i_failure_validation.csv")
    features = ["air_temperature_k", "process_temperature_k", "rotational_speed_rpm", "torque_nm", "tool_wear_min", "temperature_delta_k", "power_proxy"]
    x_train, mean, std = standardize(df[features].to_numpy(float))
    y_train = df["machine_failure"].to_numpy(int)
    best = None
    for lr in [0.03, 0.06, 0.1]:
        w = train_logistic(x_train, y_train, lr=lr, epochs=450)
        x_valid = np.nan_to_num((valid[features].to_numpy(float) - mean) / std)
        metrics = best_binary_metrics(valid["machine_failure"].to_numpy(int), predict_logistic(w, x_valid))
        if best is None or metrics["f1"] > best[0]["f1"]:
            best = (metrics, w, lr)
    metrics, w, lr = best
    return write_model(
        "equipment_failure_ai4i_v1",
        {"algorithm": "numpy_logistic_regression", "features": features, "weights": w.tolist(), "mean": mean.tolist(), "std": std.tolist(), "hyperparameters": {"lr": lr, "epochs": 450, "threshold": metrics["threshold"]}},
        f"# Equipment Failure Model\n\nDataset: AI4I engineered features.\n\nPurpose: Predict machine failure risk for the maintenance agent.\n\nMetrics: `{json.dumps(metrics)}`\n\nLimitations: AI4I is synthetic and should be treated as a prototype benchmark, not a site-validated plant model.\n",
        metrics,
        "datasets/engineered/predictive_maintenance/equipment_health_features.csv",
        "binary_classifier",
    )


def train_cmapss() -> dict:
    df = pd.read_csv(ROOT / "datasets/training/cmapss_rul_train.csv")
    valid = pd.read_csv(ROOT / "datasets/validation/cmapss_rul_validation.csv")
    df = df.sample(min(50000, len(df)), random_state=42)
    valid = valid.sample(min(15000, len(valid)), random_state=42)
    features = ["cycle", "operational_setting_1", "operational_setting_2", "operational_setting_3", "sensor_signal_mean", "sensor_signal_std", "cycle_progress"]
    x_train, mean, std = standardize(df[features].to_numpy(float))
    y_train = df["remaining_useful_life"].to_numpy(float)
    w = ridge_regression(x_train, y_train, l2=10.0)
    x_valid = np.nan_to_num((valid[features].to_numpy(float) - mean) / std)
    pred = np.c_[np.ones(len(x_valid)), x_valid] @ w
    metrics = regression_metrics(valid["remaining_useful_life"].to_numpy(float), pred)
    return write_model(
        "cmapss_rul_v1",
        {"algorithm": "numpy_ridge_regression", "features": features, "weights": w.tolist(), "mean": mean.tolist(), "std": std.tolist(), "hyperparameters": {"l2": 10.0}},
        f"# C-MAPSS RUL Model\n\nDataset: NASA C-MAPSS engineered cycle data.\n\nPurpose: Estimate remaining useful life for predictive maintenance workflows.\n\nMetrics: `{json.dumps(metrics)}`\n\nLimitations: Simulated turbofan degradation; plant equipment deployment requires calibration.\n",
        metrics,
        "datasets/engineered/predictive_maintenance/cmapss_rul_features.csv",
        "regressor",
    )


def train_secom() -> dict:
    df = pd.read_csv(ROOT / "datasets/training/secom_yield_train.csv")
    valid = pd.read_csv(ROOT / "datasets/validation/secom_yield_validation.csv")
    features = ["sensor_missing_rate", "process_signal_mean", "process_signal_std"] + [f"process_sensor_{i:03d}" for i in range(20)]
    x_train, mean, std = standardize(df[features].to_numpy(float))
    y_train = df["is_yield_failure"].to_numpy(int)
    w = train_logistic(x_train, y_train, lr=0.05, epochs=650)
    x_valid = np.nan_to_num((valid[features].to_numpy(float) - mean) / std)
    metrics = best_binary_metrics(valid["is_yield_failure"].to_numpy(int), predict_logistic(w, x_valid))
    return write_model(
        "secom_quality_failure_v1",
        {"algorithm": "numpy_logistic_regression", "features": features, "weights": w.tolist(), "mean": mean.tolist(), "std": std.tolist(), "hyperparameters": {"lr": 0.05, "epochs": 650, "threshold": metrics["threshold"]}},
        f"# SECOM Quality Failure Model\n\nDataset: SECOM engineered manufacturing quality data.\n\nPurpose: Support quality and compliance auditing with process-yield risk.\n\nMetrics: `{json.dumps(metrics)}`\n\nLimitations: Small and imbalanced public dataset; use feature selection and site validation before production.\n",
        metrics,
        "datasets/engineered/manufacturing/secom_quality_features.csv",
        "binary_classifier",
    )


def train_incident() -> dict:
    train = pd.read_csv(ROOT / "datasets/training/osha_severe_incident_train.csv")
    valid = pd.read_csv(ROOT / "datasets/validation/osha_severe_incident_validation.csv")
    for df in [train, valid]:
        df["is_high_severity"] = (pd.to_numeric(df["injury_severity_score"], errors="coerce").fillna(0) >= 4).astype(int)
        df["narrative_len"] = df["final_narrative"].fillna("").str.len()
        df["has_amputation_word"] = df["final_narrative"].fillna("").str.contains("amputat|finger|hand", case=False, regex=True).astype(int)
        df["has_fall_word"] = df["final_narrative"].fillna("").str.contains("fall|fell|ladder|platform", case=False, regex=True).astype(int)
    features = ["hospitalized", "amputation", "loss_of_eye", "narrative_len", "has_amputation_word", "has_fall_word"]
    x_train, mean, std = standardize(train[features].to_numpy(float))
    y_train = train["is_high_severity"].to_numpy(int)
    w = train_logistic(x_train, y_train, lr=0.07, epochs=500)
    x_valid = np.nan_to_num((valid[features].to_numpy(float) - mean) / std)
    metrics = best_binary_metrics(valid["is_high_severity"].to_numpy(int), predict_logistic(w, x_valid))
    return write_model(
        "incident_high_severity_v1",
        {"algorithm": "numpy_logistic_regression", "features": features, "weights": w.tolist(), "mean": mean.tolist(), "std": std.tolist(), "hyperparameters": {"threshold": metrics["threshold"]}},
        f"# Incident High Severity Model\n\nDataset: OSHA severe injury engineered incident records.\n\nPurpose: Support triage, incident intelligence, and root-cause prioritization.\n\nMetrics: `{json.dumps(metrics)}`\n\nLimitations: Public OSHA report scope excludes many state-plan and fatality records.\n",
        metrics,
        "datasets/engineered/incidents/incident_intelligence.csv",
        "binary_classifier",
    )


def train_gas_anomaly() -> dict:
    df = pd.read_csv(ROOT / "datasets/engineered/gas_sensors/gas_exposure_features.csv")
    exposure = pd.to_numeric(df["gas_exposure_index"], errors="coerce").dropna()
    threshold = float(exposure.quantile(0.95))
    risk_trend_threshold = float(pd.to_numeric(df["risk_trend_24h"], errors="coerce").dropna().quantile(0.95))
    metrics = {"threshold_p95": round(threshold, 4), "risk_trend_threshold_p95": round(risk_trend_threshold, 4), "flag_rate": round(float((exposure >= threshold).mean()), 4)}
    return write_model(
        "gas_exposure_anomaly_v1",
        {"algorithm": "quantile_threshold", "features": ["gas_exposure_index", "risk_trend_24h"], "threshold": threshold, "risk_trend_threshold": risk_trend_threshold},
        f"# Gas Exposure Anomaly Model\n\nDataset: UCI Air Quality engineered exposure features.\n\nPurpose: Detect high gas exposure periods for risk intelligence.\n\nMetrics: `{json.dumps(metrics)}`\n\nLimitations: Environmental source data; thresholds require site gas calibration.\n",
        metrics,
        "datasets/engineered/gas_sensors/gas_exposure_features.csv",
        "anomaly_detector",
    )


def train_compliance() -> dict:
    df = pd.read_csv(ROOT / "datasets/engineered/incidents/establishment_risk_features.csv", nrows=120000)
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["dart_rate", "total_case_rate", "inspection_compliance_score"])
    df["needs_review"] = ((df["dart_rate"] > df["dart_rate"].quantile(0.80)) | (df["inspection_compliance_score"] < 70)).astype(int)
    train, valid = split(df.sample(min(60000, len(df)), random_state=42))
    features = ["annual_average_employees", "total_hours_worked", "total_injuries", "total_deaths", "total_dafw_cases", "total_djtr_cases", "total_case_rate", "dart_rate", "inspection_compliance_score"]
    x_train, mean, std = standardize(train[features].to_numpy(float))
    w = train_logistic(x_train, train["needs_review"].to_numpy(int), lr=0.05, epochs=350)
    x_valid = np.nan_to_num((valid[features].to_numpy(float) - mean) / std)
    metrics = best_binary_metrics(valid["needs_review"].to_numpy(int), predict_logistic(w, x_valid))
    return write_model(
        "osha_compliance_review_v1",
        {"algorithm": "numpy_logistic_regression", "features": features, "weights": w.tolist(), "mean": mean.tolist(), "std": std.tolist(), "hyperparameters": {"threshold": metrics["threshold"]}},
        f"# OSHA Compliance Review Model\n\nDataset: OSHA ITA establishment risk features.\n\nPurpose: Rank establishments/areas for compliance review based on injury rates.\n\nMetrics: `{json.dumps(metrics)}`\n\nLimitations: OSHA warns ITA submissions may contain unresolved errors and are not generalizable to all workplaces.\n",
        metrics,
        "datasets/engineered/incidents/establishment_risk_features.csv",
        "binary_classifier",
    )


def main() -> int:
    models = [train_ai4i(), train_cmapss(), train_secom(), train_incident(), train_gas_anomaly(), train_compliance()]
    REGISTRY.write_text(json.dumps({"created_at": now(), "models": models}, indent=2))
    print(f"trained {len(models)} models")
    print(REGISTRY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
