import { useEffect, useState, useRef } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  TrendingUp,
  AlertTriangle,
  Info,
  RotateCcw,
  Printer,
} from "lucide-react";

// ---------- Animated percentage counter ----------

function AnimatedPercent({ value }) {
  const [display, setDisplay] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    let start = 0;
    const end = value;
    const duration = 1200;
    const startTime = performance.now();

    const step = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // easeOutCubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * eased;
      setDisplay(current);
      if (progress < 1) ref.current = requestAnimationFrame(step);
    };

    ref.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(ref.current);
  }, [value]);

  return <span>{display.toFixed(1)}%</span>;
}

// ---------- Risk gauge ring ----------

function RiskGauge({ percent, color }) {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const [offset, setOffset] = useState(circumference);

  useEffect(() => {
    const timer = setTimeout(() => {
      setOffset(circumference - (percent / 100) * circumference);
    }, 200);
    return () => clearTimeout(timer);
  }, [percent, circumference]);

  const strokeColor =
    color === "green"
      ? "#22c55e"
      : color === "yellow"
        ? "#eab308"
        : "#ef4444";

  const glowFilter =
    color === "green"
      ? "drop-shadow(0 0 8px rgba(34,197,94,0.4))"
      : color === "yellow"
        ? "drop-shadow(0 0 8px rgba(234,179,8,0.4))"
        : "drop-shadow(0 0 8px rgba(239,68,68,0.4))";

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="170" height="170" className="-rotate-90">
        {/* Background track */}
        <circle
          cx="85"
          cy="85"
          r={radius}
          fill="none"
          stroke="rgba(148,163,184,0.1)"
          strokeWidth="10"
        />
        {/* Animated arc */}
        <circle
          cx="85"
          cy="85"
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: "stroke-dashoffset 1.2s cubic-bezier(0.25,0.46,0.45,0.94)",
            filter: glowFilter,
          }}
        />
      </svg>
      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-extrabold text-white">
          <AnimatedPercent value={percent} />
        </span>
        <span className="text-xs text-surface-400 font-medium mt-0.5">
          Probabilitas Risiko
        </span>
      </div>
    </div>
  );
}

// ---------- Main ResultCard ----------

const RISK_CONFIG = {
  rendah: {
    Icon: ShieldCheck,
    gradient: "from-green-500/20 to-emerald-600/20",
    border: "border-green-500/30",
    glow: "glow-green",
    badge: "bg-green-500/20 text-green-400 border-green-500/30",
    title: "Risiko Rendah",
    description:
      "Berdasarkan data yang dimasukkan, model AI menunjukkan bahwa risiko penyakit kardiovaskular Anda berada pada tingkat rendah. Tetap pertahankan gaya hidup sehat Anda!",
  },
  sedang: {
    Icon: ShieldAlert,
    gradient: "from-yellow-500/20 to-amber-600/20",
    border: "border-yellow-500/30",
    glow: "glow-yellow",
    badge: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    title: "Risiko Sedang",
    description:
      "Model AI mengindikasikan adanya beberapa faktor risiko kardiovaskular. Disarankan untuk berkonsultasi dengan dokter dan melakukan pemeriksaan lebih lanjut.",
  },
  tinggi: {
    Icon: ShieldX,
    gradient: "from-red-500/20 to-rose-600/20",
    border: "border-red-500/30",
    glow: "glow-red",
    badge: "bg-red-500/20 text-red-400 border-red-500/30",
    title: "Risiko Tinggi",
    description:
      "Hasil analisis menunjukkan risiko kardiovaskular yang tinggi. Sangat disarankan untuk segera berkonsultasi dengan dokter spesialis jantung untuk evaluasi dan penanganan.",
  },
};

export default function ResultCard({ result, onReset }) {
  if (!result) return null;

  const config = RISK_CONFIG[result.risk_label] || RISK_CONFIG.sedang;
  const { Icon } = config;

  return (
    <div
      className={`glass-card ${config.glow} ${config.border} overflow-hidden animate-scale-in`}
      id="result-card"
    >
      {/* Gradient header bar */}
      <div className={`bg-gradient-to-r ${config.gradient} px-6 sm:px-8 pt-6 pb-4`}>
        <div className="flex items-center gap-3 mb-1">
          <Icon className="w-6 h-6 text-white" />
          <h2 className="text-xl font-bold text-white">Hasil Analisis AI</h2>
        </div>
        <p className="text-surface-300 text-sm">
          Prediksi risiko penyakit kardiovaskular
        </p>
      </div>

      <div className="px-6 sm:px-8 py-6 space-y-6">
        {/* Risk gauge + status */}
        <div className="flex flex-col sm:flex-row items-center gap-6">
          <RiskGauge percent={result.risk_percent} color={result.risk_color} />

          <div className="text-center sm:text-left flex-1">
            {/* Badge */}
            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1 text-sm font-semibold rounded-full border ${config.badge} mb-3`}
            >
              <Icon className="w-4 h-4" />
              {config.title}
            </span>

            {/* Description */}
            <p className="text-surface-300 text-sm leading-relaxed">
              {result.ai_explanation || config.description}
            </p>

            {/* Threshold */}
            <div className="flex items-center gap-1.5 mt-3 text-xs text-surface-500">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>
                Threshold model: <span className="font-mono font-medium text-surface-400">{result.threshold}</span>
              </span>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="flex gap-2.5 p-3.5 bg-amber-500/[0.08] border border-amber-500/20 rounded-xl">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-xs text-amber-200/80 leading-relaxed">
            {result.disclaimer}
          </p>
        </div>

        {/* Info badge */}
        <div className="flex gap-2.5 p-3.5 bg-primary-500/[0.06] border border-primary-500/15 rounded-xl">
          <Info className="w-4 h-4 text-primary-400 shrink-0 mt-0.5" />
          <p className="text-xs text-primary-200/70 leading-relaxed">
            Prediksi dihasilkan oleh model deep learning CardioGuard berdasarkan data masukan Anda yang telah diproses menjadi{" "}
            <span className="font-medium text-primary-300">24 fitur analisis</span>{" "}
          </p>
        </div>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 mt-4 print:hidden">
          <button
            type="button"
            onClick={() => window.print()}
            className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-primary-600 hover:bg-primary-500 text-white font-semibold shadow-md shadow-primary-600/20 transition-all duration-300 text-sm hover:scale-[1.01] active:scale-[0.99]"
            id="print-button"
          >
            <Printer className="w-4 h-4" />
            Cetak Hasil
          </button>
          <button
            type="button"
            onClick={onReset}
            className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl border border-surface-600/50 text-surface-300 hover:text-white hover:border-primary-500/50 hover:bg-primary-500/10 transition-all duration-300 text-sm font-medium"
            id="reset-button"
          >
            <RotateCcw className="w-4 h-4" />
            Analisis Ulang
          </button>
        </div>
      </div>
    </div>
  );
}
