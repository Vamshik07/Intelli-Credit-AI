export default function ObservationInput({ primaryInsightsText, setPrimaryInsightsText, creditOfficerObservations, setCreditOfficerObservations }) {
  return (
    <section className="space-y-4 rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
      <h2 className="text-lg font-semibold text-white">Credit Officer Observations</h2>
      <div>
        <label className="mb-1 block text-sm font-medium text-white/85">Primary Insights (one per line)</label>
        <textarea
          value={primaryInsightsText}
          onChange={(event) => setPrimaryInsightsText(event.target.value)}
          placeholder="Operating profit remains stable\nModerate debt-to-equity ratio\nStrong sector demand"
          className="min-h-36 w-full rounded-lg border border-white/30 bg-white/10 p-3 text-sm text-white placeholder:text-white/60 outline-none ring-cyan-300 transition focus:ring"
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-white/85">Narrative Observation</label>
        <textarea
          value={creditOfficerObservations}
          onChange={(event) => setCreditOfficerObservations(event.target.value)}
          placeholder="Add qualitative management, governance, repayment behavior, and operational observations..."
          className="min-h-36 w-full rounded-lg border border-white/30 bg-white/10 p-3 text-sm text-white placeholder:text-white/60 outline-none ring-cyan-300 transition focus:ring"
        />
      </div>
    </section>
  );
}
