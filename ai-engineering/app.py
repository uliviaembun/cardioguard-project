"""FastAPI service for CardioGuard model serving.

This API is adjusted to match the fullstack backend/frontend contract.
The main endpoint `/predict` returns prediction + AI explanation in one response.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

AI_DIR = Path(__file__).resolve().parent
load_dotenv(AI_DIR / ".env")
load_dotenv()

SCRIPTS_DIR = AI_DIR / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.append(str(SCRIPTS_DIR))

from genai_explainer import generate_ai_explanation  # noqa: E402
from inference import load_assets, predict as model_predict  # noqa: E402


app = FastAPI(
    title="CardioGuard AI API",
    description=(
        "REST API untuk deteksi dini risiko penyakit kardiovaskular "
        "berbasis model deep learning CardioGuard."
    ),
    version="1.1.0",
)

allowed_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CardioInput(BaseModel):
    """Request body sesuai contract fullstack CardioGuard."""

    age_years: int = Field(..., ge=1, le=120, description="Usia dalam tahun")
    gender: int = Field(..., ge=1, le=2, description="1 = Wanita, 2 = Pria")

    height: float = Field(..., gt=0, description="Tinggi badan dalam cm")
    weight: float = Field(..., gt=0, description="Berat badan dalam kg")

    ap_hi: float = Field(..., gt=0, description="Tekanan darah sistolik / atas")
    ap_lo: float = Field(..., gt=0, description="Tekanan darah diastolik / bawah")

    cholesterol: int = Field(
        ...,
        ge=1,
        le=3,
        description="1 = Normal, 2 = Di atas normal, 3 = Jauh di atas normal",
    )
    gluc: int = Field(
        ...,
        ge=1,
        le=3,
        description="1 = Normal, 2 = Di atas normal, 3 = Jauh di atas normal",
    )

    smoke: int = Field(..., ge=0, le=1, description="0 = Tidak merokok, 1 = Merokok")
    alco: int = Field(..., ge=0, le=1, description="0 = Tidak konsumsi alkohol, 1 = Konsumsi")
    active: int = Field(..., ge=0, le=1, description="0 = Tidak aktif, 1 = Aktif")

    bmi: Optional[float] = Field(
        default=None,
        gt=0,
        description="Opsional; akan dihitung otomatis jika tidak dikirim",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "age_years": 45,
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
            }
        }
    }


class PredictionResponse(BaseModel):
    """Response utama yang sesuai dengan kebutuhan fullstack."""

    risk_probability: float = Field(..., description="Probabilitas risiko dalam skala 0-1")
    risk_percent: float = Field(..., description="Probabilitas risiko dalam persen")
    threshold: float = Field(..., description="Threshold model")
    predicted_class: int = Field(..., description="0 = Tidak berisiko, 1 = Berisiko")
    risk_label: str = Field(..., description="rendah / sedang / tinggi")
    risk_color: str = Field(..., description="green / yellow / red")
    health_summary: Dict[str, Any] = Field(..., description="Ringkasan kesehatan")
    disclaimer: str = Field(..., description="Disclaimer medis")
    ai_explanation: str = Field(
        ...,
        description="Penjelasan LLM atau fallback terkait hasil prediksi",
    )


try:
    model, scaler, feature_columns, threshold = load_assets()
    MODEL_LOAD_ERROR = None
except Exception as exc:  # pragma: no cover
    model = None
    scaler = None
    feature_columns = []
    threshold = 0.5
    MODEL_LOAD_ERROR = str(exc)


def validate_payload(payload: Dict[str, Any]) -> None:
    """Validate domain-specific input rules."""

    if payload["ap_hi"] <= payload["ap_lo"]:
        raise ValueError("Tekanan darah sistolik harus lebih besar dari diastolik.")

    if payload["height"] <= 0:
        raise ValueError("Tinggi badan harus lebih dari 0.")

    if payload["weight"] <= 0:
        raise ValueError("Berat badan harus lebih dari 0.")


def get_risk_color(label: str) -> str:
    """Map risk label to frontend color key."""

    normalized_label = str(label).lower().strip()

    return {
        "rendah": "green",
        "sedang": "yellow",
        "tinggi": "red",
    }.get(normalized_label, "gray")


def get_bp_category(ap_hi: float, ap_lo: float) -> int:
    """
    Blood pressure category.

    0 = Normal
    1 = Elevated
    2 = Hipertensi Tahap 1
    3 = Hipertensi Tahap 2
    """

    if ap_hi < 120 and ap_lo < 80:
        return 0

    if 120 <= ap_hi < 130 and ap_lo < 80:
        return 1

    if (130 <= ap_hi < 140) or (80 <= ap_lo < 90):
        return 2

    return 3


def get_bp_status(ap_hi: float, ap_lo: float) -> str:
    """Return frontend-friendly blood pressure status."""

    category = get_bp_category(ap_hi, ap_lo)

    return {
        0: "Normal",
        1: "Elevated",
        2: "Hipertensi Tahap 1",
        3: "Hipertensi Tahap 2",
    }[category]


def get_bmi_category(bmi: float) -> str:
    """Return frontend-friendly BMI category."""

    if bmi < 18.5:
        return "Berat Badan Kurang"

    if bmi < 25:
        return "Normal"

    if bmi < 30:
        return "Berat Badan Berlebih"

    return "Obesitas"


def get_lifestyle_risk_label(score: int) -> str:
    """Return lifestyle risk label."""

    if score == 0:
        return "Rendah"

    if score == 1:
        return "Sedang"

    return "Tinggi"


def build_fullstack_response(
    payload: Dict[str, Any],
    prediction: Dict[str, Any],
) -> Dict[str, Any]:
    """Convert raw AI prediction output into fullstack-compatible response."""

    engineered = prediction.get("engineered_features", {})

    bmi_val = float(
        engineered.get(
            "bmi",
            payload["weight"] / ((payload["height"] / 100.0) ** 2),
        )
    )

    ap_hi_val = float(payload["ap_hi"])
    ap_lo_val = float(payload["ap_lo"])

    lifestyle_score = int(
        engineered.get(
            "lifestyle_risk",
            payload["smoke"] + payload["alco"] + (1 - payload["active"]),
        )
    )

    label = str(prediction["risk_label"]).lower().strip()

    return {
        "risk_probability": float(prediction["risk_probability"]),
        "risk_percent": float(prediction["risk_percent"]),
        "threshold": float(prediction["threshold"]),
        "predicted_class": int(prediction["predicted_class"]),
        "risk_label": label,
        "risk_color": get_risk_color(label),
        "health_summary": {
            "bmi": round(bmi_val, 2),
            "bmi_category": get_bmi_category(bmi_val),
            "blood_pressure": f"{int(ap_hi_val)}/{int(ap_lo_val)} mmHg",
            "bp_status": get_bp_status(ap_hi_val, ap_lo_val),
            "lifestyle_risk_score": lifestyle_score,
            "lifestyle_risk_label": get_lifestyle_risk_label(lifestyle_score),
        },
        "disclaimer": (
            "Hasil ini adalah skrining risiko awal berbasis AI, bukan diagnosis medis. "
            "Silakan konsultasikan dengan dokter untuk evaluasi lebih lanjut."
        ),
    }


def run_prediction(input_data: CardioInput) -> Dict[str, Any]:
    """Run model prediction and attach AI explanation."""

    if model is None or scaler is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model atau artifact belum berhasil dimuat: {MODEL_LOAD_ERROR}",
        )

    payload = input_data.model_dump(exclude_none=True)

    try:
        validate_payload(payload)

        raw_prediction = model_predict(
            payload,
            model,
            scaler,
            feature_columns,
            threshold,
        )

        response = build_fullstack_response(payload, raw_prediction)

        response["ai_explanation"] = generate_ai_explanation(
            payload=payload,
            prediction=response,
        )

        return response

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Gagal melakukan prediksi: {exc}",
        ) from exc


@app.get("/")
def root() -> Dict[str, str]:
    """Return basic API information."""

    return {
        "service": "CardioGuard AI API",
        "status": "running",
        "docs": "/docs",
        "predict_endpoint": "/predict",
        "disclaimer": "API ini untuk skrining awal, bukan diagnosis medis.",
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    """Return model and artifact loading status."""

    return {
        "status": "ok" if model is not None else "error",
        "model_loaded": model is not None,
        "n_features": len(feature_columns),
        "threshold": float(threshold),
        "model_load_error": MODEL_LOAD_ERROR,
    }


@app.get("/schema/frontend")
def frontend_schema() -> Dict[str, Any]:
    """Return request and response contract summary for frontend/backend integration."""

    return {
        "predict": {
            "method": "POST",
            "endpoint": "/predict",
            "request_body": {
                "age_years": 45,
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
            },
            "response_fields": [
                "risk_probability",
                "risk_percent",
                "threshold",
                "predicted_class",
                "risk_label",
                "risk_color",
                "health_summary",
                "disclaimer",
                "ai_explanation",
            ],
        }
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_risk(input_data: CardioInput) -> Dict[str, Any]:
    """Predict cardiovascular risk and return AI explanation in one response."""

    return run_prediction(input_data)
