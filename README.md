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

## Disclaimer

CardioGuard tidak memberikan diagnosis medis. Hasil prediksi hanya digunakan sebagai informasi awal untuk meningkatkan kesadaran terhadap faktor risiko penyakit kardiovaskular.
