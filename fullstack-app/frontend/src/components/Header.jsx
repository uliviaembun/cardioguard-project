import { Heart, Activity, Shield } from "lucide-react";

export default function Header() {
  return (
    <header className="relative text-center pt-12 pb-8 px-4">
      {/* Decorative background orbs */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-primary-500/[0.07] rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute top-10 left-1/4 w-[200px] h-[200px] bg-primary-400/[0.04] rounded-full blur-[80px] pointer-events-none" />

      {/* Logo icon cluster */}
      <div className="relative inline-flex items-center justify-center mb-6">
        <div className="absolute w-20 h-20 bg-primary-500/20 rounded-full animate-pulse-slow" />
        <div className="absolute w-14 h-14 bg-primary-500/30 rounded-full animate-pulse-slow" style={{ animationDelay: "0.5s" }} />
        <div className="relative z-10 w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-500/30 rotate-3">
          <Heart className="w-8 h-8 text-white animate-heartbeat" />
        </div>
        <div className="absolute -right-3 -top-1 z-20 w-7 h-7 bg-gradient-to-br from-green-400 to-emerald-500 rounded-lg flex items-center justify-center shadow-md">
          <Shield className="w-4 h-4 text-white" />
        </div>
      </div>

      {/* Title */}
      <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-3">
        <span className="text-gradient">Cardio</span>
        <span className="text-white">Guard</span>
      </h1>

      {/* Tagline */}
      <p className="text-surface-400 text-sm sm:text-base max-w-md mx-auto leading-relaxed">
        Sistem prediksi risiko penyakit kardiovaskular berbasis
        <span className="text-primary-400 font-medium"> Artificial Intelligence</span>
      </p>

      {/* Feature badges */}
      <div className="flex flex-wrap justify-center gap-3 mt-6">
        {[
          { icon: Activity, text: "Deep Learning Model" },
          { icon: Shield, text: "Skrining Akurat" },
          { icon: Heart, text: "Deteksi Dini" },
        ].map(({ icon: Icon, text }) => (
          <span
            key={text}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary-500/10 text-primary-300 text-xs font-medium rounded-full border border-primary-500/20"
          >
            <Icon className="w-3.5 h-3.5" />
            {text}
          </span>
        ))}
      </div>
    </header>
  );
}
