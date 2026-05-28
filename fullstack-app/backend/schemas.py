"""Pydantic schemas for CardioGuard Fullstack Backend."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CardioInput(BaseModel):
    """Request body from frontend for cardiovascular risk prediction."""

    age_years: int = Field(..., ge=1, le=120, description="Usia dalam tahun")
    gender: int = Field(..., ge=1, le=2, description="1 = Wanita, 2 = Pria")

    height: float = Field(..., gt=0, description="Tinggi badan dalam cm")
    weight: float = Field(..., gt=0, description="Berat badan dalam kg")

    ap_hi: float = Field(..., gt=0, description="Tekanan darah sistolik")
    ap_lo: float = Field(..., gt=0, description="Tekanan darah diastolik")

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
        description="Opsional; akan dihitung otomatis oleh AI API jika tidak dikirim",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "age_years": 60,
                "gender": 2,
                "height": 165,
                "weight": 85,
                "ap_hi": 160,
                "ap_lo": 100,
                "cholesterol": 3,
                "gluc": 2,
                "smoke": 1,
                "alco": 1,
                "active": 0,
            }
        }
    }


class PredictionResponse(BaseModel):
    """Response returned from AI API and forwarded to frontend."""

    risk_probability: float = Field(..., description="Probabilitas risiko dalam skala 0-1")
    risk_percent: float = Field(..., description="Probabilitas risiko dalam persen")
    threshold: float = Field(..., description="Threshold model")
    predicted_class: int = Field(..., description="0 = Tidak berisiko tinggi, 1 = Berisiko tinggi")
    risk_label: str = Field(..., description="rendah / sedang / tinggi")
    risk_color: str = Field(..., description="green / yellow / red")
    health_summary: Dict[str, Any] = Field(..., description="Ringkasan kesehatan")
    disclaimer: str = Field(..., description="Disclaimer medis")
    ai_explanation: str = Field(..., description="Penjelasan AI atau fallback explanation")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    n_features: int
    threshold: float
    model_load_error: Optional[Any] = None
    ai_api_url: Optional[str] = None