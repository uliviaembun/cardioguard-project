"""FastAPI service for CardioGuard model serving."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

AI_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = AI_DIR / "scripts"
sys.path.append(str(SCRIPTS_DIR))

from inference import load_assets, predict  # noqa: E402
from genai_explainer import generate_ai_explanation  # noqa: E402

app = FastAPI(
    title="CardioGuard AI API",
    description="REST API untuk deteksi dini risiko penyakit kardiovaskular berbasis deep learning.",
    version="1.0.0",
)

model, scaler, feature_columns, threshold = load_assets()


class CardioInput(BaseModel):
    gender: int = Field(..., description="1 atau 2 sesuai encoding dataset")
    height: float = Field(..., gt=0, description="Tinggi badan dalam cm")
    weight: float = Field(..., gt=0, description="Berat badan dalam kg")
    ap_hi: float = Field(..., gt=0, description="Tekanan darah sistolik")
    ap_lo: float = Field(..., gt=0, description="Tekanan darah diastolik")
    cholesterol: int = Field(..., ge=1, le=3, description="1 normal, 2 above normal, 3 well above normal")
    gluc: int = Field(..., ge=1, le=3, description="1 normal, 2 above normal, 3 well above normal")
    smoke: int = Field(..., ge=0, le=1)
    alco: int = Field(..., ge=0, le=1)
    active: int = Field(..., ge=0, le=1)
    age_years: int = Field(..., ge=1, le=120)
    bmi: Optional[float] = Field(default=None, description="Opsional; akan dihitung otomatis jika tidak dikirim")


@app.get("/")
def root():
    return {
        "service": "CardioGuard AI API",
        "status": "running",
        "docs": "/docs",
        "disclaimer": "API ini untuk skrining awal, bukan diagnosis medis.",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "n_features": len(feature_columns),
        "threshold": threshold,
    }


@app.post("/predict")
def predict_risk(input_data: CardioInput):
    payload = input_data.model_dump(exclude_none=True)
    return predict(payload, model, scaler, feature_columns, threshold)


@app.post("/explain")
def explain_risk(input_data: CardioInput):
    payload = input_data.model_dump(exclude_none=True)
    prediction = predict(payload, model, scaler, feature_columns, threshold)
    prediction["ai_explanation"] = generate_ai_explanation(payload, prediction)
    return prediction
