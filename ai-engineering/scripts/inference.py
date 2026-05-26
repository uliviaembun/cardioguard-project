"""Inference utilities for CardioGuard."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import tensorflow as tf

from training_model import FEATURE_COLUMNS, RiskFeatureGate, cardio_guard_loss, add_feature_engineering

SCRIPT_DIR = Path(__file__).resolve().parent
AI_DIR = SCRIPT_DIR.parent
ARTIFACT_DIR = AI_DIR / "artifacts"
MODEL_DIR = AI_DIR / "models"

MODEL_PATH = MODEL_DIR / "cardioguard_best_model.keras"
if not MODEL_PATH.exists():
    MODEL_PATH = MODEL_DIR / "cardioguard_model.keras"


def load_assets():
    model = tf.keras.models.load_model(
        MODEL_PATH,
        custom_objects={
            "RiskFeatureGate": RiskFeatureGate,
            "cardio_guard_loss": cardio_guard_loss,
        },
    )
    with open(ARTIFACT_DIR / "scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open(ARTIFACT_DIR / "feature_columns.json", "r", encoding="utf-8") as f:
        feature_columns = json.load(f)
    threshold_path = ARTIFACT_DIR / "threshold.json"
    threshold = 0.5
    if threshold_path.exists():
        with open(threshold_path, "r", encoding="utf-8") as f:
            threshold = float(json.load(f).get("threshold", 0.5))
    return model, scaler, feature_columns, threshold


def preprocess_one(payload: Dict[str, Any], scaler, feature_columns=None):
    feature_columns = feature_columns or FEATURE_COLUMNS
    df = pd.DataFrame([payload])
    df = add_feature_engineering(df)
    missing = [col for col in feature_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Input kurang kolom: {missing}")
    X = df[feature_columns].astype("float32")
    X_scaled = scaler.transform(X).astype("float32")
    return X_scaled, df[feature_columns]


def risk_label(probability: float, threshold: float) -> str:
    if probability < 0.33:
        return "rendah"
    if probability < threshold:
        return "sedang"
    return "tinggi"


def predict(payload: Dict[str, Any], model=None, scaler=None, feature_columns=None, threshold=None):
    if model is None or scaler is None or feature_columns is None or threshold is None:
        model, scaler, feature_columns, threshold = load_assets()

    X_scaled, engineered = preprocess_one(payload, scaler, feature_columns)
    probability = float(model(X_scaled, training=False).numpy().reshape(-1)[0])
    pred_class = int(probability >= threshold)
    return {
        "risk_probability": round(probability, 6),
        "risk_percent": round(probability * 100, 2),
        "threshold": round(float(threshold), 4),
        "predicted_class": pred_class,
        "risk_label": risk_label(probability, threshold),
        "engineered_features": engineered.iloc[0].to_dict(),
        "disclaimer": "Hasil ini adalah skrining risiko awal, bukan diagnosis medis.",
    }


if __name__ == "__main__":
    sample = {
        "gender": 2,
        "height": 168,
        "weight": 75,
        "ap_hi": 130,
        "ap_lo": 85,
        "cholesterol": 1,
        "gluc": 1,
        "smoke": 0,
        "alco": 0,
        "active": 1,
        "age_years": 45,
    }
    print(json.dumps(predict(sample), indent=2, ensure_ascii=False))
