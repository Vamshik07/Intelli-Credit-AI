import { motion } from "framer-motion";
import Lottie from "lottie-react";

const STATUS_STYLE = {
  pending: "bg-slate-200 text-slate-600",
  in_progress: "bg-indigo-100 text-indigo-700",
  completed: "bg-emerald-100 text-emerald-700",
  warning: "bg-amber-100 text-amber-700",
};

const pulseLottie = {
  v: "5.7.4",
  fr: 30,
  ip: 0,
  op: 60,
  w: 120,
  h: 120,
  nm: "pulse",
  ddd: 0,
  assets: [],
  layers: [
    {
      ddd: 0,
      ind: 1,
      ty: 4,
      nm: "circle",
      sr: 1,
      ks: {
        o: { a: 0, k: 100 },
        r: { a: 0, k: 0 },
        p: { a: 0, k: [60, 60, 0] },
        a: { a: 0, k: [0, 0, 0] },
        s: {
          a: 1,
          k: [
            { t: 0, s: [60, 60, 100] },
            { t: 30, s: [100, 100, 100] },
            { t: 60, s: [60, 60, 100] },
          ],
        },
      },
      shapes: [
        { ty: "el", p: { a: 0, k: [0, 0] }, s: { a: 0, k: [40, 40] }, nm: "Ellipse" },
        { ty: "fl", c: { a: 0, k: [0.31, 0.27, 0.9, 1] }, o: { a: 0, k: 100 }, r: 1, nm: "Fill" },
      ],
      ip: 0,
      op: 60,
      st: 0,
      bm: 0,
    },
  ],
};

export default function AnalysisProgressTracker({ workflow, loading }) {
  return (
    <section className="space-y-3 rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Agent Workflow</h2>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${loading ? "bg-cyan-300/25 text-cyan-100" : "bg-white/15 text-white/80"}`}>
          {loading ? "AI analysis in progress" : "Ready"}
        </span>
      </div>

      {loading ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-3 rounded-xl border border-cyan-200/30 bg-white/10 p-3">
          <div className="h-12 w-12">
            <Lottie animationData={pulseLottie} loop />
          </div>
          <div>
            <p className="text-sm font-semibold text-cyan-100">AI Agents Analyzing Financial Data...</p>
            <p className="text-xs text-white/75">Pipeline is running with staged validation and risk aggregation.</p>
          </div>
        </motion.div>
      ) : null}

      <div className="flex items-center gap-2 overflow-x-auto rounded-lg bg-white/10 p-2 text-xs text-white/80">
        {workflow.map((step, idx) => (
          <div key={`node-${step.agent}`} className="flex items-center gap-2">
            <motion.div
              animate={step.status === "in_progress" ? { boxShadow: ["0 0 0 0 rgba(79,70,229,0.4)", "0 0 0 12px rgba(79,70,229,0)"] } : {}}
              transition={{ repeat: Infinity, duration: 1.6 }}
              className={`h-2.5 w-2.5 rounded-full ${step.status === "completed" ? "bg-emerald-300" : step.status === "in_progress" ? "bg-cyan-300" : "bg-white/40"}`}
            />
            <span className="whitespace-nowrap">{step.label.replace(" Agent", "")}</span>
            {idx < workflow.length - 1 ? <span className="flow-arrow inline-block h-2 w-8" /> : null}
          </div>
        ))}
      </div>

      <div className="space-y-2">
        {workflow.map((step, index) => (
          <motion.div
            key={step.agent}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.06 }}
            className="flex items-center justify-between rounded-lg border border-white/20 bg-white/5 px-3 py-2"
          >
            <p className="text-sm text-white/90">{step.label}</p>
            <span className={`rounded-full px-2 py-1 text-xs font-medium ${STATUS_STYLE[step.status] || STATUS_STYLE.pending}`}>
              {step.status === "completed" ? "completed OK" : step.status.replace("_", " ")}
            </span>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
