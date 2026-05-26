# CardioGuard AI Engineering

Modul ini berisi pipeline machine learning untuk mendukung fitur deteksi dini risiko penyakit kardiovaskular pada aplikasi CardioGuard. Model digunakan untuk menghasilkan estimasi risiko berdasarkan data fisik, tekanan darah, dan beberapa indikator gaya hidup pengguna.

> Hasil prediksi dari model ini digunakan sebagai skrining awal dan edukasi kesehatan. Output model tidak ditujukan sebagai pengganti diagnosis dokter atau tenaga medis profesional.

## Overview

CardioGuard AI dikembangkan sebagai modul backend untuk melakukan prediksi risiko penyakit kardiovaskular. Model dibangun menggunakan TensorFlow/Keras dan disajikan melalui REST API berbasis FastAPI.

Pipeline AI mencakup:

- preprocessing dan feature engineering;
- training model neural network;
- custom training loop menggunakan `tf.GradientTape`;
- custom layer dan custom loss function;
- penyimpanan model dalam format `.keras`;
- inference script untuk pengujian lokal;
- REST API untuk serving model;
- TensorBoard logging untuk monitoring training;
- optional generative AI explanation untuk membantu menjelaskan hasil prediksi.

## Folder Structure

```text
ai-engineering/
├── app.py
├── requirements.txt
├── README_AI.md
├── kaggle_train.py
├── scripts/
│   ├── training_model.py
│   ├── inference.py
│   └── genai_explainer.py
├── models/
│   ├── cardioguard_model.keras
│   └── cardioguard_best_model.keras
├── artifacts/
│   ├── scaler.pkl
│   ├── feature_columns.json
│   ├── threshold.json
│   └── training_metrics.json
└── logs/
    └── fit/
```

## Model Description

Model yang digunakan adalah neural network berbasis TensorFlow Keras Functional API. Input model berasal dari fitur numerik dan kategorikal sederhana yang berkaitan dengan risiko penyakit kardiovaskular.

Komponen utama yang digunakan:

- `RiskFeatureGate`: custom layer untuk membantu model memberi bobot adaptif pada fitur input;
- `cardio_guard_loss`: custom loss function untuk mendukung proses klasifikasi risiko;
- `CustomTrainingMonitor`: monitor training untuk menyimpan model terbaik berdasarkan performa validasi;
- custom training loop berbasis `tf.GradientTape`.

Output model berupa probabilitas risiko dalam rentang 0 sampai 1. Probabilitas tersebut dibandingkan dengan threshold yang disimpan pada folder `artifacts/` untuk menentukan label risiko.

## Input Features

Fitur utama yang digunakan model:

| Feature | Description |
|---|---|
| `gender` | Encoding jenis kelamin sesuai dataset |
| `height` | Tinggi badan dalam cm |
| `weight` | Berat badan dalam kg |
| `ap_hi` | Tekanan darah sistolik |
| `ap_lo` | Tekanan darah diastolik |
| `cholesterol` | Kategori kadar kolesterol |
| `gluc` | Kategori kadar glukosa |
| `smoke` | Status merokok |
| `alco` | Konsumsi alkohol |
| `active` | Status aktivitas fisik |
| `age_years` | Usia dalam tahun |

Pipeline juga membuat beberapa fitur turunan, seperti BMI, kategori tekanan darah, pulse pressure, mean arterial pressure, indikator obesitas, indikator tekanan darah tinggi, indikator kolesterol tinggi, indikator glukosa tinggi, dan beberapa fitur interaksi.

## Training

Training dilakukan melalui script berikut:

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

Setelah training selesai, model dan artifact akan disimpan ke beberapa folder utama.

### Models

```text
models/cardioguard_model.keras
models/cardioguard_best_model.keras
```

| File | Description |
|---|---|
| `cardioguard_model.keras` | Model pada epoch terakhir |
| `cardioguard_best_model.keras` | Model terbaik berdasarkan performa validasi |

Untuk inference dan API, model yang direkomendasikan adalah `cardioguard_best_model.keras`.

### Artifacts

```text
artifacts/scaler.pkl
artifacts/feature_columns.json
artifacts/threshold.json
artifacts/training_metrics.json
```

| Artifact | Description |
|---|---|
| `scaler.pkl` | Scaler untuk normalisasi fitur |
| `feature_columns.json` | Daftar fitur yang digunakan model |
| `threshold.json` | Threshold klasifikasi risiko |
| `training_metrics.json` | Ringkasan metrik hasil training |

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

## Inference

Untuk mencoba inference tanpa menjalankan API:

```bash
python scripts/inference.py
```

Script inference akan memuat model, scaler, daftar fitur, dan threshold dari folder `models/` dan `artifacts/`.

## Running the API

API dijalankan menggunakan FastAPI.

Dari folder `ai-engineering`, jalankan:

```bash
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Dokumentasi endpoint dapat dibuka di:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Informasi singkat service |
| `GET` | `/health` | Mengecek status model dan artifact |
| `POST` | `/predict` | Menghasilkan prediksi risiko |
| `POST` | `/explain` | Menghasilkan prediksi beserta penjelasan tambahan |

## Example Request

Contoh request ke endpoint `/predict`:

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

Contoh response:

```json
{
  "risk_probability": 0.390542,
  "risk_percent": 39.05,
  "threshold": 0.48,
  "predicted_class": 0,
  "risk_label": "sedang",
  "disclaimer": "Hasil ini adalah skrining risiko awal, bukan diagnosis medis."
}
```

## Generative AI Explanation

Endpoint `/explain` menyediakan penjelasan tambahan yang lebih mudah dibaca pengguna berdasarkan hasil prediksi model. Fitur ini bersifat opsional dan tidak memengaruhi output utama dari model prediksi.

Secara default, service tetap dapat berjalan tanpa API key menggunakan fallback explanation. Jika environment variable `OPENAI_API_KEY` tersedia, service akan menggunakan generative AI untuk membuat penjelasan yang lebih natural.

API key tidak disimpan di repository. Konfigurasi dilakukan melalui environment variable pada environment lokal atau deployment server.

Windows PowerShell:

```powershell
$env:OPENAI_MODEL="gpt-5.4-mini"
```

Linux/macOS:

```bash
export OPENAI_MODEL="gpt-5.4-mini"
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

Beberapa keterbatasan modul ini:

- data input masih terbatas pada fitur umum;
- model tidak menggunakan data klinis lanjutan seperti ECG, riwayat penyakit detail, atau hasil pemeriksaan laboratorium lengkap;
- prediksi bersifat estimasi risiko awal;
- performa model dapat berubah jika distribusi data pengguna berbeda dari data training.

## Disclaimer

CardioGuard tidak memberikan diagnosis medis. Hasil prediksi hanya digunakan sebagai informasi awal untuk meningkatkan kesadaran pengguna terhadap faktor risiko penyakit kardiovaskular. Untuk evaluasi kesehatan yang lebih akurat, pengguna tetap disarankan berkonsultasi dengan tenaga medis profesional.
