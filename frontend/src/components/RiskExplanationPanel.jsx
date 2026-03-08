export default function RiskExplanationPanel({ reasons = [], researchInsights = {} }) {
  return (
    <section className="space-y-4 rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
      <div>
        <h3 className="text-lg font-semibold text-white">Risk Explanation</h3>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-white/85">
          {reasons.length ? reasons.map((reason, index) => <li key={`${reason}-${index}`}>{reason}</li>) : <li>No risk reasons generated</li>}
        </ul>
      </div>
      <div className="rounded-lg border border-white/15 bg-white/5 p-3 text-sm text-white/85">
        <p className="font-medium text-white">Research Insights</p>
        <p className="mt-1"><span className="font-medium">Industry trends:</span> {researchInsights.industry_trends || "n/a"}</p>
        <p className="mt-1"><span className="font-medium">News signals:</span> {(researchInsights.news_signals || []).slice(0, 3).join(" | ") || "n/a"}</p>
        <p className="mt-1"><span className="font-medium">Regulatory alerts:</span> {(researchInsights.regulatory_alerts || []).join(", ") || "n/a"}</p>
      </div>
    </section>
  );
}
