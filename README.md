# CardioGuard Project

CardioGuard adalah aplikasi kesehatan digital berbasis machine learning untuk membantu melakukan skrining awal risiko penyakit kardiovaskular berdasarkan parameter fisik dan gaya hidup pengguna.

Model pada proyek ini memprediksi probabilitas risiko dari fitur seperti usia, tinggi badan, berat badan, tekanan darah, kolesterol, glukosa, aktivitas fisik, kebiasaan merokok, dan konsumsi alkohol.

> Catatan: hasil prediksi hanya digunakan sebagai skrining awal dan edukasi kesehatan. Output aplikasi bukan diagnosis medis dan tidak menggantikan konsultasi dengan dokter atau tenaga kesehatan profesional.

## Struktur Repository

```text
cardioguard-project/
├── ai-engineering/        # model, training pipeline, inference, dan API AI
├── data-science/          # eksplorasi dan analisis data
├── data/                  # dataset 
├── docs/                  # dokumentasi
├── fullstack-app/         # web
├── requirements.txt       # dependency umum
└── README.md
```

## Komponen Utama

### AI Engineering

Folder `ai-engineering/` berisi pipeline machine learning, model TensorFlow/Keras, custom layer, custom loss, custom training loop, model artifact, inference script, dan API berbasis FastAPI.

Dokumentasi detail tersedia di:

```text
ai-engineering/README_AI.md
```

### Data Science

Folder `data-science/` berisi notebook dan analisis eksploratif untuk memahami dataset serta fitur yang digunakan dalam pemodelan.

### Fullstack App

Folder `fullstack-app/` berisi aplikasi web yang menggunakan output model untuk menampilkan hasil prediksi risiko kepada pengguna.

## Menjalankan Modul AI

Masuk ke folder AI:

```bash
cd ai-engineering
```

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan virtual environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependency:

```bash
pip install -r requirements.txt
```

Jalankan API:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Buka dokumentasi API lokal:

```text
http://127.0.0.1:8000/docs
```

## Contoh Input Prediksi

```json
{
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
  "age_years": 45
}
```

## Output Model

Model menghasilkan probabilitas risiko dalam rentang 0 sampai 1. Probabilitas tersebut dibandingkan dengan threshold yang disimpan pada artifact untuk menentukan kelas risiko.

Contoh output:

```json
{
  "risk_probability": 0.39,
  "risk_percent": 39.0,
  "threshold": 0.48,
  "predicted_class": 0,
  "risk_label": "sedang",
  "disclaimer": "Hasil ini adalah skrining risiko awal, bukan diagnosis medis."
}
```

## Dokumentasi Tambahan

```text
ai-engineering/README_AI.md
```

## Disclaimer

CardioGuard tidak memberikan diagnosis medis. Hasil prediksi hanya digunakan sebagai informasi awal untuk meningkatkan kesadaran terhadap faktor risiko penyakit kardiovaskular.
