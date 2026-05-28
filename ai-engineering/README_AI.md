# CardioGuard AI Engineering

Folder ini berisi pipeline AI untuk proyek CardioGuard, mulai dari training model, penyimpanan artifact, inference, sampai API prediksi risiko penyakit kardiovaskular.

Model digunakan untuk membantu skrining awal risiko berdasarkan fitur seperti usia, tinggi badan, berat badan, tekanan darah, kolesterol, glukosa, aktivitas fisik, kebiasaan merokok, dan konsumsi alkohol.

> Hasil prediksi dari model ini digunakan sebagai skrining awal dan edukasi kesehatan. Output model tidak ditujukan sebagai pengganti diagnosis dokter atau tenaga medis profesional.

---

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
- Generative AI explanation untuk membantu menjelaskan hasil prediksi secara natural kepada pengguna.

API inference utama hanya menggunakan satu endpoint:

```text
POST /predict
```

Endpoint ini mengembalikan hasil prediksi model, ringkasan kesehatan, disclaimer, dan `ai_explanation` dalam satu response sehingga mudah diintegrasikan dengan fullstack/frontend.

---

## Folder Structure

```text
ai-engineering/
├── app.py                         # FastAPI app untuk serving model
├── kaggle_train.py                # Script training via Kaggle
├── kernel-metadata.json           # Kaggle kernel metadata
├── requirements.txt               # Dependency AI
├── README_AI.md                   # Dokumentasi AI engineering
├── scripts/
│   ├── training_model.py          # Training pipeline
│   ├── inference.py               # Local inference dan model loading
│   └── genai_explainer.py         # Gemini/fallback explanation generator
├── models/
│   ├── cardioguard_model.keras
│   └── cardioguard_best_model.keras
├── artifacts/
│   ├── scaler.pkl                 # Scaler preprocessing
│   ├── feature_columns.json       # Daftar fitur yang digunakan model
│   ├── threshold.json             # Threshold klasifikasi
│   └── training_metrics.json      # Metrik hasil training
└── logs/
    └── fit/                       # TensorBoard logs
```

---

## Model Description

Model yang digunakan adalah neural network berbasis TensorFlow Keras Functional API. Input model berasal dari fitur numerik dan kategorikal sederhana yang berkaitan dengan risiko penyakit kardiovaskular.

Komponen utama yang digunakan:

- `RiskFeatureGate`: custom layer untuk membantu model memberi bobot adaptif pada fitur input;
- `cardio_guard_loss`: custom loss function untuk mendukung proses klasifikasi risiko;
- `CustomTrainingMonitor`: monitor training untuk menyimpan model terbaik berdasarkan performa validasi;
- custom training loop berbasis `tf.GradientTape`.

Output model berupa probabilitas risiko dalam rentang 0 sampai 1. Probabilitas tersebut dibandingkan dengan threshold yang disimpan pada folder `artifacts/` untuk menentukan kelas prediksi.

Selain output model utama, API juga menambahkan field siap pakai untuk frontend:

- `risk_label`
- `risk_color`
- `health_summary`
- `disclaimer`
- `ai_explanation`

---

## Input Features

Fitur utama yang diterima endpoint `/predict`:

| Feature | Description |
|---|---|
| `age_years` | Usia dalam tahun |
| `gender` | Encoding jenis kelamin, `1` = Wanita, `2` = Pria |
| `height` | Tinggi badan dalam cm |
| `weight` | Berat badan dalam kg |
| `ap_hi` | Tekanan darah sistolik |
| `ap_lo` | Tekanan darah diastolik |
| `cholesterol` | Kategori kadar kolesterol, `1` = Normal, `2` = Di atas normal, `3` = Jauh di atas normal |
| `gluc` | Kategori kadar glukosa, `1` = Normal, `2` = Di atas normal, `3` = Jauh di atas normal |
| `smoke` | Status merokok, `0` = Tidak, `1` = Ya |
| `alco` | Konsumsi alkohol, `0` = Tidak, `1` = Ya |
| `active` | Aktivitas fisik, `0` = Tidak aktif, `1` = Aktif |

Pipeline juga membuat fitur turunan, seperti BMI, kategori tekanan darah, pulse pressure, mean arterial pressure, indikator obesitas, indikator tekanan darah tinggi, indikator kolesterol tinggi, indikator glukosa tinggi, dan beberapa fitur interaksi.

---

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

---

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

---

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
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Jika dependency FastAPI, Uvicorn, python-dotenv, atau Gemini belum tersedia, install manual:

```bash
pip install fastapi uvicorn python-dotenv google-genai
```

---

## Environment Variables

Jika ingin memakai Gemini untuk membuat `ai_explanation`, buat file `.env` di folder `ai-engineering/`:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Jika `GEMINI_API_KEY` tidak tersedia, invalid, atau melewati limit, service tetap berjalan menggunakan fallback explanation berbasis aturan.

---

## Inference

Untuk mencoba inference tanpa menjalankan API:

```bash
python scripts/inference.py
```

Script inference akan memuat model, scaler, daftar fitur, dan threshold dari folder `models/` dan `artifacts/`.

---

## Running the AI API

Dari folder `ai-engineering`, jalankan:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8001
```

Untuk Windows PowerShell, jika ingin mengurangi log TensorFlow:

```powershell
$env:TF_CPP_MIN_LOG_LEVEL="2"
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

> Untuk AI API, disarankan tidak memakai `--reload` saat menjalankan service normal karena TensorFlow/model dapat ter-load lebih dari sekali dan membuat startup lebih lama.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Informasi singkat service |
| `GET` | `/health` | Mengecek status model dan artifact |
| `GET` | `/schema/frontend` | Menampilkan ringkasan contract request dan response |
| `POST` | `/predict` | Menghasilkan prediksi risiko, ringkasan kesehatan, disclaimer, dan `ai_explanation` |

---

## Example Request

Contoh request dan response dari endpoint `/predict`.

Endpoint ini sudah mengembalikan hasil prediksi, ringkasan kesehatan, disclaimer, dan `ai_explanation` dalam satu kali hit API.

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

---

## Generative AI Explanation

Fitur Generative AI Explanation digunakan untuk membuat penjelasan singkat yang lebih natural dan mudah dipahami pengguna. Penjelasan ini dikembalikan langsung melalui field `ai_explanation` pada response endpoint `/predict`.

Generative AI tidak menentukan hasil prediksi. Hasil prediksi tetap berasal dari model machine learning utama. LLM hanya membantu menyusun kalimat penjelasan berdasarkan output model, ringkasan kesehatan, dan faktor risiko input.

Flow explanation:

```text
Input user
   ↓
Model menghasilkan risk_probability, predicted_class, risk_label
   ↓
API membuat health_summary dan disclaimer
   ↓
Gemini menyusun ai_explanation
   ↓
Jika Gemini gagal, fallback explanation digunakan
```

Konfigurasi Gemini dilakukan melalui environment variable:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Jika API key tidak tersedia, invalid, atau sudah melewati limit free tier, sistem tetap mengembalikan `ai_explanation` dari fallback sehingga endpoint `/predict` tetap dapat digunakan.

---

## Fullstack Integration

Dalam aplikasi web, AI API tidak dipanggil langsung oleh frontend. Alur integrasinya:

```text
Frontend Web
   ↓
Fullstack Backend
   ↓
AI API /predict
```

Port lokal yang digunakan:

| Service | Port |
|---|---:|
| AI API | `8001` |
| Fullstack Backend | `8000` |
| Frontend | `5173` |

Backend fullstack mengarah ke AI API melalui environment variable:

```env
AI_API_URL=http://127.0.0.1:8001
```

Frontend mengarah ke backend fullstack melalui environment variable:

```env
VITE_API_URL=http://127.0.0.1:8000
```

---

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

---

## Evaluation Notes

Model dievaluasi menggunakan beberapa metrik, seperti accuracy, AUC, MAE berbasis probabilitas, dan MAE berbasis label hasil threshold.

Pada eksperimen terakhir, performa model belum mencapai target akurasi 85% dan MAE label 0,02. Hal ini dicatat sebagai keterbatasan eksperimen karena dataset yang digunakan merupakan data tabular dengan fitur klinis sederhana. Untuk konteks skrining awal, metrik seperti AUC, recall, precision, dan threshold selection tetap perlu dipertimbangkan bersama accuracy.

Detail metrik tersimpan di:

```text
artifacts/training_metrics.json
```

---

## Limitations

Beberapa keterbatasan modul ini:

- data input masih terbatas pada fitur umum;
- model tidak menggunakan data klinis lanjutan seperti ECG, riwayat penyakit detail, atau hasil pemeriksaan laboratorium lengkap;
- prediksi bersifat estimasi risiko awal;
- performa model dapat berubah jika distribusi data pengguna berbeda dari data training;
- `ai_explanation` bersifat penjelasan natural dan tidak mengubah hasil prediksi model.

---

## Disclaimer

CardioGuard tidak memberikan diagnosis medis. Hasil prediksi hanya digunakan sebagai informasi awal untuk meningkatkan kesadaran pengguna terhadap faktor risiko penyakit kardiovaskular. Untuk evaluasi kesehatan yang lebih akurat, pengguna tetap disarankan berkonsultasi dengan tenaga medis profesional.
