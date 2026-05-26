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


def generate_ai_explanation(payload: Dict[str, Any], prediction: Dict[str, Any]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback_explanation(payload, prediction)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
        prompt = f"""
Buat penjelasan singkat, empatik, dan aman secara medis dalam bahasa Indonesia.
Jangan memberi diagnosis. Jelaskan bahwa ini hanya skrining awal.

Input pengguna:
{payload}

Output model:
{prediction}

Format jawaban:
1 paragraf ringkas + 3 saran gaya hidup yang aman dan umum.
""".strip()

        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": "Kamu adalah asisten edukasi kesehatan preventif. Jangan mendiagnosis atau menggantikan dokter.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.output_text
    except Exception as exc:  # keep API reliable even if GenAI provider fails
        return fallback_explanation(payload, prediction) + f" (AI explainer fallback aktif: {exc})"
