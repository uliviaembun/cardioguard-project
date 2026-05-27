"""Optional Generative AI explanation module for CardioGuard.

This module generates a short, safe, user-friendly explanation.
If Gemini is unavailable, missing, or errors out, it returns a deterministic fallback.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    from google import genai
    from google.genai import types
except Exception:  # pragma: no cover
    genai = None
    types = None


def _level_text(value: Any) -> str:
    """Convert encoded medical level into human-readable Indonesian text."""

    mapping = {
        1: "normal",
        2: "di atas normal",
        3: "jauh di atas normal",
        "1": "normal",
        "2": "di atas normal",
        "3": "jauh di atas normal",
    }

    return mapping.get(value, str(value))


def _yes_no(value: Any) -> str:
    """Convert 0/1 boolean-like value into Indonesian text."""

    return "ya" if int(value or 0) == 1 else "tidak"


def _collect_relevant_factors(payload: Dict[str, Any]) -> list[str]:
    """Collect relevant risk factors from normalized payload."""

    factors = []

    ap_hi = float(payload.get("ap_hi", 0))
    ap_lo = float(payload.get("ap_lo", 0))

    if ap_hi >= 130 or ap_lo >= 80:
        factors.append("tekanan darah perlu dipantau lebih rutin")

    if int(payload.get("cholesterol", 1)) > 1:
        factors.append("level kolesterol berada di atas normal")

    if int(payload.get("gluc", 1)) > 1:
        factors.append("level gula darah berada di atas normal")

    if int(payload.get("smoke", 0)) == 1:
        factors.append("kebiasaan merokok dapat meningkatkan risiko")

    if int(payload.get("alco", 0)) == 1:
        factors.append("konsumsi alkohol sebaiknya dibatasi")

    if int(payload.get("active", 1)) == 0:
        factors.append("aktivitas fisik masih bisa ditingkatkan")

    return factors


def fallback_explanation(payload: Dict[str, Any], prediction: Dict[str, Any]) -> str:
    """Return a deterministic explanation if Gemini is unavailable."""

    risk_label = prediction.get("risk_label", "tidak diketahui")
    risk_percent = prediction.get("risk_percent", 0)

    factors = _collect_relevant_factors(payload)

    if factors:
        factor_text = "Faktor yang perlu diperhatikan: " + "; ".join(factors) + "."
    else:
        factor_text = "Data utama terlihat cukup baik, tetap pertahankan gaya hidup sehat."

    return (
        f"Model memperkirakan risiko kardiovaskular Anda berada pada kategori "
        f"{risk_label} ({risk_percent}%). "
        f"{factor_text} "
        f"Hasil ini hanya skrining awal, bukan diagnosis medis."
    )


def _clean_generated_text(text: Optional[str]) -> str:
    """Clean Gemini output and reject incomplete or prompt-like responses."""

    if not text:
        return ""

    cleaned = " ".join(text.strip().split())

    forbidden_prefixes = (
        "tentu",
        "berikut",
        "draf",
        "ini draf",
        "halo!",
        "**",
        "---",
    )

    lower = cleaned.lower()

    if lower.startswith(forbidden_prefixes):
        return ""

    # Reject output that is clearly too short or only a fragment.
    if len(cleaned) < 80:
        return ""

    # Require at least one complete sentence.
    if not cleaned.endswith((".", "!", "?")):
        return ""

    return cleaned


def generate_ai_explanation(payload: Dict[str, Any], prediction: Dict[str, Any]) -> str:
    """Generate explanation using Gemini with deterministic fallback."""

    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    print("[Gemini Debug] API key loaded:", bool(api_key))
    print("[Gemini Debug] model:", model_name)
    print("[Gemini Debug] genai package loaded:", genai is not None)
    print("[Gemini Debug] types package loaded:", types is not None)

    if not api_key or genai is None or types is None:
        print("[Gemini Debug] Using fallback because API key/package is missing.")
        return fallback_explanation(payload, prediction)

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
Tulis SATU paragraf penjelasan hasil skrining CardioGuard untuk user.

Aturan output:
- Bahasa Indonesia natural, ramah, dan langsung ke inti.
- Output harus berupa 2 sampai 3 kalimat lengkap.
- Panjang ideal 60 sampai 120 kata.
- Jangan pakai markdown, bullet, judul, atau sapaan.
- Jangan mulai dengan "Tentu", "Berikut", atau "Draf".
- Jangan memberi diagnosis medis.
- Jangan menyatakan user pasti sakit atau pasti sehat.
- Sebutkan kategori risiko dan persentase risiko.
- Sebutkan faktor yang paling relevan dari data input.
- Akhiri dengan kalimat bahwa hasil ini hanya skrining awal, bukan diagnosis medis.
- Jangan mengembalikan potongan kalimat. Jawaban harus selesai.

Data prediksi:
risk_label = {prediction.get("risk_label")}
risk_percent = {prediction.get("risk_percent")}
predicted_class = {prediction.get("predicted_class")}
threshold = {prediction.get("threshold")}

Ringkasan kesehatan:
BMI = {prediction.get("health_summary", {}).get("bmi")}
kategori BMI = {prediction.get("health_summary", {}).get("bmi_category")}
tekanan darah = {prediction.get("health_summary", {}).get("blood_pressure")}
status tekanan darah = {prediction.get("health_summary", {}).get("bp_status")}
risiko gaya hidup = {prediction.get("health_summary", {}).get("lifestyle_risk_score")}/3
kategori risiko gaya hidup = {prediction.get("health_summary", {}).get("lifestyle_risk_label")}

Data input:
usia = {payload.get("age_years")} tahun
gender = {payload.get("gender")}
tinggi badan = {payload.get("height")} cm
berat badan = {payload.get("weight")} kg
tekanan darah = {payload.get("ap_hi")}/{payload.get("ap_lo")} mmHg
kolesterol = {_level_text(payload.get("cholesterol"))}
gula darah = {_level_text(payload.get("gluc"))}
merokok = {_yes_no(payload.get("smoke"))}
konsumsi alkohol = {_yes_no(payload.get("alco"))}
aktif fisik = {_yes_no(payload.get("active"))}

Tulis hanya paragraf finalnya.
""".strip()

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.35,
                max_output_tokens=512,
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
            ),
        )

        print("[Gemini Debug] finish reason:", response.candidates[0].finish_reason if response.candidates else None)
        print("[Gemini Debug] usage metadata:", response.usage_metadata)

        raw_text = response.text or ""
        generated_text = _clean_generated_text(raw_text)

        print("[Gemini Debug] raw response:", raw_text)
        print("[Gemini Debug] cleaned response:", generated_text)

        if not generated_text:
            print("[Gemini Debug] Using fallback because generated text is too short/incomplete.")
            return fallback_explanation(payload, prediction)

        return generated_text

    except Exception as exc:
        print(f"[Gemini Explainer] Gemini request failed: {exc}")
        return fallback_explanation(payload, prediction)