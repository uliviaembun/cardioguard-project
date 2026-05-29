# CardioGuard

**CardioGuard** adalah aplikasi web berbasis Artificial Intelligence untuk membantu skrining awal risiko penyakit kardiovaskular. Aplikasi ini menerima data kesehatan dasar pengguna, seperti usia, tinggi badan, berat badan, tekanan darah, kolesterol, gula darah, aktivitas fisik, kebiasaan merokok, dan konsumsi alkohol. Berdasarkan data tersebut, sistem memberikan estimasi tingkat risiko kardiovaskular, ringkasan kesehatan, serta penjelasan singkat yang mudah dipahami pengguna.

> **Disclaimer:** CardioGuard bukan alat diagnosis medis. Hasil prediksi hanya digunakan sebagai skrining awal dan edukasi kesehatan. Untuk evaluasi kesehatan yang akurat, pengguna tetap disarankan berkonsultasi dengan dokter atau tenaga medis profesional.

## Live Demo

Aplikasi CardioGuard dapat diakses melalui:

```text
https://www.cardioguard.my.id
```

Production API:

```text
https://uliviaembun-cardioguard-api.hf.space
```

Main endpoint:

```text
POST /predict
```

## Overview

Penyakit kardiovaskular merupakan salah satu masalah kesehatan serius yang sering berkaitan dengan faktor risiko seperti tekanan darah tinggi, obesitas, kolesterol tinggi, gula darah tinggi, kebiasaan merokok, konsumsi alkohol, dan kurangnya aktivitas fisik.

CardioGuard dikembangkan untuk membantu pengguna memahami risiko awal secara lebih mudah melalui aplikasi web yang interaktif. Sistem ini menggabungkan:

* model deep learning berbasis TensorFlow/Keras untuk prediksi risiko;
* Gemini API sebagai Large Language Model untuk menghasilkan penjelasan hasil skrining;
* web frontend untuk input data, visualisasi hasil, dan cetak laporan skrining.

## Main Features

Fitur utama CardioGuard:

* Form input data kesehatan pengguna.
* Prediksi risiko penyakit kardiovaskular berbasis model deep learning.
* Kategori risiko: rendah, sedang, dan tinggi.
* Ringkasan kesehatan berupa BMI, kategori BMI, tekanan darah, dan risiko gaya hidup.
* Penjelasan hasil prediksi menggunakan Gemini API sebagai LLM.
* Fallback explanation jika Gemini API tidak tersedia atau mengalami error.
* Tampilan web interaktif untuk melihat hasil skrining.
* Cetak hasil skrining dalam format laporan sederhana agar dapat disimpan atau dibawa saat konsultasi.
* API modular yang dapat dijalankan secara lokal maupun di-host sebagai service terpisah.

## Production Architecture

Pada versi production, arsitektur dibuat sederhana agar deployment gratis lebih efisien dan menghindari double cold start.

```text
User
  ↓
Custom Domain
https://www.cardioguard.my.id
  ↓
Frontend Web di Vercel
  ↓
Hugging Face Spaces API
https://uliviaembun-cardioguard-api.hf.space
  ↓
TensorFlow Model + Gemini API
```

Production hosting summary:

| Component     | Platform            | Description                                                               |
| ------------- | ------------------- | ------------------------------------------------------------------------- |
| Custom Domain | DomaiNesia          | Domain publik `www.cardioguard.my.id`                                     |
| Frontend      | Vercel              | Menampilkan form, hasil analisis, dan fitur cetak hasil                   |
| AI API        | Hugging Face Spaces | Menjalankan endpoint `/predict`, model TensorFlow, dan Gemini explanation |
| LLM           | Gemini API          | Menghasilkan `ai_explanation` yang natural dan mudah dipahami             |
| Source Code   | GitHub              | Menyimpan source code project                                             |

## Production API Flow

Alur request saat user melakukan skrining di website production:

```text
User membuka https://www.cardioguard.my.id
        ↓
Frontend Vercel menerima input user
        ↓
Frontend POST ke Hugging Face API
        ↓
POST https://uliviaembun-cardioguard-api.hf.space/predict
        ↓
API menjalankan model TensorFlow untuk prediksi risiko
        ↓
API menggunakan Gemini API sebagai LLM untuk membuat ai_explanation
        ↓
Jika Gemini API tidak tersedia/error, API menggunakan fallback explanation
        ↓
API mengembalikan:
- risk_probability
- risk_percent
- risk_label
- risk_color
- health_summary
- disclaimer
- ai_explanation
        ↓
Frontend menampilkan hasil analisis ke user
```

## Local Development Architecture

Untuk development lokal, project tetap menyediakan backend proxy di folder `fullstack-app/backend`.

```text
Frontend Web
    ↓
Fullstack Backend
    ↓
AI API
    ↓
TensorFlow Model + Gemini API
```

Port lokal yang digunakan:

| Service           | URL                     | Description                              |
| ----------------- | ----------------------- | ---------------------------------------- |
| Frontend          | `http://localhost:5173` | Tampilan web CardioGuard                 |
| Fullstack Backend | `http://127.0.0.1:8000` | Backend proxy untuk development lokal    |
| AI API            | `http://127.0.0.1:8001` | Service AI untuk prediksi dan penjelasan |

> Catatan: pada production hosted version, frontend langsung memanggil Hugging Face Spaces API. Backend proxy tetap tersedia untuk local development dan eksperimen integrasi.

## Repository Structure

```text
cardioguard-project/
├── ai-engineering/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── README_AI.md
│   ├── scripts/
│   │   ├── inference.py
│   │   ├── genai_explainer.py
│   │   └── training_model.py
│   ├── models/
│   ├── artifacts/
│   └── logs/
│
├── fullstack-app/
│   ├── backend/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── requirements.txt
│   └── frontend/
│       ├── src/
│       ├── package.json
│       └── .env
│
├── data-science/
├── data/
├── docs/
├── requirements.txt
└── README.md
```

## Tech Stack

| Layer            | Technology                              |
| ---------------- | --------------------------------------- |
| Frontend         | React, Vite                             |
| Frontend Hosting | Vercel                                  |
| AI API Hosting   | Hugging Face Spaces                     |
| Local Backend    | FastAPI, HTTPX                          |
| AI API           | FastAPI, TensorFlow/Keras               |
| Model Serving    | TensorFlow/Keras `.keras` model         |
| LLM Explanation  | Gemini API                              |
| Data Processing  | NumPy, Pandas, Scikit-learn             |
| Environment      | Python virtual environment, Node.js/npm |

## AI Module

AI module berada di folder:

```text
ai-engineering/
```

AI API menjalankan model TensorFlow/Keras untuk menghasilkan prediksi risiko kardiovaskular. Endpoint utama yang digunakan adalah:

```text
POST /predict
```

Endpoint ini mengembalikan:

* probabilitas risiko;
* persentase risiko;
* label risiko;
* warna indikator risiko;
* ringkasan kesehatan;
* disclaimer medis;
* `ai_explanation` dari Gemini API atau fallback explanation.

Dokumentasi teknis lengkap AI module tersedia di:

```text
ai-engineering/README_AI.md
```

## API Contract

### Request Body

Contoh request ke endpoint `/predict`:

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

Keterangan encoding:

| Field         | Description                                                   |
| ------------- | ------------------------------------------------------------- |
| `gender`      | `1` = Wanita, `2` = Pria                                      |
| `cholesterol` | `1` = Normal, `2` = Di atas normal, `3` = Jauh di atas normal |
| `gluc`        | `1` = Normal, `2` = Di atas normal, `3` = Jauh di atas normal |
| `smoke`       | `0` = Tidak merokok, `1` = Merokok                            |
| `alco`        | `0` = Tidak konsumsi alkohol, `1` = Konsumsi alkohol          |
| `active`      | `0` = Tidak aktif, `1` = Aktif                                |

### Response Body

Contoh response:

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
  "ai_explanation": "Hasil skrining CardioGuard menunjukkan kategori risiko tinggi dengan persentase 84.9%. Faktor yang paling berkontribusi antara lain tekanan darah, BMI, dan gaya hidup. Hasil ini hanya skrining awal dan bukan diagnosis medis."
}
```

## Running the Project Locally

Ada dua opsi running lokal:

1. **Frontend langsung ke Hugging Face API** — paling cepat untuk testing UI.
2. **Full local services** — menjalankan AI API, backend proxy, dan frontend secara lokal.

## Option 1 — Run Frontend with Hosted API

Gunakan opsi ini jika API Hugging Face sudah aktif dan kamu hanya ingin menjalankan frontend lokal.

Masuk ke folder frontend:

```bash
cd fullstack-app/frontend
```

Buat file `.env`:

```env
VITE_API_URL=https://uliviaembun-cardioguard-api.hf.space
```

Install dependency:

```bash
npm install
```

Jalankan frontend:

```bash
npm run dev
```

Buka aplikasi:

```text
http://localhost:5173
```

## Option 2 — Run Full Local Services

Gunakan opsi ini jika ingin menjalankan seluruh service secara lokal.

### 1. Run AI API

Masuk ke folder AI:

```bash
cd ai-engineering
```

Buat dan aktifkan virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

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

Jika `GEMINI_API_KEY` tidak tersedia, service tetap berjalan menggunakan fallback explanation.

Jalankan AI API:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8001
```

Cek health endpoint:

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

### 2. Run Fullstack Backend

Masuk ke folder backend:

```bash
cd fullstack-app/backend
```

Buat dan aktifkan virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependency:

```bash
pip install -r requirements.txt
```

Buat file `.env` di folder `fullstack-app/backend/`:

```env
AI_API_URL=http://127.0.0.1:8001
AI_API_TIMEOUT=60
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Jalankan backend:

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Cek health endpoint:

```text
http://127.0.0.1:8000/health
```

Jika berhasil, backend akan meneruskan health check ke AI API dan mengembalikan status model.

### 3. Run Frontend

Masuk ke folder frontend:

```bash
cd fullstack-app/frontend
```

Buat file `.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Install dependency:

```bash
npm install
```

Jalankan frontend:

```bash
npm run dev
```

Buka aplikasi:

```text
http://localhost:5173
```

## Notes for Restricted Devices

Jika perangkat tidak dapat menginstall Node.js/npm secara system-wide, frontend dapat dijalankan menggunakan Node.js portable ZIP. Setelah ZIP diekstrak, tambahkan folder Node ke `PATH` hanya untuk terminal aktif.

Contoh Windows PowerShell:

```powershell
$nodePath = "$env:USERPROFILE\Downloads\node-v24.16.0-win-x64\node-v24.16.0-win-x64"
$env:Path = "$nodePath;$env:Path"

node -v
npm.cmd -v
```

Gunakan `npm.cmd` jika PowerShell memblokir `npm.ps1`:

```powershell
npm.cmd install
npm.cmd run dev
```

## Deployment

### Frontend Deployment

Frontend di-deploy ke Vercel.

Vercel project setting:

```text
Framework Preset : Vite
Root Directory   : fullstack-app/frontend
Install Command  : npm install
Build Command    : npm run build
Output Directory : dist
```

Vercel environment variable:

```env
VITE_API_URL=https://uliviaembun-cardioguard-api.hf.space
```

### AI API Deployment

AI API di-deploy ke Hugging Face Spaces sebagai Docker Space.

Hugging Face Space:

```text
https://huggingface.co/spaces/uliviaembun/cardioguard-api
```

Production API URL:

```text
https://uliviaembun-cardioguard-api.hf.space
```

Required Hugging Face variables & secrets:

```env
GEMINI_API_KEY=gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://www.cardioguard.my.id,https://cardioguard.my.id
TF_CPP_MIN_LOG_LEVEL=2
```

Docker Space uses:

```text
ai-engineering/Dockerfile
```

with exposed port:

```text
7860
```

## Testing the Hosted API

Test health endpoint:

```text
https://uliviaembun-cardioguard-api.hf.space/health
```

Test prediction endpoint using curl:

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

## Environment Files

File `.env` tidak disimpan ke repository.

### `ai-engineering/.env`

```env
GEMINI_API_KEY=gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
TF_CPP_MIN_LOG_LEVEL=2
```

### `fullstack-app/backend/.env`

```env
AI_API_URL=http://127.0.0.1:8001
AI_API_TIMEOUT=60
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### `fullstack-app/frontend/.env`

For hosted API:

```env
VITE_API_URL=https://uliviaembun-cardioguard-api.hf.space
```

For local backend:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Important Notes

* Production frontend is hosted on Vercel.
* Production API is hosted on Hugging Face Spaces.
* Production frontend directly calls Hugging Face API.
* Local backend proxy is available for development but is not required in production.
* Hugging Face Free CPU Space may sleep after a period of inactivity, so the first request after idle time can be slower.
* Gemini API is used only to generate explanation text, not to determine the model prediction.
* If Gemini API is unavailable, the system returns deterministic fallback explanation.

## Limitations

Beberapa keterbatasan CardioGuard:

* Prediksi bersifat estimasi risiko awal, bukan diagnosis medis.
* Data input masih terbatas pada fitur umum seperti tekanan darah, BMI, kolesterol, glukosa, dan gaya hidup.
* Model tidak menggunakan data klinis lanjutan seperti ECG, riwayat penyakit detail, atau hasil laboratorium lengkap.
* Hasil dapat berubah jika artifact model, threshold, atau input pengguna berubah.
* Penjelasan `ai_explanation` dapat berasal dari Gemini API atau fallback explanation.
* Free hosting dapat mengalami cold start setelah periode tidak aktif.

## Disclaimer

CardioGuard tidak memberikan diagnosis medis. Hasil prediksi hanya digunakan sebagai informasi awal untuk meningkatkan kesadaran pengguna terhadap faktor risiko penyakit kardiovaskular. Untuk evaluasi kesehatan yang lebih akurat, pengguna tetap disarankan berkonsultasi dengan tenaga medis profesional.
