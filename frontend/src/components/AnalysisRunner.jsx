import { useState } from "react";
import { runAnalysis } from "../services/api";

export default function AnalysisRunner({ companyId, onComplete }) {
  const [primaryInsights, setPrimaryInsights] = useState("");
  const [creditOfficerObservations, setCreditOfficerObservations] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!companyId) {
      setError("Create company before running analysis.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const result = await runAnalysis({
        company_id: companyId,
        primary_insights: primaryInsights
          .split("\n")
          .map((value) => value.trim())
          .filter(Boolean),
        credit_officer_observations: creditOfficerObservations,
      });
      onComplete(result);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="space-y-3 rounded-xl border bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">3. Run Analysis</h2>
      <textarea
        value={primaryInsights}
        onChange={(e) => setPrimaryInsights(e.target.value)}
        placeholder="Primary insights (one per line)"
        className="min-h-24 w-full rounded border p-2"
      />
      <textarea
        value={creditOfficerObservations}
        onChange={(e) => setCreditOfficerObservations(e.target.value)}
        placeholder="Credit officer observations"
        className="min-h-24 w-full rounded border p-2"
      />
      <button type="submit" disabled={loading} className="rounded bg-slate-900 px-4 py-2 text-white disabled:opacity-60">
        {loading ? "Running..." : "Run Full Credit Workflow"}
      </button>
      {error ? <p className="text-sm text-red-700">{error}</p> : null}
    </form>
  );
}
