import AnalysisProgressTracker from "../components/AnalysisProgressTracker";
import AnimatedButton from "../components/AnimatedButton";
import { motion } from "framer-motion";

export default function AnalysisPage({ runFullAnalysis, analysisLoading, analysisError, workflow }) {
  return (
    <section className="space-y-4">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
        <h2 className="text-xl font-semibold text-white">Run AI Analysis</h2>
        <p className="mt-1 text-sm text-white/80">This triggers the full LangGraph workflow: ingestion, financials, research, litigation, risk scoring, CAM generation.</p>
        <AnimatedButton
          type="button"
          onClick={runFullAnalysis}
          disabled={analysisLoading}
          className="mt-4 rounded-lg bg-gradient-to-r from-fuchsia-500 via-blue-500 to-cyan-400 px-4 py-2 text-sm font-medium text-white transition disabled:opacity-60"
          withConfetti
        >
          {analysisLoading ? "Running Analysis..." : "Run Full Credit Workflow"}
        </AnimatedButton>
        {analysisError ? <p className="mt-2 text-sm text-rose-600">{analysisError}</p> : null}
      </motion.div>

      {analysisLoading ? (
        <div className="rounded-2xl border border-cyan-200/40 bg-white/10 p-4 shadow-xl backdrop-blur-xl">
          <p className="text-sm font-semibold text-cyan-100">AI Agents are processing the credit pipeline</p>
          <div className="mt-3 space-y-2">
            <div className="h-3 w-full rounded skeleton" />
            <div className="h-3 w-10/12 rounded skeleton" />
            <div className="h-3 w-8/12 rounded skeleton" />
          </div>
        </div>
      ) : null}
      <AnalysisProgressTracker workflow={workflow} loading={analysisLoading} />
    </section>
  );
}
