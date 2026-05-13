import { useState } from 'react'

function App() {
  // 1. State untuk menyimpan data ketikan user
  const [formData, setFormData] = useState({
    tinggi_badan: '',
    berat_badan: '',
    tensi_sistolik: '',
    tensi_diastolik: ''
  })

  // 2. State untuk menyimpan balasan dari Backend
  const [hasil, setHasil] = useState(null)
  const [loading, setLoading] = useState(false)

  // 3. Fungsi untuk menangkap ketikan di form
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  // 4. Fungsi untuk mengirim data ke API saat tombol diklik
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Mengirim POST request ke URL FastAPI kita
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // Memastikan tipe datanya adalah angka (float)
        body: JSON.stringify({
          tinggi_badan: parseFloat(formData.tinggi_badan),
          berat_badan: parseFloat(formData.berat_badan),
          tensi_sistolik: parseFloat(formData.tensi_sistolik),
          tensi_diastolik: parseFloat(formData.tensi_diastolik)
        })
      })

      const data = await response.json()
      setHasil(data) // Menyimpan balasan dari API ke layar
    } catch (error) {
      console.error("Error:", error)
      alert("Gagal terhubung ke Backend. Pastikan Uvicorn FastAPI sedang menyala!")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      
      <div className="max-w-lg w-full bg-white p-8 rounded-2xl shadow-xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">CardioGuard</h1>
          <p className="text-gray-500 mt-2 text-sm">
            Deteksi Dini Risiko Penyakit Jantung Terintegrasi AI
          </p>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          
          <div className="flex gap-4">
            <div className="w-1/2">
              <label className="block text-sm font-semibold text-gray-700 mb-1">Tinggi Badan (cm)</label>
              <input 
                type="number" 
                name="tinggi_badan"
                value={formData.tinggi_badan}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" 
                placeholder="Misal: 170" 
              />
            </div>
            <div className="w-1/2">
              <label className="block text-sm font-semibold text-gray-700 mb-1">Berat Badan (kg)</label>
              <input 
                type="number" 
                name="berat_badan"
                value={formData.berat_badan}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" 
                placeholder="Misal: 65" 
              />
            </div>
          </div>

          <div className="flex gap-4">
            <div className="w-1/2">
              <label className="block text-sm font-semibold text-gray-700 mb-1">Tensi Sistolik</label>
              <input 
                type="number" 
                name="tensi_sistolik"
                value={formData.tensi_sistolik}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 outline-none" 
                placeholder="Misal: 120" 
              />
            </div>
            <div className="w-1/2">
              <label className="block text-sm font-semibold text-gray-700 mb-1">Tensi Diastolik</label>
              <input 
                type="number" 
                name="tensi_diastolik"
                value={formData.tensi_diastolik}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-blue-500 outline-none" 
                placeholder="Misal: 80" 
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className={`w-full mt-6 text-white font-bold py-3 px-4 rounded-lg shadow-md transition-all duration-200 ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {loading ? 'Menganalisis...' : 'Analisis Risiko dengan AI'}
          </button>

        </form>

        {/* 5. Tampilan Hasil Prediksi dari Backend */}
        {hasil && (
          <div className={`mt-8 p-4 rounded-lg border text-center ${hasil.prediksi_ai.risiko_tinggi ? 'bg-red-50 border-red-200 text-red-700' : 'bg-green-50 border-green-200 text-green-700'}`}>
            <h3 className="font-bold text-lg mb-1">Hasil Analisis</h3>
            <p className="font-medium">{hasil.prediksi_ai.pesan}</p>
            <p className="text-sm mt-2 opacity-80">
              Kalkulasi BMI Otomatis: <span className="font-bold">{hasil.hasil_kalkulasi.bmi_otomatis}</span>
            </p>
          </div>
        )}

      </div>
    </div>
  )
}

export default App