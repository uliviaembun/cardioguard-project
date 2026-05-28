# CardioGuard

CardioGuard adalah aplikasi web berbasis AI untuk membantu skrining awal risiko penyakit kardiovaskular. Aplikasi ini menerima data kesehatan dasar pengguna, seperti usia, tinggi badan, berat badan, tekanan darah, kolesterol, gula darah, aktivitas fisik, kebiasaan merokok, dan konsumsi alkohol. Berdasarkan data tersebut, sistem memberikan estimasi tingkat risiko kardiovaskular, ringkasan kesehatan, serta penjelasan singkat yang mudah dipahami pengguna.

> CardioGuard bukan alat diagnosis medis. Hasil prediksi hanya digunakan sebagai skrining awal dan edukasi kesehatan. Untuk evaluasi kesehatan yang akurat, pengguna tetap disarankan berkonsultasi dengan dokter atau tenaga medis profesional.

## Overview

Penyakit kardiovaskular merupakan salah satu masalah kesehatan serius yang sering kali berkaitan dengan faktor risiko seperti tekanan darah tinggi, obesitas, kolesterol tinggi, gula darah tinggi, kebiasaan merokok, konsumsi alkohol, dan kurangnya aktivitas fisik.

CardioGuard dikembangkan untuk membantu pengguna memahami faktor risiko dasar secara lebih mudah melalui aplikasi web yang interaktif. Sistem ini menggabungkan model deep learning untuk prediksi risiko dan Gemini API sebagai Large Language Model (LLM) untuk menghasilkan penjelasan singkat yang lebih natural bagi pengguna.

Secara umum, CardioGuard terdiri dari tiga bagian utama:

* Frontend web untuk input data dan visualisasi hasil.
* Backend sebagai API gateway untuk frontend.
* AI API untuk menjalankan model TensorFlow dan menghasilkan `ai_explanation` dari LLM (Gemini Flash).

## Main Features

Fitur utama CardioGuard:

* Form input data kesehatan pengguna.
* Prediksi risiko penyakit kardiovaskular berbasis model AI.
* Kategori risiko: rendah, sedang, dan tinggi.
* Ringkasan kesehatan berupa BMI, kategori BMI, tekanan darah, dan risiko gaya hidup.
* Penjelasan hasil prediksi menggunakan Gemini API sebagai LLM.
* Fallback explanation jika Gemini API tidak tersedia atau mengalami error.
* Tampilan web interaktif untuk melihat hasil skrining.
* Backend API yang terpisah dari AI API agar integrasi lebih modular.

## System Architecture

Arsitektur aplikasi dibuat terpisah agar frontend, backend, dan AI service dapat dikembangkan secara independen.

```text
Frontend Web
    ↓
Backend
    ↓
AI API
    ↓
TensorFlow Model + Gemini API
```

Port lokal yang digunakan:

| Service           | URL                     | Description                              |
| ----------------- | ----------------------- | ---------------------------------------- |
| Frontend          | `http://127.0.0.1:5173` | Tampilan web CardioGuard                 |
| Fullstack Backend | `http://127.0.0.1:8000` | API yang diakses frontend                |
| AI API            | `http://127.0.0.1:8001` | Service AI untuk prediksi dan penjelasan |

## API Flow

Alur request saat user submit form:

```text
User mengisi form di frontend
        ↓
Frontend POST http://127.0.0.1:8000/predict
        ↓
Backend meneruskan request ke AI API
        ↓
AI API POST http://127.0.0.1:8001/predict
        ↓
AI API menjalankan model TensorFlow untuk prediksi risiko
        ↓
AI API menggunakan Gemini API sebagai LLM untuk membuat ai_explanation
        ↓
Jika Gemini API tidak tersedia/error, AI API menggunakan fallback explanation
        ↓
AI API mengembalikan prediksi + health_summary + disclaimer + ai_explanation
        ↓
Backend meneruskan response ke frontend
        ↓
Frontend menampilkan hasil analisis ke user
```

## Repository Structure

```text
cardioguard-project/
├── ai-engineering/
│   ├── app.py
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
│   │   ├── requirements.txt
│   │   └── .env
│   └── frontend/
│       ├── src/
│       ├── package.json
│       └── .env
│
├── data-science/
├── data/
├── docs/
└── README.md
```

## Tech Stack

| Layer           | Technology                              |
| --------------- | --------------------------------------- |
| Frontend        | React, Vite                             |
| Backend         | FastAPI, HTTPX                          |
| AI API          | FastAPI, TensorFlow/Keras               |
| Model Serving   | TensorFlow/Keras `.keras` model         |
| LLM Explanation | Gemini API                              |
| Data Processing | NumPy, Pandas, Scikit-learn             |
| Environment     | Python virtual environment, Node.js/npm |

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
  "ai_explanation": "Hasil skrining CardioGuard Anda menunjukkan kategori risiko tinggi dengan persentase 84.9%. Hal ini dipengaruhi oleh beberapa faktor, terutama tekanan darah, BMI, dan gaya hidup. Hasil ini hanya skrining awal dan bukan diagnosis medis."
}
```

## Local Setup

Aplikasi dijalankan menggunakan tiga service berbeda:

```text
AI API              → port 8001
Fullstack Backend   → port 8000
Frontend            → port 5173
```

Disarankan menggunakan virtual environment terpisah untuk `ai-engineering` dan `fullstack-app/backend`.

## 1. Run AI API

Masuk ke folder AI:

```bash
cd ai-engineering
```

Buat dan aktifkan virtual environment:

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
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
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

## 2. Run Fullstack Backend

Masuk ke folder backend:

```bash
cd fullstack-app/backend
```

Buat dan aktifkan virtual environment:

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

## 3. Run Frontend

Masuk ke folder frontend:

```bash
cd fullstack-app/frontend
```

Install dependency:

```bash
npm install
```

Buat file `.env` di folder `fullstack-app/frontend/`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Jalankan frontend:

```bash
npm run dev
```

Buka aplikasi di browser:

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

## Running Order Summary

Gunakan tiga terminal terpisah.

### Terminal 1 — AI API

```bash
cd ai-engineering
python -m uvicorn app:app --host 0.0.0.0 --port 8001
```

### Terminal 2 — Backend

```bash
cd fullstack-app/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3 — Frontend

```bash
cd fullstack-app/frontend
npm run dev
```

Akses aplikasi melalui:

```text
http://localhost:5173
```

## Testing the Integration

Test backend prediction endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
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

Jika integrasi berhasil, response akan memiliki field:

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
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

### `fullstack-app/backend/.env`

```env
AI_API_URL=http://127.0.0.1:8001
AI_API_TIMEOUT=60
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### `fullstack-app/frontend/.env`

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Limitations

Beberapa keterbatasan CardioGuard:

* Prediksi bersifat estimasi risiko awal, bukan diagnosis medis.
* Data input masih terbatas pada fitur umum seperti tekanan darah, BMI, kolesterol, glukosa, dan gaya hidup.
* Model tidak menggunakan data klinis lanjutan seperti ECG, riwayat penyakit detail, atau hasil laboratorium lengkap.
* Hasil dapat berubah jika artifact model, threshold, atau input pengguna berubah.
* Penjelasan `ai_explanation` dapat berasal dari Gemini API atau fallback explanation.

## Disclaimer

CardioGuard tidak memberikan diagnosis medis. Hasil prediksi hanya digunakan sebagai informasi awal untuk meningkatkan kesadaran pengguna terhadap faktor risiko penyakit kardiovaskular. Untuk evaluasi kesehatan yang lebih akurat, pengguna tetap disarankan berkonsultasi dengan tenaga medis profesional.
