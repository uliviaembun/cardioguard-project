"""Pydantic schemas for CardioGuard API."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CardioInput(BaseModel):
    """Request body for cardiovascular risk prediction.

    The 11 raw features expected by the model.  Engineered features
    (BMI, bp_cat, pulse_pressure, etc.) are computed server-side.
    """

    age_years: int = Field(
        ..., ge=1, le=120, description="Usia dalam tahun"
    )
    gender: int = Field(
        ..., ge=1, le=2, description="1 = Wanita, 2 = Pria"
    )
    height: float = Field(
        ..., gt=0, description="Tinggi badan dalam cm"
    )
    weight: float = Field(
        ..., gt=0, description="Berat badan dalam kg"
    )
    ap_hi: float = Field(
        ..., gt=0, description="Tekanan darah sistolik (mmHg)"
    )
    ap_lo: float = Field(
        ..., gt=0, description="Tekanan darah diastolik (mmHg)"
    )
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
    smoke: int = Field(
        ..., ge=0, le=1, description="0 = Tidak merokok, 1 = Merokok"
    )
    alco: int = Field(
        ..., ge=0, le=1, description="0 = Tidak konsumsi alkohol, 1 = Konsumsi"
    )
    active: int = Field(
        ..., ge=0, le=1, description="0 = Tidak aktif, 1 = Aktif berolahraga"
    )
    bmi: Optional[float] = Field(
        default=None,
        gt=0,
        description="Opsional; dihitung otomatis jika tidak dikirim",
    )

    model_config = {"json_schema_extra": {
        "examples": [
            {
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
        ]
    }}


class PredictionResponse(BaseModel):
    """Standard response returned by the prediction endpoint."""

    risk_probability: float = Field(
        ..., description="Probabilitas risiko (0.0 – 1.0)"
    )
    risk_percent: float = Field(
        ..., description="Probabilitas risiko dalam persen"
    )
    threshold: float = Field(
        ..., description="Threshold optimal model"
    )
    predicted_class: int = Field(
        ..., description="0 = Tidak berisiko, 1 = Berisiko"
    )
    risk_label: str = Field(
        ..., description="rendah / sedang / tinggi"
    )
    risk_color: str = Field(
        ..., description="green / yellow / red"
    )
    health_summary: Dict[str, Any] = Field(
        ..., description="Ringkasan kesehatan (BMI, tekanan darah, dll.)"
    )
    disclaimer: str = Field(
        ..., description="Pesan disclaimer medis"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    n_features: int
    threshold: float
    model_load_error: Optional[str] = None
