"""Optional Generative AI explanation module.

Set OPENAI_API_KEY to enable this. The API output must stay educational and must not
claim to diagnose disease.
"""

from __future__ import annotations

import os
from typing import Any, Dict
from google import genai
from google.genai import types


def fallback_explanation(payload: Dict[str, Any], prediction: Dict[str, Any]) -> str:
    """Return a short deterministic explanation if Gemini is unavailable."""

    risk_label = prediction.get("risk_label", "tidak diketahui")
    risk_percent = prediction.get("risk_percent", 0)

    notes = []

    if payload.get("ap_hi", 0) >= 130 or payload.get("ap_lo", 0) >= 80:
        notes.append("tekanan darah perlu dipantau")
    if payload.get("smoke", 0) == 1:
        notes.append("kebiasaan merokok dapat meningkatkan risiko")
    if payload.get("cholesterol", 1) > 1:
        notes.append("kolesterol perlu diperhatikan")
    if payload.get("gluc", 1) > 1:
        notes.append("glukosa perlu diperhatikan")
    if payload.get("active", 1) == 0:
        notes.append("aktivitas fisik masih bisa ditingkatkan")

    if notes:
        factor_text = " Beberapa faktor yang perlu diperhatikan: " + ", ".join(notes) + "."
    else:
        factor_text = " Tetap pertahankan pola hidup sehat dan lakukan pemeriksaan berkala."

    return (
        f"Hasil skrining awal menunjukkan risiko kardiovaskular Anda berada pada kategori "
        f"{risk_label}, sekitar {risk_percent}%. "
        f"{factor_text} "
        "Hasil ini bukan diagnosis medis, jadi konsultasikan dengan tenaga kesehatan untuk evaluasi lebih lanjut."
    )


def generate_ai_explanation(payload, prediction):
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        return fallback_explanation(payload, prediction)

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
Tulis pesan singkat untuk user aplikasi CardioGuard.

Aturan:
- Langsung mulai dari isi pesan, jangan pakai "Tentu", "Berikut", "Draf", atau markdown.
- Maksimal 3 kalimat.
- Bahasa Indonesia natural, ramah, dan tidak terlalu formal.
- Jangan memberi diagnosis.
- Jangan menyatakan user pasti sakit atau pasti sehat.
- Sebutkan kategori risiko dan persentase.
- Berikan 1 saran umum yang aman.
- Akhiri dengan disclaimer singkat bahwa ini hanya skrining awal.

Data prediksi:
risk_label = {prediction.get("risk_label")}
risk_percent = {prediction.get("risk_percent")}
predicted_class = {prediction.get("predicted_class")}
threshold = {prediction.get("threshold")}

Input penting:
usia = {payload.get("age_years")}
tekanan_darah = {payload.get("ap_hi")}/{payload.get("ap_lo")}
cholesterol = {payload.get("cholesterol")}
gluc = {payload.get("gluc")}
smoke = {payload.get("smoke")}
active = {payload.get("active")}
""".strip()

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=120,
            ),
        )
        return response.text.strip()

    except Exception as exc:
        print(f"[Gemini Explainer] Gemini request failed: {exc}")
        return fallback_explanation(payload, prediction)