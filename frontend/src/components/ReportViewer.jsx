export default function ReportViewer({ analysisResult, latestReport }) {
  if (!analysisResult && !latestReport) {
    return (
      <div className="rounded-xl border bg-white p-4 shadow-sm">
        <h2 className="text-lg font-semibold">4. Decision Output</h2>
        <p className="text-slate-600">Run analysis to view recommendation and risk report.</p>
      </div>
    );
  }

  const risk = analysisResult?.risk || latestReport || {};
  const recommendation = analysisResult?.recommendation || latestReport?.loan_terms || {};
  const reasons = analysisResult?.reasons || latestReport?.reasons || [];
  const reports = analysisResult?.reports || latestReport?.report_paths || {};
  const explainability = analysisResult?.explainability || {};
  const components = explainability.components || {};

  return (
    <div className="space-y-3 rounded-xl border bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">4. Decision Output</h2>
      <div className="grid gap-2 md:grid-cols-2">
        <p><span className="font-medium">Final Score:</span> {risk.final_score ?? "n/a"}</p>
        <p><span className="font-medium">Recommendation:</span> {risk.recommendation || "n/a"}</p>
      </div>
      <div>
        <p className="font-medium">Risk Reasons</p>
        <ul className="list-disc pl-5 text-sm text-slate-700">
          {reasons.length ? reasons.map((reason, index) => <li key={`${reason}-${index}`}>{reason}</li>) : <li>No reasons available</li>}
        </ul>
      </div>
      <div className="text-sm text-slate-700">
        <p><span className="font-medium">Loan Terms:</span> {JSON.stringify(recommendation)}</p>
        <p><span className="font-medium">CAM DOCX:</span> {reports.cam_docx_path || "n/a"}</p>
        <p><span className="font-medium">CAM PDF:</span> {reports.cam_pdf_path || "n/a"}</p>
      </div>
      {Object.keys(components).length ? (
        <div className="text-sm text-slate-700">
          <p className="font-medium">Explainability Components</p>
          <p>Weighted Score: {components.weighted_score ?? "n/a"}</p>
          <p>Primary Insight Penalty: {components.primary_insight_penalty ?? "n/a"}</p>
          <p>Financial Strength: {components.financial_strength ?? "n/a"}</p>
          <p>Legal Strength: {components.legal_strength ?? "n/a"}</p>
          <p>Promoter Strength: {components.promoter_strength ?? "n/a"}</p>
          <p>Industry Strength: {components.industry_strength ?? "n/a"}</p>
          <p>Operational Strength: {components.operational_strength ?? "n/a"}</p>
        </div>
      ) : null}
    </div>
  );
}
