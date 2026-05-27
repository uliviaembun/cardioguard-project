"""Optional Generative AI explanation module.

Set OPENAI_API_KEY to enable this. The API output must stay educational and must not
claim to diagnose disease.
"""

from __future__ import annotations

import os
from typing import Any, Dict


def fallback_explanation(payload: Dict[str, Any], prediction: Dict[str, Any]) -> str:
    tips = []
    if payload.get("ap_hi", 0) >= 130 or payload.get("ap_lo", 0) >= 80:
        tips.append("tekanan darah terlihat perlu dipantau lebih rutin")
    if payload.get("cholesterol", 1) > 1:
        tips.append("kolesterol berada di atas level normal pada skema dataset")
    if payload.get("active", 1) == 0:
        tips.append("aktivitas fisik rendah dapat meningkatkan risiko")
    if payload.get("smoke", 0) == 1:
        tips.append("kebiasaan merokok merupakan faktor risiko penting")
    if not tips:
        tips.append("jaga pola makan, aktivitas fisik, dan pemeriksaan kesehatan berkala")

    return (
        f"Model memperkirakan risiko {prediction['risk_label']} "
        f"({prediction['risk_percent']}%). Faktor yang perlu diperhatikan: "
        + "; ".join(tips)
        + ". Ini bukan diagnosis medis. Konsultasikan ke tenaga kesehatan untuk pemeriksaan lanjutan."
    )


import os
from google import genai


def generate_ai_explanation(payload, prediction):
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        return fallback_explanation(payload, prediction)

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
Buat penjelasan singkat dalam bahasa Indonesia untuk pengguna aplikasi CardioGuard.

Konteks:
- CardioGuard hanya memberikan skrining awal risiko kardiovaskular.
- Jangan memberikan diagnosis.
- Jangan menyatakan pengguna pasti sakit atau pasti sehat.
- Gunakan bahasa empatik dan mudah dipahami.

Input pengguna:
{payload}

Hasil prediksi model:
{prediction}
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        return response.text

    except Exception as exc:
        return fallback_explanation(payload, prediction) + f" Gemini fallback aktif: {exc}"