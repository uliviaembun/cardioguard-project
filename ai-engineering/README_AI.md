# CardioGuard AI Engineering

Modul ini berisi pipeline machine learning untuk mendukung fitur deteksi dini risiko penyakit kardiovaskular pada aplikasi CardioGuard. Model digunakan untuk menghasilkan estimasi risiko berdasarkan data fisik, tekanan darah, dan beberapa indikator gaya hidup pengguna.

> Catatan: hasil prediksi dari model ini digunakan sebagai skrining awal dan edukasi kesehatan. Output model tidak ditujukan sebagai pengganti diagnosis dokter atau tenaga medis profesional.

## Overview

CardioGuard AI dikembangkan sebagai modul backend untuk melakukan prediksi risiko penyakit kardiovaskular. Model dibangun menggunakan TensorFlow/Keras dan disajikan melalui REST API berbasis FastAPI.

Pipeline AI mencakup beberapa bagian utama:

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

Beberapa komponen utama yang digunakan:

- `RiskFeatureGate`: custom layer untuk membantu model memberi bobot adaptif pada fitur input;
- `cardio_guard_loss`: custom loss function untuk mendukung proses klasifikasi risiko;
- `CustomTrainingMonitor`: monitor training untuk menyimpan model terbaik berdasarkan performa validasi;
- custom training loop berbasis `tf.GradientTape`.

Output model berupa probabilitas risiko dalam rentang 0 sampai 1. Probabilitas tersebut kemudian dibandingkan dengan threshold yang disimpan pada folder `artifacts/` untuk menentukan label risiko.

## Input Features

Fitur utama yang digunakan oleh model:

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
| `active` | Aktivitas fisik |
| `age_years` | Usia dalam tahun |

Selain fitur utama, pipeline training juga membuat beberapa fitur turunan, seperti:

- BMI;
- kategori tekanan darah;
- pulse pressure;
- mean arterial pressure;
- indikator obesitas;
- indikator tekanan darah tinggi;
- indikator kolesterol tinggi;
- indikator glukosa tinggi;
- fitur interaksi antara usia, BMI, tekanan darah, dan kolesterol.

Feature engineering ini dilakukan untuk menambah sinyal prediktif dari data tabular yang tersedia.

## Training Pipeline

Training dilakukan melalui script:

```bash
python scripts/training_model.py
```

Contoh command training:

```bash
python scripts/training_model.py --rebuild-data --epochs 40 --batch-size 128 --learning-rate 0.001
```

Parameter yang umum digunakan:

| Parameter | Description |
|---|---|
| `--rebuild-data` | Menjalankan ulang proses data preparation |
| `--epochs` | Jumlah epoch training |
| `--batch-size` | Ukuran batch |
| `--learning-rate` | Learning rate optimizer |

Training pipeline akan menyimpan beberapa output utama:

```text
models/
artifacts/
logs/
```

## Training Output

Setelah training selesai, model dan artifact akan disimpan ke folder berikut:

### Models

```text
models/cardioguard_model.keras
models/cardioguard_best_model.keras
```

Perbedaan kedua file tersebut:

| File | Description |
|---|---|
| `cardioguard_model.keras` | Model pada epoch terakhir |
| `cardioguard_best_model.keras` | Model terbaik berdasarkan performa validasi |

Untuk inference dan API, model yang direkomendasikan adalah:

```text
models/cardioguard_best_model.keras
```

karena model tersebut merupakan checkpoint terbaik selama proses training.

### Artifacts

```text
artifacts/scaler.pkl
artifacts/feature_columns.json
artifacts/threshold.json
artifacts/training_metrics.json
```

Keterangan:

| Artifact | Description |
|---|---|
| `scaler.pkl` | Scaler yang digunakan untuk normalisasi fitur |
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

## Running Inference Locally

Untuk mencoba inference tanpa menjalankan API:

```bash
python scripts/inference.py
```

Script inference akan memuat:

- model dari folder `models/`;
- scaler dari folder `artifacts/`;
- daftar fitur dari `feature_columns.json`;
- threshold dari `threshold.json`.

Output inference berupa probabilitas risiko, label risiko, dan level risiko.

## Running the API

API dijalankan menggunakan FastAPI.

Dari folder `ai-engineering`, jalankan:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Setelah API berjalan, dokumentasi endpoint dapat dibuka di:

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
  "risk_probability": 0.42,
  "risk_label": 0,
  "risk_level": "low",
  "threshold": 0.48
}
```

## Generative AI Explanation

Endpoint `/explain` dapat menggunakan generative AI untuk membuat penjelasan yang lebih mudah dipahami pengguna. Fitur ini bersifat opsional dan digunakan sebagai tambahan, bukan sebagai bagian utama dari prediksi model.

Jika API key tidak tersedia, service tetap dapat berjalan menggunakan fallback explanation.

Contoh konfigurasi environment variable.

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key"
$env:OPENAI_MODEL="gpt-5.4-mini"
```

Linux/macOS:

```bash
export OPENAI_API_KEY="your_api_key"
export OPENAI_MODEL="gpt-5.4-mini"
```

## Kaggle Training

Training model dilakukan di Kaggle untuk memanfaatkan GPU.

Script yang digunakan:

```text
kaggle_train.py
```

Script ini melakukan clone repository dari branch feat/ai-model, menjalankan training, lalu menyimpan output training pada environment Kaggle.


## Evaluation Notes

Model dievaluasi menggunakan beberapa metrik:

- accuracy;
- AUC;
- MAE berbasis probabilitas;
- MAE berbasis label hasil threshold.

Karena dataset yang digunakan merupakan data tabular dengan fitur klinis sederhana, performa model sangat dipengaruhi oleh kualitas fitur, noise data, dan keterbatasan informasi medis yang tersedia. Dalam konteks deteksi dini, metrik seperti AUC, recall, precision, dan threshold selection perlu dipertimbangkan bersama accuracy.

## Limitations

Beberapa keterbatasan modul ini:

- data input masih terbatas pada fitur umum;
- model tidak menggunakan data klinis lanjutan seperti ECG, riwayat penyakit detail, atau hasil pemeriksaan laboratorium lengkap;
- prediksi bersifat estimasi risiko awal;
- performa model dapat berubah jika distribusi data pengguna berbeda dari data training.

## Disclaimer

CardioGuard tidak memberikan diagnosis medis. Hasil prediksi hanya digunakan sebagai informasi awal untuk meningkatkan kesadaran pengguna terhadap faktor risiko penyakit kardiovaskular. Untuk evaluasi kesehatan yang lebih akurat, pengguna tetap disarankan berkonsultasi dengan tenaga medis profesional.
