import {
  Scale,
  HeartPulse,
  PersonStanding,
  Activity,
} from "lucide-react";

const CARDS = [
  {
    key: "bmi",
    icon: Scale,
    label: "BMI",
    getValue: (s) => s.bmi,
    getSub: (s) => s.bmi_category,
    getColor: (s) => {
      const v = s.bmi;
      if (v < 18.5) return "text-blue-400";
      if (v < 25) return "text-green-400";
      if (v < 30) return "text-yellow-400";
      return "text-red-400";
    },
  },
  {
    key: "bp",
    icon: HeartPulse,
    label: "Tekanan Darah",
    getValue: (s) => s.blood_pressure,
    getSub: (s) => s.bp_status,
    getColor: (s) => {
      const status = s.bp_status;
      if (status === "Normal") return "text-green-400";
      if (status === "Elevated") return "text-yellow-400";
      return "text-red-400";
    },
  },
  {
    key: "lifestyle",
    icon: PersonStanding,
    label: "Risiko Gaya Hidup",
    getValue: (s) => `${s.lifestyle_risk_score}/3`,
    getSub: (s) => s.lifestyle_risk_label,
    getColor: (s) => {
      const v = s.lifestyle_risk_score;
      if (v === 0) return "text-green-400";
      if (v === 1) return "text-yellow-400";
      return "text-red-400";
    },
  },
];

export default function DashboardSummary({ summary }) {
  if (!summary) return null;

  return (
    <div className="animate-slide-up" id="dashboard-summary">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-4 h-4 text-primary-400" />
        <h3 className="text-sm font-semibold text-surface-300 uppercase tracking-wide">
          Ringkasan Kesehatan
        </h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {CARDS.map(({ key, icon: Icon, label, getValue, getSub, getColor }) => (
          <div
            key={key}
            className="glass-card p-4 flex flex-col items-center text-center gap-2 hover:border-primary-500/30 transition-all duration-300"
          >
            <div className="w-10 h-10 rounded-xl bg-surface-800/60 flex items-center justify-center">
              <Icon className={`w-5 h-5 ${getColor(summary)}`} />
            </div>
            <span className="text-xs text-surface-400 font-medium">{label}</span>
            <span className={`text-lg font-bold ${getColor(summary)}`}>
              {getValue(summary)}
            </span>
            <span
              className={`text-[11px] px-2 py-0.5 rounded-full font-medium border ${
                getColor(summary).replace("text-", "border-").replace("400", "500/30")
              } ${getColor(summary)} bg-surface-800/40`}
            >
              {getSub(summary)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
