"""CardioGuard Fullstack Backend – FastAPI application.

Loads the trained TensorFlow model at startup and exposes REST endpoints
for cardiovascular risk prediction.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from inference_engine import load_assets, predict
from schemas import CardioInput, HealthResponse, PredictionResponse

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger("cardioguard")

# ---------------------------------------------------------------------------
# Application state (populated at startup)
# ---------------------------------------------------------------------------
_state: Dict[str, Any] = {
    "model": None,
    "scaler": None,
    "feature_columns": [],
    "threshold": 0.5,
    "load_error": None,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model and artifacts once at startup."""
    logger.info("Loading CardioGuard model and artifacts …")
    try:
        model, scaler, feature_columns, threshold = load_assets()
        _state["model"] = model
        _state["scaler"] = scaler
        _state["feature_columns"] = feature_columns
        _state["threshold"] = threshold
        logger.info(
            "Model loaded — %d features, threshold=%.4f",
            len(feature_columns),
            threshold,
        )
    except Exception as exc:
        _state["load_error"] = str(exc)
        logger.error("Failed to load model: %s", exc)
    yield
    logger.info("Shutting down CardioGuard API.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="CardioGuard AI API",
    description=(
        "REST API untuk deteksi dini risiko penyakit kardiovaskular "
        "berbasis model deep learning TensorFlow."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – allow frontend dev server (Vite default port) and any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["Info"])
def root() -> Dict[str, str]:
    """Return basic API information."""
    return {
        "service": "CardioGuard AI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "disclaimer": "API ini untuk skrining awal, bukan diagnosis medis.",
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
def health() -> Dict[str, Any]:
    """Return model and artifact loading status."""
    return {
        "status": "ok" if _state["model"] is not None else "error",
        "model_loaded": _state["model"] is not None,
        "n_features": len(_state["feature_columns"]),
        "threshold": _state["threshold"],
        "model_load_error": _state["load_error"],
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_risk(input_data: CardioInput) -> Dict[str, Any]:
    """Predict cardiovascular risk from patient input.

    Accepts the 11 raw health features, computes engineered features
    server-side, and returns the model prediction with risk label,
    color indicator, health summary, and disclaimer.
    """
    if _state["model"] is None or _state["scaler"] is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model belum berhasil dimuat: {_state['load_error']}",
        )

    payload = input_data.model_dump(exclude_none=True)

    try:
        result = predict(
            payload,
            _state["model"],
            _state["scaler"],
            _state["feature_columns"],
            _state["threshold"],
        )
        logger.info(
            "Prediction: prob=%.4f label=%s",
            result["risk_probability"],
            result["risk_label"],
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal melakukan prediksi: {exc}",
        ) from exc