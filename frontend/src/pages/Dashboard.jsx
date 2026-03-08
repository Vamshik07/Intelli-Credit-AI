import { motion } from "framer-motion";
import CountUp from "react-countup";

function GlassCard({ title, children }) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02, boxShadow: "0 14px 28px rgba(14,165,233,0.24)" }}
      transition={{ type: "spring", stiffness: 260, damping: 22 }}
      className="rounded-2xl border border-white/10 bg-slate-900/85 p-5 shadow-xl backdrop-blur-md"
    >
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-200">{title}</p>
      <div className="mt-2 font-semibold text-white">{children}</div>
    </motion.div>
  );
}

function RiskGauge({ score }) {
  const circumference = 440;
  const offset = circumference - (Math.max(0, Math.min(100, score)) / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <svg width="160" height="160" className="-rotate-90">
        <circle cx="80" cy="80" r="70" stroke="rgba(255,255,255,0.22)" strokeWidth="12" fill="transparent" />

        <motion.circle
          cx="80"
          cy="80"
          r="70"
          stroke="url(#riskGrad)"
          strokeWidth="12"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 2 }}
        />

        <defs>
          <linearGradient id="riskGrad">
            <stop offset="0%" stopColor="#22D3EE" />
            <stop offset="100%" stopColor="#A78BFA" />
          </linearGradient>
        </defs>
      </svg>

      <div className="-mt-1 text-3xl font-bold">
        <CountUp end={Number(score || 0)} duration={2} decimals={2} />
      </div>
      <span className="text-xs font-medium text-slate-200">Credit Risk Score</span>
    </div>
  );
}

export default function Dashboard({ health, healthLoading, companyId, analysisResult }) {
  const score = analysisResult?.risk_scores?.weighted_final_score || 0;

  return (
    <section className="space-y-4">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl border border-white/10 bg-slate-900/85 p-6 shadow-xl backdrop-blur-md">
        <h2 className="text-2xl font-semibold text-white">AI Credit Dashboard</h2>
        <p className="mt-2 font-medium text-slate-200">Analyze financials, legal signals, and external intelligence using LangGraph multi-agent orchestration.</p>
      </motion.div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {healthLoading ? (
          Array.from({ length: 4 }).map((_, idx) => <div key={idx} className="h-44 rounded-2xl skeleton" />)
        ) : (
          <>
            <GlassCard title="API Status">
              <p className="text-lg">{health.apiUp ? "Operational" : "Offline"}</p>
            </GlassCard>
            <GlassCard title="MongoDB">
              <p className="text-lg">{health.mongoConnected ? "Connected" : "Disconnected"}</p>
            </GlassCard>
            <GlassCard title="Current Company">
              <p className="text-lg">{companyId || "Not Selected"}</p>
            </GlassCard>
            <GlassCard title="Risk Score">
              <RiskGauge score={score} />
            </GlassCard>
          </>
        )}
      </div>
    </section>
  );
}
