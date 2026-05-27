import { Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="text-center py-8 px-4 mt-8 border-t border-surface-800/60">
      <div className="flex items-center justify-center gap-1.5 text-surface-500 text-xs mb-2">
        <span>Built with</span>
        <Heart className="w-3 h-3 text-accent-500 animate-heartbeat" />
        <span>by</span>
        <span className="font-semibold text-surface-400">Tim CardioGuard</span>
      </div>

      <p className="text-surface-600 text-[11px] max-w-sm mx-auto leading-relaxed mb-3">
        Proyek Capstone — Prediksi Risiko Penyakit Kardiovaskular Berbasis AI.
        Tidak dimaksudkan sebagai pengganti konsultasi medis profesional.
      </p>

      <div className="flex items-center justify-center gap-4 text-surface-600 text-xs">
        <span>React + TailwindCSS</span>
        <span className="text-surface-700">•</span>
        <span>FastAPI + TensorFlow</span>
        <span className="text-surface-700">•</span>
        <span>v1.0.0</span>
      </div>
    </footer>
  );
}
