"""FastAPI service for CardioGuard model serving."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

AI_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = AI_DIR / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.append(str(SCRIPTS_DIR))

from genai_explainer import generate_ai_explanation  # noqa: E402
from inference import load_assets, predict  # noqa: E402


app = FastAPI(
    title="CardioGuard AI API",
    description=(
        "REST API untuk deteksi dini risiko penyakit kardiovaskular "
        "berbasis model machine learning."
    ),
    version="1.0.0",
)


class CardioInput(BaseModel):
    """Request body for cardiovascular risk prediction."""

    gender: int = Field(..., ge=1, le=2, description="Encoding gender sesuai dataset")
    height: float = Field(..., gt=0, description="Tinggi badan dalam cm")
    weight: float = Field(..., gt=0, description="Berat badan dalam kg")
    ap_hi: float = Field(..., gt=0, description="Tekanan darah sistolik")
    ap_lo: float = Field(..., gt=0, description="Tekanan darah diastolik")
    cholesterol: int = Field(
        ...,
        ge=1,
        le=3,
        description="1 normal, 2 above normal, 3 well above normal",
    )
    gluc: int = Field(
        ...,
        ge=1,
        le=3,
        description="1 normal, 2 above normal, 3 well above normal",
    )
    smoke: int = Field(..., ge=0, le=1, description="0 tidak merokok, 1 merokok")
    alco: int = Field(..., ge=0, le=1, description="0 tidak konsumsi alkohol, 1 konsumsi alkohol")
    active: int = Field(..., ge=0, le=1, description="0 tidak aktif, 1 aktif")
    age_years: int = Field(..., ge=1, le=120, description="Usia dalam tahun")
    bmi: Optional[float] = Field(
        default=None,
        gt=0,
        description="Opsional; akan dihitung otomatis jika tidak dikirim",
    )


class PredictionResponse(BaseModel):
    """Standard response returned by the prediction endpoint."""

    risk_probability: float
    risk_percent: float
    threshold: float
    predicted_class: int
    risk_label: str
    engineered_features: Dict[str, Any]
    disclaimer: str


try:
    model, scaler, feature_columns, threshold = load_assets()
    MODEL_LOAD_ERROR = None
except Exception as exc:  # pragma: no cover
    model = None
    scaler = None
    feature_columns = []
    threshold = 0.5
    MODEL_LOAD_ERROR = str(exc)


@app.get("/")
def root() -> Dict[str, str]:
    """Return basic API information."""

    return {
        "service": "CardioGuard AI API",
        "status": "running",
        "docs": "/docs",
        "disclaimer": "API ini untuk skrining awal, bukan diagnosis medis.",
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    """Return model and artifact loading status."""

    return {
        "status": "ok" if model is not None else "error",
        "model_loaded": model is not None,
        "n_features": len(feature_columns),
        "threshold": threshold,
        "model_load_error": MODEL_LOAD_ERROR,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_risk(input_data: CardioInput) -> Dict[str, Any]:
    """Predict cardiovascular risk from user input."""

    if model is None or scaler is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model atau artifact belum berhasil dimuat: {MODEL_LOAD_ERROR}",
        )

    payload = input_data.model_dump(exclude_none=True)

    try:
        return predict(payload, model, scaler, feature_columns, threshold)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Gagal melakukan prediksi: {exc}",
        ) from exc


@app.post("/explain")
def explain_risk(input_data: CardioInput) -> Dict[str, Any]:
    """Predict risk and add a user-friendly explanation."""

    if model is None or scaler is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model atau artifact belum berhasil dimuat: {MODEL_LOAD_ERROR}",
        )

    payload = input_data.model_dump(exclude_none=True)

    try:
        prediction = predict(payload, model, scaler, feature_columns, threshold)
        prediction["ai_explanation"] = generate_ai_explanation(payload, prediction)
        return prediction
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Gagal membuat prediksi atau penjelasan: {exc}",
        ) from exc
