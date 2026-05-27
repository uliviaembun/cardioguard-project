import { useState, useMemo } from "react";
import {
  User,
  Ruler,
  Weight,
  HeartPulse,
  Droplets,
  Cigarette,
  Wine,
  Dumbbell,
  Calculator,
  ArrowRight,
  Loader2,
} from "lucide-react";

const INITIAL_FORM = {
  age_years: "",
  gender: "",
  height: "",
  weight: "",
  ap_hi: "",
  ap_lo: "",
  cholesterol: "",
  gluc: "",
  smoke: 0,
  alco: 0,
  active: 1,
};

export default function PredictionForm({ onSubmit, loading }) {
  const [form, setForm] = useState(INITIAL_FORM);

  // ---------- Helpers ----------

  const set = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const bmi = useMemo(() => {
    const h = parseFloat(form.height);
    const w = parseFloat(form.weight);
    if (h > 0 && w > 0) return (w / (h / 100) ** 2).toFixed(1);
    return null;
  }, [form.height, form.weight]);

  const bmiColor = useMemo(() => {
    if (!bmi) return "text-surface-400";
    const v = parseFloat(bmi);
    if (v < 18.5) return "text-blue-400";
    if (v < 25) return "text-green-400";
    if (v < 30) return "text-yellow-400";
    return "text-red-400";
  }, [bmi]);

  const bmiLabel = useMemo(() => {
    if (!bmi) return "";
    const v = parseFloat(bmi);
    if (v < 18.5) return "Kurang";
    if (v < 25) return "Normal";
    if (v < 30) return "Berlebih";
    return "Obesitas";
  }, [bmi]);

  // ---------- Submit ----------

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      age_years: parseInt(form.age_years, 10),
      gender: parseInt(form.gender, 10),
      height: parseFloat(form.height),
      weight: parseFloat(form.weight),
      ap_hi: parseFloat(form.ap_hi),
      ap_lo: parseFloat(form.ap_lo),
      cholesterol: parseInt(form.cholesterol, 10),
      gluc: parseInt(form.gluc, 10),
      smoke: form.smoke,
      alco: form.alco,
      active: form.active,
    };
    onSubmit(payload);
  };

  // ---------- Toggle component ----------

  const Toggle = ({ value, onChange, label, activeLabel, inactiveLabel }) => (
    <div className="flex items-center justify-between">
      <span className="input-label mb-0">{label}</span>
      <div className="flex items-center gap-2">
        <span className={`text-xs ${value ? "text-surface-500" : "text-surface-300 font-medium"}`}>
          {inactiveLabel}
        </span>
        <button
          type="button"
          onClick={() => onChange(value ? 0 : 1)}
          className={`toggle-btn ${value ? "toggle-btn-active" : "toggle-btn-inactive"}`}
          aria-label={label}
        >
          <span
            className="toggle-knob"
            style={{ transform: value ? "translateX(22px)" : "translateX(2px)" }}
          />
        </button>
        <span className={`text-xs ${value ? "text-primary-300 font-medium" : "text-surface-500"}`}>
          {activeLabel}
        </span>
      </div>
    </div>
  );

  // ---------- Render ----------

  return (
    <form
      onSubmit={handleSubmit}
      className="glass-card p-6 sm:p-8 space-y-6 animate-fade-in"
      id="prediction-form"
    >
      {/* -------- Section: Data Pribadi -------- */}
      <div>
        <div className="section-label">
          <User className="w-4 h-4" />
          <span>Data Pribadi</span>
          <div className="section-line" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Umur */}
          <div>
            <label htmlFor="age_years" className="input-label">Umur (tahun)</label>
            <input
              id="age_years"
              type="number"
              min="1"
              max="120"
              required
              placeholder="Misal: 45"
              value={form.age_years}
              onChange={(e) => set("age_years", e.target.value)}
              className="input-field"
            />
          </div>

          {/* Gender */}
          <div>
            <label htmlFor="gender" className="input-label">Jenis Kelamin</label>
            <select
              id="gender"
              required
              value={form.gender}
              onChange={(e) => set("gender", e.target.value)}
              className="select-field"
            >
              <option value="" disabled>Pilih</option>
              <option value="1">Wanita</option>
              <option value="2">Pria</option>
            </select>
          </div>
        </div>
      </div>

      {/* -------- Section: Fisik -------- */}
      <div>
        <div className="section-label">
          <Ruler className="w-4 h-4" />
          <span>Data Fisik</span>
          <div className="section-line" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Tinggi */}
          <div>
            <label htmlFor="height" className="input-label">Tinggi Badan (cm)</label>
            <input
              id="height"
              type="number"
              min="50"
              max="250"
              step="0.1"
              required
              placeholder="Misal: 168"
              value={form.height}
              onChange={(e) => set("height", e.target.value)}
              className="input-field"
            />
          </div>

          {/* Berat */}
          <div>
            <label htmlFor="weight" className="input-label">Berat Badan (kg)</label>
            <input
              id="weight"
              type="number"
              min="10"
              max="300"
              step="0.1"
              required
              placeholder="Misal: 75"
              value={form.weight}
              onChange={(e) => set("weight", e.target.value)}
              className="input-field"
            />
          </div>
        </div>

        {/* BMI auto */}
        {bmi && (
          <div className="mt-3 flex items-center gap-2 px-4 py-2.5 bg-surface-800/40 rounded-xl border border-surface-700/50 animate-fade-in">
            <Calculator className="w-4 h-4 text-primary-400" />
            <span className="text-sm text-surface-400">BMI Otomatis:</span>
            <span className={`text-sm font-bold ${bmiColor}`}>{bmi}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${bmiColor} bg-surface-700/50 font-medium`}>
              {bmiLabel}
            </span>
          </div>
        )}
      </div>

      {/* -------- Section: Tanda Vital -------- */}
      <div>
        <div className="section-label">
          <HeartPulse className="w-4 h-4" />
          <span>Tanda Vital</span>
          <div className="section-line" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Sistolik */}
          <div>
            <label htmlFor="ap_hi" className="input-label">Tekanan Darah Sistolik (mmHg)</label>
            <input
              id="ap_hi"
              type="number"
              min="50"
              max="250"
              required
              placeholder="Misal: 120"
              value={form.ap_hi}
              onChange={(e) => set("ap_hi", e.target.value)}
              className="input-field"
            />
          </div>

          {/* Diastolik */}
          <div>
            <label htmlFor="ap_lo" className="input-label">Tekanan Darah Diastolik (mmHg)</label>
            <input
              id="ap_lo"
              type="number"
              min="30"
              max="200"
              required
              placeholder="Misal: 80"
              value={form.ap_lo}
              onChange={(e) => set("ap_lo", e.target.value)}
              className="input-field"
            />
          </div>
        </div>
      </div>

      {/* -------- Section: Indikator Kesehatan -------- */}
      <div>
        <div className="section-label">
          <Droplets className="w-4 h-4" />
          <span>Indikator Kesehatan</span>
          <div className="section-line" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Kolesterol */}
          <div>
            <label htmlFor="cholesterol" className="input-label">Level Kolesterol</label>
            <select
              id="cholesterol"
              required
              value={form.cholesterol}
              onChange={(e) => set("cholesterol", e.target.value)}
              className="select-field"
            >
              <option value="" disabled>Pilih</option>
              <option value="1">Normal</option>
              <option value="2">Di atas Normal</option>
              <option value="3">Jauh di atas Normal</option>
            </select>
          </div>

          {/* Gula Darah */}
          <div>
            <label htmlFor="gluc" className="input-label">Level Gula Darah</label>
            <select
              id="gluc"
              required
              value={form.gluc}
              onChange={(e) => set("gluc", e.target.value)}
              className="select-field"
            >
              <option value="" disabled>Pilih</option>
              <option value="1">Normal</option>
              <option value="2">Di atas Normal</option>
              <option value="3">Jauh di atas Normal</option>
            </select>
          </div>
        </div>
      </div>

      {/* -------- Section: Gaya Hidup -------- */}
      <div>
        <div className="section-label">
          <Dumbbell className="w-4 h-4" />
          <span>Gaya Hidup</span>
          <div className="section-line" />
        </div>

        <div className="space-y-4 bg-surface-800/30 rounded-xl p-4 border border-surface-700/40">
          <Toggle
            value={form.smoke}
            onChange={(v) => set("smoke", v)}
            label={<span className="flex items-center gap-1.5"><Cigarette className="w-3.5 h-3.5" /> Merokok</span>}
            activeLabel="Ya"
            inactiveLabel="Tidak"
          />
          <div className="h-px bg-surface-700/30" />
          <Toggle
            value={form.alco}
            onChange={(v) => set("alco", v)}
            label={<span className="flex items-center gap-1.5"><Wine className="w-3.5 h-3.5" /> Konsumsi Alkohol</span>}
            activeLabel="Ya"
            inactiveLabel="Tidak"
          />
          <div className="h-px bg-surface-700/30" />
          <Toggle
            value={form.active}
            onChange={(v) => set("active", v)}
            label={<span className="flex items-center gap-1.5"><Dumbbell className="w-3.5 h-3.5" /> Aktivitas Fisik</span>}
            activeLabel="Aktif"
            inactiveLabel="Tidak"
          />
        </div>
      </div>

      {/* -------- Submit -------- */}
      <button
        type="submit"
        disabled={loading}
        className="btn-primary flex items-center justify-center gap-2 text-base"
        id="submit-prediction"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Menganalisis Risiko…</span>
          </>
        ) : (
          <>
            <HeartPulse className="w-5 h-5" />
            <span>Analisis Risiko Kardiovaskular</span>
            <ArrowRight className="w-4 h-4" />
          </>
        )}
      </button>
    </form>
  );
}
