"""CardioGuard Fullstack Backend.

Frontend calls this backend. This backend forwards prediction requests
to the CardioGuard AI API.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import CardioInput, HealthResponse, PredictionResponse

load_dotenv()

AI_API_URL = os.getenv("AI_API_URL", "http://127.0.0.1:8001").rstrip("/")
AI_API_TIMEOUT = float(os.getenv("AI_API_TIMEOUT", "60"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
)

logger = logging.getLogger("cardioguard-fullstack-backend")

app = FastAPI(
    title="CardioGuard Fullstack Backend",
    description=(
        "Backend web CardioGuard yang meneruskan request prediksi "
        "ke CardioGuard AI API."
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


def extract_error_detail(response: httpx.Response) -> Any:
    """Extract readable error detail from AI API response."""

    try:
        data = response.json()
        return data.get("detail", data)
    except Exception:
        return response.text


@app.get("/", tags=["Info"])
def root() -> Dict[str, str]:
    """Return basic API information."""

    return {
        "service": "CardioGuard Fullstack Backend",
        "version": "1.1.0",
        "status": "running",
        "docs": "/docs",
        "predict_endpoint": "/predict",
        "ai_api_url": AI_API_URL,
        "disclaimer": "API ini untuk skrining awal, bukan diagnosis medis.",
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health() -> Dict[str, Any]:
    """Check AI API health through the fullstack backend."""

    try:
        async with httpx.AsyncClient(timeout=AI_API_TIMEOUT) as client:
            response = await client.get(f"{AI_API_URL}/health")

        if response.status_code >= 400:
            return {
                "status": "error",
                "model_loaded": False,
                "n_features": 0,
                "threshold": 0.0,
                "model_load_error": extract_error_detail(response),
                "ai_api_url": AI_API_URL,
            }

        data = response.json()

        return {
            "status": data.get("status", "unknown"),
            "model_loaded": bool(data.get("model_loaded", False)),
            "n_features": int(data.get("n_features", 0)),
            "threshold": float(data.get("threshold", 0.0)),
            "model_load_error": data.get("model_load_error"),
            "ai_api_url": AI_API_URL,
        }

    except httpx.RequestError as exc:
        logger.error("AI API health check failed: %s", exc)

        return {
            "status": "error",
            "model_loaded": False,
            "n_features": 0,
            "threshold": 0.0,
            "model_load_error": f"Tidak dapat terhubung ke AI API: {exc}",
            "ai_api_url": AI_API_URL,
        }


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_risk(input_data: CardioInput) -> Dict[str, Any]:
    """Forward cardiovascular risk prediction request to AI API."""

    payload = input_data.model_dump(exclude_none=True)

    try:
        async with httpx.AsyncClient(timeout=AI_API_TIMEOUT) as client:
            response = await client.post(f"{AI_API_URL}/predict", json=payload)

        if response.status_code >= 400:
            detail = extract_error_detail(response)
            raise HTTPException(status_code=response.status_code, detail=detail)

        data = response.json()

        logger.info(
            "Prediction proxied successfully: probability=%s label=%s",
            data.get("risk_probability"),
            data.get("risk_label"),
        )

        return data

    except HTTPException:
        raise

    except httpx.RequestError as exc:
        logger.error("AI API request failed: %s", exc)

        raise HTTPException(
            status_code=503,
            detail=(
                "Tidak dapat terhubung ke CardioGuard AI API. "
                f"Pastikan AI API berjalan di {AI_API_URL}."
            ),
        ) from exc

    except Exception as exc:
        logger.exception("Prediction proxy failed")

        raise HTTPException(
            status_code=500,
            detail=f"Gagal melakukan prediksi melalui AI API: {exc}",
        ) from exc