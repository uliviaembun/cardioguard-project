from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Konfigurasi CORS agar Frontend (port 5173) diizinkan mengirim data ke Backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Dalam tahap development, kita izinkan semua
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Membuat struktur data yang diharapkan dari Frontend
class PatientData(BaseModel):
    tinggi_badan: float
    berat_badan: float
    tensi_sistolik: float
    tensi_diastolik: float

@app.get("/")
def read_root():
    return {"message": "CardioGuard API is running!"}

@app.post("/predict")
def predict_cardio(data: PatientData):
    # 1. Menghitung BMI secara otomatis di backend
    tinggi_m = data.tinggi_badan / 100
    bmi = round(data.berat_badan / (tinggi_m ** 2), 2)
    
    # 2. (DUMMY LOGIC) Nanti di sini kita akan me-load model AI TensorFlow (model.predict)
    # Untuk sementara, kita buat logika sederhana:
    # Jika BMI > 25 atau Tensi > 130/80, kita anggap Berisiko
    berisiko = False
    if bmi > 25 or data.tensi_sistolik > 130 or data.tensi_diastolik > 80:
        berisiko = True

    # 3. Mengembalikan hasil ke Frontend
    return {
        "status": "success",
        "input_diterima": data,
        "hasil_kalkulasi": {
            "bmi_otomatis": bmi
        },
        "prediksi_ai": {
            "risiko_tinggi": berisiko,
            "pesan": "Risiko Penyakit Jantung Tinggi!" if berisiko else "Risiko Penyakit Jantung Rendah, tetap jaga kesehatan!"
        }
    }