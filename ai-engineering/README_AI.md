# CardioGuard AI Engineering

## Yang dipenuhi

- Deep Learning TensorFlow Functional API
- Custom Layer: `RiskFeatureGate`
- Custom Loss Function: `cardio_guard_loss`
- Custom Callback-like monitor: `CustomTrainingMonitor`
- Full custom training + evaluation loop dengan `tf.GradientTape`
- TensorBoard logging di `ai-engineering/logs/fit/...`
- Export model `.keras`
- Inference script
- REST API FastAPI
- Optional Generative AI explanation via OpenAI API

## Struktur file

```text
ai-engineering/
├── app.py
├── requirements.txt
├── scripts/
│   ├── training_model.py
│   ├── inference.py
│   └── genai_explainer.py
├── models/
├── artifacts/
└── logs/
```

## Setup

```bash
cd ai-engineering
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
```

## Train model

Jalankan dari folder `ai-engineering` atau root repo:

```bash
python scripts/training_model.py --rebuild-data --epochs 80 --batch-size 64
```

Output utama:

```text
ai-engineering/models/cardioguard_model.keras
ai-engineering/models/cardioguard_best_model.keras
ai-engineering/artifacts/scaler.pkl
ai-engineering/artifacts/feature_columns.json
ai-engineering/artifacts/threshold.json
ai-engineering/artifacts/training_metrics.json
ai-engineering/logs/fit/...
```

## TensorBoard

```bash
tensorboard --logdir logs
```

Buka URL yang muncul di terminal, biasanya `http://localhost:6006`.

## Coba inference lokal

```bash
python scripts/inference.py
```

## Jalankan API

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Buka:

```text
http://127.0.0.1:8000/docs
```

Contoh body untuk `/predict`:

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

## Optional Generative AI

Set environment variable:

```bash
set OPENAI_API_KEY=isi_api_key_kamu
set OPENAI_MODEL=gpt-5.4-mini
```

Lalu panggil endpoint `/explain`.
