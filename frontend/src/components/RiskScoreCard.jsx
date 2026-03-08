import { motion } from "framer-motion";
import CountUp from "react-countup";

export default function RiskScoreCard({ riskScores, recommendation }) {
  const score = Number(riskScores?.weighted_final_score || 0);
  const decision = recommendation?.decision || "Pending";

  return (
    <motion.section
      whileHover={{ y: -4, scale: 1.01, boxShadow: "0 16px 30px rgba(15,23,42,0.14)" }}
      transition={{ type: "spring", stiffness: 280, damping: 24 }}
      className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl"
    >
      <h3 className="text-lg font-semibold text-white">Risk Score</h3>
      <div className="mt-3">
        <div className="mb-2 flex items-end justify-between">
          <p className="text-3xl font-bold text-white"><CountUp end={score} duration={1.4} decimals={2} /></p>
          <p className="text-sm text-white/70">out of 100</p>
        </div>
        <div className="h-3 rounded-full bg-white/25">
          <div
            className={`h-3 rounded-full transition-all ${score >= 80 ? "bg-emerald-300" : score >= 60 ? "bg-cyan-300" : "bg-rose-300"}`}
            style={{ width: `${Math.min(Math.max(score, 0), 100)}%` }}
          />
        </div>
      </div>
      <p className="mt-4 rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-white/85">Recommendation: {decision}</p>
    </motion.section>
  );
}
