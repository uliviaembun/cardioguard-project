# CardioGuard AI Engineering

Folder ini berisi modul AI untuk proyek **CardioGuard**, mulai dari training model, penyimpanan artifact, inference, Generative AI explanation, sampai API prediksi risiko penyakit kardiovaskular.

Model digunakan untuk membantu skrining awal risiko berdasarkan fitur seperti usia, tinggi badan, berat badan, tekanan darah, kolesterol, glukosa, aktivitas fisik, kebiasaan merokok, dan konsumsi alkohol.

> Hasil prediksi dari model ini digunakan sebagai skrining awal dan edukasi kesehatan. Output model tidak ditujukan sebagai pengganti diagnosis dokter atau tenaga medis profesional.

## Live API

AI API production di-deploy menggunakan **Hugging Face Spaces** sebagai Docker Space.

```text
https://uliviaembun-cardioguard-api.hf.space
```

Endpoint utama:

```text
POST /predict
```

Health check:

```text
GET /health
```

## Overview

CardioGuard AI dikembangkan sebagai modul prediksi risiko penyakit kardiovaskular berbasis model deep learning. Model dibangun menggunakan TensorFlow/Keras dan disajikan melalui REST API berbasis FastAPI.

Pipeline AI mencakup:

* preprocessing dan feature engineering;
* training model neural network;
* custom layer dan custom loss function;
* custom training loop menggunakan `tf.GradientTape`;
* penyimpanan model dalam format `.keras`;
* penyimpanan artifact preprocessing dan threshold;
* inference script untuk pengujian lokal;
* REST API untuk serving model;
* TensorBoard logging untuk monitoring training;
* Generative AI explanation menggunakan Gemini API;
* fallback explanation jika Gemini API tidak tersedia atau error.

## Production Architecture

Pada versi production, AI API di-host sebagai service mandiri di Hugging Face Spaces. Frontend production langsung memanggil endpoint `/predict` dari Hugging Face API.

```text
Frontend Vercel
        ↓
Hugging Face Spaces API
        ↓
TensorFlow/Keras Model
        ↓
Gemini API / Fallback Explanation
```

Production flow:

```text
User submit form di website
        ↓
Frontend POST ke /predict
        ↓
AI API melakukan preprocessing dan feature engineering
        ↓
Model TensorFlow menghasilkan probabilitas risiko
        ↓
Sistem membentuk health_summary dan risk_label
        ↓
Gemini API membuat ai_explanation
        ↓
Jika Gemini error, fallback explanation digunakan
        ↓
Response dikembalikan ke frontend
```

## Folder Structure

```text
ai-engineering/
├── app.py                         # FastAPI app untuk serving model
├── Dockerfile                     # Docker config untuk Hugging Face Spaces
├── kaggle_train.py                # Script training via Kaggle
├── kernel-metadata.json           # Kaggle kernel metadata
├── requirements.txt               # Dependency AI API
├── README_AI.md                   # Dokumentasi AI engineering
├── scripts/
│   ├── training_model.py          # Training pipeline
│   ├── inference.py               # Inference utilities
│   └── genai_explainer.py         # Gemini/fallback explanation module
├── models/
│   ├── cardioguard_model.keras
│   └── cardioguard_best_model.keras
├── artifacts/
│   ├── scaler.pkl                 # Scaler preprocessing
│   ├── feature_columns.json       # Daftar fitur model
│   ├── threshold.json             # Threshold klasifikasi
│   └── training_metrics.json      # Ringkasan metrik training
└── logs/
    └── fit/                       # TensorBoard logs
```

## Model Description

Model yang digunakan adalah neural network berbasis **TensorFlow Keras Functional API**. Input model berasal dari fitur numerik dan kategorikal yang berkaitan dengan risiko penyakit kardiovaskular.

Komponen utama:

* `RiskFeatureGate`: custom layer untuk membantu model memberi bobot adaptif pada fitur input;
* `cardio_guard_loss`: custom loss function untuk mendukung proses klasifikasi risiko;
* `CustomTrainingMonitor`: monitor training untuk menyimpan model terbaik berdasarkan performa validasi;
* custom training loop berbasis `tf.GradientTape`.

Output model berupa probabilitas risiko dalam rentang 0 sampai 1. Probabilitas tersebut dibandingkan dengan threshold dari `artifacts/threshold.json` untuk menentukan kelas risiko.

## Input Features

Endpoint `/predict` menerima 11 fitur input utama dari user:

| Feature       | Description                                                                  |
| ------------- | ---------------------------------------------------------------------------- |
| `age_years`   | Usia dalam tahun                                                             |
| `gender`      | Encoding jenis kelamin: `1` = wanita, `2` = pria                             |
| `height`      | Tinggi badan dalam cm                                                        |
| `weight`      | Berat badan dalam kg                                                         |
| `ap_hi`       | Tekanan darah sistolik                                                       |
| `ap_lo`       | Tekanan darah diastolik                                                      |
| `cholesterol` | Kategori kolesterol: `1` normal, `2` di atas normal, `3` jauh di atas normal |
| `gluc`        | Kategori glukosa: `1` normal, `2` di atas normal, `3` jauh di atas normal    |
| `smoke`       | Status merokok: `0` tidak, `1` ya                                            |
| `alco`        | Konsumsi alkohol: `0` tidak, `1` ya                                          |
| `active`      | Aktivitas fisik: `0` tidak aktif, `1` aktif                                  |

Dalam pipeline inference, input tersebut diproses menjadi **24 fitur model**, yang terdiri dari fitur input utama dan fitur hasil feature engineering.

Contoh fitur hasil feature engineering:

* BMI;
* kategori tekanan darah;
* pulse pressure;
* mean arterial pressure;
* indikator obesitas;
* indikator tekanan darah tinggi;
* indikator kolesterol tinggi;
* indikator glukosa tinggi;
* skor risiko gaya hidup;
* fitur interaksi seperti `age_bmi` dan `age_ap_hi`.

## Training

Training dilakukan melalui script:

```bash
python scripts/training_model.py
```

Contoh command training:

```bash
python scripts/training_model.py --rebuild-data --epochs 40 --batch-size 128 --learning-rate 0.001
```

Output training disimpan ke folder:

```text
models/
artifacts/
logs/
```

## Training Output

### Models

```text
models/cardioguard_model.keras
models/cardioguard_best_model.keras
```

| File                           | Description                                 |
| ------------------------------ | ------------------------------------------- |
| `cardioguard_model.keras`      | Model pada epoch terakhir                   |
| `cardioguard_best_model.keras` | Model terbaik berdasarkan performa validasi |

Untuk inference dan API, model yang direkomendasikan adalah:

```text
models/cardioguard_best_model.keras
```

### Artifacts

Artifact yang dibutuhkan untuk inference:

```text
artifacts/scaler.pkl
artifacts/feature_columns.json
artifacts/threshold.json
artifacts/training_metrics.json
```

| Artifact                | Description                       |
| ----------------------- | --------------------------------- |
| `scaler.pkl`            | Scaler untuk normalisasi fitur    |
| `feature_columns.json`  | Daftar fitur yang digunakan model |
| `threshold.json`        | Threshold klasifikasi risiko      |
| `training_metrics.json` | Ringkasan metrik hasil training   |

### TensorBoard Logs

Log training disimpan di:

```text
logs/fit/
```

Untuk membuka TensorBoard:

```bash
tensorboard --logdir logs
```

## Local Setup

Disarankan menggunakan Python 3.10 atau 3.11.

Masuk ke folder AI engineering:

```bash
cd ai-engineering
```

Buat virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependency:

```bash
pip install -r requirements.txt
```

Buat file `.env` di folder `ai-engineering/`:

```env
GEMINI_API_KEY=gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
TF_CPP_MIN_LOG_LEVEL=2
```

Jika `GEMINI_API_KEY` tidak tersedia, API tetap dapat berjalan menggunakan fallback explanation.

## Inference

Untuk mencoba inference tanpa menjalankan API:

```bash
python scripts/inference.py
```

Script inference akan memuat model, scaler, daftar fitur, dan threshold dari folder `models/` dan `artifacts/`.

## Running the API Locally

Dari folder `ai-engineering`, jalankan:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8001
```

Dokumentasi endpoint dapat dibuka di:

```text
http://127.0.0.1:8001/docs
```

Health check:

```text
http://127.0.0.1:8001/health
```

Expected response:

```json
{
  "status": "ok",
  "model_loaded": true,
  "n_features": 24,
  "threshold": 0.48,
  "model_load_error": null
}
```

## API Endpoints

| Method | Endpoint           | Description                                                                         |
| ------ | ------------------ | ----------------------------------------------------------------------------------- |
| `GET`  | `/`                | Informasi singkat service                                                           |
| `GET`  | `/health`          | Mengecek status model dan artifact                                                  |
| `GET`  | `/schema/frontend` | Ringkasan schema request/response                                                   |
| `POST` | `/predict`         | Menghasilkan prediksi risiko, ringkasan kesehatan, disclaimer, dan `ai_explanation` |

> Endpoint utama untuk frontend adalah `POST /predict`. Endpoint ini sudah mengembalikan semua kebutuhan UI dalam satu kali hit API.

## Example Request

Contoh request dan response dari endpoint `/predict`.

### Risiko Rendah

<table>
<tr>
<td width="50%"><strong>Input Request</strong></td>
<td width="50%"><strong>Output Response</strong></td>
</tr>
<tr>
<td>

```json
{
  "age_years": 25,
  "gender": 1,
  "height": 160,
  "weight": 52,
  "ap_hi": 110,
  "ap_lo": 70,
  "cholesterol": 1,
  "gluc": 1,
  "smoke": 0,
  "alco": 0,
  "active": 1
}
```

</td>
<td>

```json
{
  "risk_probability": 0.012003,
  "risk_percent": 1.2,
  "threshold": 0.48,
  "predicted_class": 0,
  "risk_label": "rendah",
  "risk_color": "green",
  "health_summary": {
    "bmi": 20.31,
    "bmi_category": "Normal",
    "blood_pressure": "110/70 mmHg",
    "bp_status": "Normal",
    "lifestyle_risk_score": 0,
    "lifestyle_risk_label": "Rendah"
  },
  "disclaimer": "Hasil ini adalah skrining risiko awal berbasis AI, bukan diagnosis medis. Silakan konsultasikan dengan dokter untuk evaluasi lebih lanjut.",
  "ai_explanation": "Hasil skrining CardioGuard Anda menunjukkan risiko rendah sebesar 1.2% untuk masalah kardiovaskular. Ini didukung oleh gaya hidup sehat Anda yang aktif secara fisik, tidak merokok, dan tidak mengonsumsi alkohol, serta tekanan darah dan BMI yang berada dalam rentang normal. Namun, perlu diingat bahwa ini hanyalah skrining awal dan bukan diagnosis medis."
}
```

</td>
</tr>
</table>

### Risiko Tinggi

<table>
<tr>
<td width="50%"><strong>Input Request</strong></td>
<td width="50%"><strong>Output Response</strong></td>
</tr>
<tr>
<td>

```json
{
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
  "active": 0
}
```

</td>
<td>

```json
{
  "risk_probability": 0.848959,
  "risk_percent": 84.9,
  "threshold": 0.48,
  "predicted_class": 1,
  "risk_label": "tinggi",
  "risk_color": "red",
  "health_summary": {
    "bmi": 31.22,
    "bmi_category": "Obesitas",
    "blood_pressure": "160/100 mmHg",
    "bp_status": "Hipertensi Tahap 2",
    "lifestyle_risk_score": 3,
    "lifestyle_risk_label": "Tinggi"
  },
  "disclaimer": "Hasil ini adalah skrining risiko awal berbasis AI, bukan diagnosis medis. Silakan konsultasikan dengan dokter untuk evaluasi lebih lanjut.",
  "ai_explanation": "Hasil skrining CardioGuard Anda menunjukkan kategori risiko tinggi dengan persentase 84.9%. Hal ini dipengaruhi oleh beberapa faktor, terutama usia Anda yang 60 tahun, tekanan darah 160/100 mmHg yang termasuk Hipertensi Tahap 2, serta gaya hidup Anda yang merokok, mengonsumsi alkohol, dan kurang aktif secara fisik. Ingat, hasil ini hanyalah skrining awal dan bukan diagnosis medis."
}
```

</td>
</tr>
</table>

Catatan: nilai probabilitas, label risiko, dan isi `ai_explanation` dapat berbeda bergantung pada artifact model, threshold, input pengguna, serta status koneksi ke Gemini API.

## Generative AI Explanation

CardioGuard menggunakan **Gemini API** sebagai LLM untuk menghasilkan penjelasan hasil prediksi yang lebih natural dan mudah dipahami pengguna.

Pada endpoint `/predict`, sistem melakukan:

```text
1. Model TensorFlow menghasilkan prediksi risiko.
2. Sistem membentuk label risiko dan health_summary.
3. Gemini API membuat ai_explanation berdasarkan hasil model dan input pengguna.
4. Jika Gemini API tidak tersedia/error, sistem menggunakan fallback explanation berbasis aturan.
```

Gemini API **tidak menentukan hasil prediksi utama**. Prediksi tetap berasal dari model TensorFlow/Keras.

Konfigurasi Gemini dilakukan melalui environment variable:

```env
GEMINI_API_KEY=gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Jika API key tidak tersedia, invalid, atau melewati limit, sistem tetap mengembalikan response lengkap menggunakan fallback explanation.

## Deployment to Hugging Face Spaces

AI API production di-deploy sebagai **Docker Space** di Hugging Face Spaces.

Hugging Face Space:

```text
https://huggingface.co/spaces/uliviaembun/cardioguard-api
```

Production API URL:

```text
https://uliviaembun-cardioguard-api.hf.space
```

Dockerfile:

```text
ai-engineering/Dockerfile
```

Port yang digunakan:

```text
7860
```

Docker command:

```dockerfile
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

Metadata `README.md` pada Space:

```yaml
---
title: CardioGuard API
emoji: ❤️
colorFrom: red
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---
```

Required variables & secrets di Hugging Face:

```env
GEMINI_API_KEY=gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://www.cardioguard.my.id,https://cardioguard.my.id
TF_CPP_MIN_LOG_LEVEL=2
```

## Dockerfile

Dockerfile yang digunakan untuk deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

## Testing Hosted API

Test health endpoint:

```text
https://uliviaembun-cardioguard-api.hf.space/health
```

Test prediction endpoint:

```bash
curl -X POST "https://uliviaembun-cardioguard-api.hf.space/predict" \
  -H "Content-Type: application/json" \
  -d '{
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
    "active": 0
  }'
```

Jika berhasil, response akan memiliki field:

```json
{
  "risk_percent": 84.9,
  "risk_label": "tinggi",
  "risk_color": "red",
  "ai_explanation": "..."
}
```

## Kaggle Training

Training model dapat dilakukan di Kaggle untuk memanfaatkan GPU.

Script yang digunakan:

```text
kaggle_train.py
```

Contoh push kernel ke Kaggle:

```bash
kaggle kernels push -p . --accelerator NvidiaTeslaT4
```

Cek status kernel:

```bash
kaggle kernels status uliviaembun/cardioguard-ai-training
```

Download output kernel:

```bash
kaggle kernels output uliviaembun/cardioguard-ai-training -p kaggle_outputs -o
```

## Evaluation Notes

Model dievaluasi menggunakan beberapa metrik, seperti accuracy, AUC, MAE berbasis probabilitas, dan MAE berbasis label hasil threshold.

Pada eksperimen terakhir, performa model belum mencapai target akurasi 85% dan MAE label 0,02. Hal ini dicatat sebagai keterbatasan eksperimen karena dataset yang digunakan merupakan data tabular dengan fitur klinis sederhana. Untuk konteks skrining awal, metrik seperti AUC, recall, precision, dan threshold selection tetap perlu dipertimbangkan bersama accuracy.

Detail metrik tersimpan di:

```text
artifacts/training_metrics.json
```

## Limitations

Beberapa keterbatasan modul AI ini:

* data input masih terbatas pada fitur umum;
* model tidak menggunakan data klinis lanjutan seperti ECG, riwayat penyakit detail, atau hasil pemeriksaan laboratorium lengkap;
* prediksi bersifat estimasi risiko awal;
* performa model dapat berubah jika distribusi data pengguna berbeda dari data training;
* nilai prediksi dapat berubah jika artifact model atau threshold diperbarui;
* `ai_explanation` dapat berbeda tergantung respons Gemini API;
* jika Gemini API error, sistem menggunakan fallback explanation;
* Hugging Face Free CPU Space dapat mengalami cold start setelah periode tidak aktif.

## Disclaimer

CardioGuard tidak memberikan diagnosis medis. Hasil prediksi hanya digunakan sebagai informasi awal untuk meningkatkan kesadaran pengguna terhadap faktor risiko penyakit kardiovaskular. Untuk evaluasi kesehatan yang lebih akurat, pengguna tetap disarankan berkonsultasi dengan tenaga medis profesional.
