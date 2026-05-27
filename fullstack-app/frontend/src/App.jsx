import { useState, useRef } from "react";
import { AlertCircle, X } from "lucide-react";

import { predictRisk } from "./api";
import Header from "./components/Header";
import PredictionForm from "./components/PredictionForm";
import ResultCard from "./components/ResultCard";
import DashboardSummary from "./components/DashboardSummary";
import Footer from "./components/Footer";

export default function App() {
  const [result, setResult] = useState(null);
  const [patientData, setPatientData] = useState(null);
  const [analysisTime, setAnalysisTime] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const resultRef = useRef(null);

  // ---- Submit handler ----
  const handleSubmit = async (payload) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setPatientData(null);

    try {
      const data = await predictRisk(payload);
      setResult(data);
      setPatientData(payload);

      // Capture current formatted date/time in Indonesian locale
      const now = new Date();
      const formattedDate = now.toLocaleDateString("id-ID", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      });
      const formattedTime = now.toLocaleTimeString("id-ID", {
        hour: "2-digit",
        minute: "2-digit",
      }) + " WIB";
      setAnalysisTime(`${formattedDate}, ${formattedTime}`);

      // Smooth scroll to result
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 200);
    } catch (err) {
      console.error("Prediction error:", err);

      if (err.response) {
        // Server responded with error
        const detail = err.response.data?.detail || "Terjadi kesalahan pada server.";
        setError(`Error ${err.response.status}: ${detail}`);
      } else if (err.request) {
        // No response received
        setError(
          "Tidak dapat terhubung ke server. Pastikan backend FastAPI berjalan di http://127.0.0.1:8000"
        );
      } else {
        setError(`Terjadi kesalahan: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  // ---- Reset handler ----
  const handleReset = () => {
    setResult(null);
    setPatientData(null);
    setAnalysisTime("");
    setError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <>
      {/* Screen View (Hidden when printing) */}
      <div className="print:hidden gradient-bg min-h-screen flex flex-col">
        {/* Main content */}
        <main className="flex-1 w-full max-w-2xl mx-auto px-4 pb-4">
          <Header />

          {/* Error banner */}
          {error && (
            <div className="mb-6 flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl animate-fade-in">
              <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-red-300 font-medium">Gagal Menganalisis</p>
                <p className="text-xs text-red-400/80 mt-1">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-400/60 hover:text-red-300 transition-colors"
                aria-label="Tutup error"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Form */}
          <PredictionForm onSubmit={handleSubmit} loading={loading} />

          {/* Results */}
          {result && (
            <div ref={resultRef} className="mt-8 space-y-6">
              <ResultCard result={result} onReset={handleReset} />
              <DashboardSummary summary={result.health_summary} />
            </div>
          )}
        </main>

        <Footer />
      </div>

      {/* Printable Report View (Visible only during printing) */}
      {result && patientData && (
        <div className="hidden print:block bg-white text-slate-900 p-12 max-w-4xl mx-auto font-sans leading-relaxed text-sm">
          {/* Logo / Header Section */}
          <div className="flex justify-between items-center border-b-2 border-slate-900 pb-4 mb-6">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">♥</span>
                </div>
                <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
                  Cardio<span className="text-primary-600">Guard</span>
                </h1>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                AI-Powered Cardiovascular Risk Screening System
              </p>
            </div>
            <div className="text-right">
              <h2 className="text-lg font-bold text-slate-800 uppercase tracking-wide">
                Laporan Screening Kesehatan
              </h2>
              <p className="text-xs text-slate-500">ID Laporan: CG-{Math.floor(100000 + Math.random() * 900000)}</p>
            </div>
          </div>

          {/* Patient Details & Time Section */}
          <div className="grid grid-cols-2 gap-6 mb-6 bg-slate-50 p-4 rounded-xl border border-slate-200">
            <div>
              <h3 className="font-bold text-slate-800 mb-2 border-b border-slate-200 pb-1 text-xs uppercase tracking-wider">
                Biodata Pasien
              </h3>
              <table className="w-full text-xs">
                <tbody>
                  <tr>
                    <td className="font-semibold text-slate-500 py-1 w-24">Umur</td>
                    <td className="text-slate-800 py-1">: {patientData.age_years} Tahun</td>
                  </tr>
                  <tr>
                    <td className="font-semibold text-slate-500 py-1">Jenis Kelamin</td>
                    <td className="text-slate-800 py-1">
                      : {patientData.gender === 2 ? "Pria" : "Wanita"}
                    </td>
                  </tr>
                  <tr>
                    <td className="font-semibold text-slate-500 py-1">Tinggi / Berat</td>
                    <td className="text-slate-800 py-1">
                      : {patientData.height} cm / {patientData.weight} kg
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div>
              <h3 className="font-bold text-slate-800 mb-2 border-b border-slate-200 pb-1 text-xs uppercase tracking-wider">
                Informasi Pemeriksaan
              </h3>
              <table className="w-full text-xs">
                <tbody>
                  <tr>
                    <td className="font-semibold text-slate-500 py-1 w-24">Waktu Analisis</td>
                    <td className="text-slate-800 py-1">: {analysisTime}</td>
                  </tr>
                  <tr>
                    <td className="font-semibold text-slate-500 py-1">Metode</td>
                    <td className="text-slate-800 py-1">: TensorFlow Deep Learning</td>
                  </tr>
                  <tr>
                    <td className="font-semibold text-slate-500 py-1">Status Sistem</td>
                    <td className="text-emerald-700 font-medium py-1">: Siap / Optimal</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Prediction Result Section */}
          <div className={`mb-6 p-6 rounded-xl border-2 ${
            result.risk_label === "tinggi"
              ? "bg-red-50 border-red-500 text-red-900"
              : result.risk_label === "sedang"
                ? "bg-yellow-50 border-yellow-500 text-yellow-900"
                : "bg-green-50 border-green-500 text-green-900"
          }`}>
            <h3 className="text-base font-bold uppercase tracking-wide mb-2">
              Hasil Deteksi Risiko Kardiovaskular
            </h3>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm">
                  Berdasarkan model klasifikasi deep learning CardioGuard, tingkat risiko Anda dikategorikan sebagai:
                </p>
                <p className="text-xl font-black uppercase mt-1">
                  RISIKO {result.risk_label}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs uppercase font-semibold text-slate-500">Probabilitas Risiko</p>
                <p className="text-3xl font-extrabold">{result.risk_percent}%</p>
              </div>
            </div>
          </div>

          {/* Detailed Health Summary */}
          <div className="mb-6">
            <h3 className="font-bold text-slate-800 mb-3 uppercase tracking-wide border-b border-slate-300 pb-1 text-xs">
              Hasil Pengukuran Kesehatan Utama
            </h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="border border-slate-200 rounded-xl p-4 text-center bg-slate-50">
                <p className="text-xs font-semibold text-slate-500 uppercase">Indeks Massa Tubuh (BMI)</p>
                <p className="text-xl font-bold text-slate-800 my-1">{result.health_summary.bmi}</p>
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-200 font-medium text-slate-700">
                  {result.health_summary.bmi_category}
                </span>
              </div>
              <div className="border border-slate-200 rounded-xl p-4 text-center bg-slate-50">
                <p className="text-xs font-semibold text-slate-500 uppercase">Tekanan Darah</p>
                <p className="text-xl font-bold text-slate-800 my-1">
                  {result.health_summary.blood_pressure.replace(" mmHg", "")}
                </p>
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-200 font-medium text-slate-700">
                  {result.health_summary.bp_status}
                </span>
              </div>
              <div className="border border-slate-200 rounded-xl p-4 text-center bg-slate-50">
                <p className="text-xs font-semibold text-slate-500 uppercase">Gaya Hidup & Kebiasaan</p>
                <p className="text-xl font-bold text-slate-800 my-1">
                  {result.health_summary.lifestyle_risk_score}/3
                </p>
                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-200 font-medium text-slate-700">
                  Skor {result.health_summary.lifestyle_risk_label}
                </span>
              </div>
            </div>
          </div>

          {/* Recommendations / Advice */}
          <div className="mb-8 p-4 border border-slate-200 rounded-xl bg-slate-50/50">
            <h3 className="font-bold text-slate-800 mb-2 uppercase tracking-wide text-xs">
              Rekomendasi Tindakan Medis
            </h3>
            <p className="text-xs text-slate-700 leading-relaxed">
              {result.risk_label === "tinggi"
                ? "SANGAT DISARANKAN untuk segera berkonsultasi dengan dokter spesialis jantung atau layanan medis terdekat. Batasi aktivitas fisik berat secara mendadak sebelum berkonsultasi, kendalikan pola makan secara ketat, dan lakukan pemeriksaan penunjang (EKG/Ekokardiografi)."
                : result.risk_label === "sedang"
                  ? "Disarankan untuk melakukan perbaikan gaya hidup, membatasi konsumsi lemak jenuh/garam, berolahraga secara teratur, memantau tekanan darah mandiri secara rutin, dan merencanakan konsultasi dengan dokter umum/spesialis penyakit dalam."
                  : "Pertahankan gaya hidup sehat yang aktif secara fisik (minimal 150 menit per minggu), konsumsi makanan padat nutrisi rendah kolesterol, pertahankan berat badan ideal, dan lakukan pemeriksaan skrining berkala secara berkala."}
            </p>
          </div>

          {/* Footer Disclaimer & Signatures */}
          <div className="grid grid-cols-3 gap-6 items-end mt-12 pt-6 border-t border-slate-200">
            <div className="col-span-2">
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                Catatan Hukum & Medis
              </h4>
              <p className="text-[9px] text-slate-400 leading-normal">
                {result.disclaimer}
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-slate-400 mb-12">Tanda Tangan Pemeriksa</p>
              <div className="w-32 mx-auto border-b border-slate-400" />
              <p className="text-[10px] font-bold text-slate-600 mt-1">CardioGuard AI Assessor</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}