"""Self-contained inference engine for CardioGuard.

This module bundles everything needed to run predictions without
importing from the ai-engineering/scripts directory, keeping the
backend independently deployable.  Feature engineering and custom
Keras objects are replicated here so that the .keras model can be
loaded cleanly.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers


# ---------------------------------------------------------------------------
# Paths – relative to *this* file inside fullstack-app/backend/
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent.parent  # cardioguard-project/
_AI_DIR = _REPO_ROOT / "ai-engineering"
_ARTIFACT_DIR = _AI_DIR / "artifacts"
_MODEL_DIR = _AI_DIR / "models"


# ---------------------------------------------------------------------------
# Feature engineering (copied from training_model.py)
# ---------------------------------------------------------------------------

FEATURE_COLUMNS: List[str] = [
    "gender",
    "height",
    "weight",
    "ap_hi",
    "ap_lo",
    "cholesterol",
    "gluc",
    "smoke",
    "alco",
    "active",
    "age_years",
    "bmi",
    "bp_cat",
    "pulse_pressure",
    "map",
    "age_bmi",
    "age_ap_hi",
    "age_cholesterol",
    "bmi_ap_hi",
    "is_obese",
    "is_high_bp",
    "is_high_cholesterol",
    "is_high_glucose",
    "lifestyle_risk",
]


def bp_category(ap_hi: float, ap_lo: float) -> int:
    """Ordinal blood-pressure category.

    0: normal, 1: elevated, 2: hypertension stage 1, 3: hypertension stage 2.
    """
    if ap_hi < 120 and ap_lo < 80:
        return 0
    if 120 <= ap_hi < 130 and ap_lo < 80:
        return 1
    if (130 <= ap_hi < 140) or (80 <= ap_lo < 90):
        return 2
    return 3


def add_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Compute derived features expected by the model."""
    df = df.copy()

    if "bmi" not in df.columns:
        df["bmi"] = df["weight"] / ((df["height"] / 100.0) ** 2)

    df["bp_cat"] = [bp_category(h, l) for h, l in zip(df["ap_hi"], df["ap_lo"])]
    df["pulse_pressure"] = df["ap_hi"] - df["ap_lo"]
    df["map"] = df["ap_lo"] + (df["pulse_pressure"] / 3.0)

    # interaction / risk flags
    df["age_bmi"] = df["age_years"] * df["bmi"]
    df["age_ap_hi"] = df["age_years"] * df["ap_hi"]
    df["age_cholesterol"] = df["age_years"] * df["cholesterol"]
    df["bmi_ap_hi"] = df["bmi"] * df["ap_hi"]

    df["is_obese"] = (df["bmi"] >= 30).astype(int)
    df["is_high_bp"] = ((df["ap_hi"] >= 140) | (df["ap_lo"] >= 90)).astype(int)
    df["is_high_cholesterol"] = (df["cholesterol"] >= 2).astype(int)
    df["is_high_glucose"] = (df["gluc"] >= 2).astype(int)
    df["lifestyle_risk"] = df["smoke"] + df["alco"] + (1 - df["active"])

    return df


# ---------------------------------------------------------------------------
# Custom Keras objects (must be registered before load_model)
# ---------------------------------------------------------------------------

@tf.keras.utils.register_keras_serializable(package="CardioGuard")
class RiskFeatureGate(layers.Layer):
    """Trainable feature-wise gate to emphasize useful risk features."""

    def build(self, input_shape):
        feature_dim = int(input_shape[-1])
        self.gate_logits = self.add_weight(
            name="gate_logits",
            shape=(feature_dim,),
            initializer="zeros",
            trainable=True,
        )
        super().build(input_shape)

    def call(self, inputs):
        gate = tf.nn.sigmoid(self.gate_logits)
        return inputs * gate

    def get_config(self):
        return super().get_config()


@tf.keras.utils.register_keras_serializable(package="CardioGuard")
def cardio_guard_loss(y_true, y_pred):
    """BCE + false-negative penalty for health-risk screening."""
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.clip_by_value(tf.cast(y_pred, tf.float32), 1e-7, 1.0 - 1e-7)
    bce = tf.keras.backend.binary_crossentropy(y_true, y_pred)
    fn_penalty = tf.reduce_mean(y_true * tf.square(1.0 - y_pred), axis=-1)
    return bce + 0.05 * fn_penalty


# ---------------------------------------------------------------------------
# Asset loading
# ---------------------------------------------------------------------------

def load_assets(
    model_dir: Optional[Path] = None,
    artifact_dir: Optional[Path] = None,
) -> Tuple[tf.keras.Model, Any, List[str], float]:
    """Load model, scaler, feature column list, and optimal threshold."""
    model_dir = model_dir or _MODEL_DIR
    artifact_dir = artifact_dir or _ARTIFACT_DIR

    model_path = model_dir / "cardioguard_best_model.keras"
    if not model_path.exists():
        model_path = model_dir / "cardioguard_model.keras"

    model = tf.keras.models.load_model(
        model_path,
        custom_objects={
            "RiskFeatureGate": RiskFeatureGate,
            "cardio_guard_loss": cardio_guard_loss,
        },
    )

    with open(artifact_dir / "scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    with open(artifact_dir / "feature_columns.json", "r", encoding="utf-8") as f:
        feature_columns = json.load(f)

    threshold = 0.5
    threshold_path = artifact_dir / "threshold.json"
    if threshold_path.exists():
        with open(threshold_path, "r", encoding="utf-8") as f:
            threshold = float(json.load(f).get("threshold", 0.5))

    return model, scaler, feature_columns, threshold


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def preprocess_one(
    payload: Dict[str, Any],
    scaler: Any,
    feature_columns: Optional[List[str]] = None,
) -> Tuple[np.ndarray, pd.DataFrame]:
    """Convert a single input dict into a scaled numpy array."""
    feature_columns = feature_columns or FEATURE_COLUMNS
    df = pd.DataFrame([payload])
    df = add_feature_engineering(df)

    missing = [col for col in feature_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Input kurang kolom: {missing}")

    X = df[feature_columns].astype("float32")
    X_scaled = scaler.transform(X).astype("float32")
    return X_scaled, df[feature_columns]


# ---------------------------------------------------------------------------
# Risk classification helpers
# ---------------------------------------------------------------------------

def risk_label(probability: float, threshold: float) -> str:
    """Map probability to Indonesian risk label."""
    if probability < 0.33:
        return "rendah"
    if probability < threshold:
        return "sedang"
    return "tinggi"


def risk_color(label: str) -> str:
    """Map risk label to indicator color."""
    return {"rendah": "green", "sedang": "yellow", "tinggi": "red"}.get(label, "gray")


def bmi_category(bmi: float) -> str:
    """Human-readable BMI category."""
    if bmi < 18.5:
        return "Berat Badan Kurang"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Berat Badan Berlebih"
    return "Obesitas"


def bp_status(ap_hi: float, ap_lo: float) -> str:
    """Human-readable blood pressure status."""
    cat = bp_category(ap_hi, ap_lo)
    return {
        0: "Normal",
        1: "Elevated",
        2: "Hipertensi Tahap 1",
        3: "Hipertensi Tahap 2",
    }[cat]


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

def predict(
    payload: Dict[str, Any],
    model: tf.keras.Model,
    scaler: Any,
    feature_columns: List[str],
    threshold: float,
) -> Dict[str, Any]:
    """Run full inference pipeline and return structured result."""
    X_scaled, engineered = preprocess_one(payload, scaler, feature_columns)
    probability = float(model(X_scaled, training=False).numpy().reshape(-1)[0])
    pred_class = int(probability >= threshold)
    label = risk_label(probability, threshold)
    color = risk_color(label)

    # Compute summary values for the dashboard
    bmi_val = float(engineered["bmi"].iloc[0])
    ap_hi_val = float(payload.get("ap_hi", 0))
    ap_lo_val = float(payload.get("ap_lo", 0))
    lifestyle = int(engineered["lifestyle_risk"].iloc[0])

    health_summary = {
        "bmi": round(bmi_val, 2),
        "bmi_category": bmi_category(bmi_val),
        "blood_pressure": f"{int(ap_hi_val)}/{int(ap_lo_val)} mmHg",
        "bp_status": bp_status(ap_hi_val, ap_lo_val),
        "lifestyle_risk_score": lifestyle,
        "lifestyle_risk_label": (
            "Rendah" if lifestyle == 0
            else "Sedang" if lifestyle == 1
            else "Tinggi"
        ),
    }

    return {
        "risk_probability": round(probability, 6),
        "risk_percent": round(probability * 100, 2),
        "threshold": round(float(threshold), 4),
        "predicted_class": pred_class,
        "risk_label": label,
        "risk_color": color,
        "health_summary": health_summary,
        "disclaimer": (
            "Hasil ini adalah skrining risiko awal berbasis AI, bukan diagnosis medis. "
            "Silakan konsultasikan dengan dokter untuk evaluasi lebih lanjut."
        ),
    }
