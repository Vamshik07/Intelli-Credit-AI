import AgentWorkflowViewer from "../components/AgentWorkflowViewer";
import FinancialMetricsPanel from "../components/FinancialMetricsPanel";
import RiskExplanationPanel from "../components/RiskExplanationPanel";
import RiskScoreCard from "../components/RiskScoreCard";

export default function ResultsPage({ analysisResult, workflow }) {
  if (!analysisResult) {
    return (
      <div className="space-y-4">
        <div className="rounded-2xl border border-white/20 bg-white/10 p-5 text-sm text-white/80 shadow-xl backdrop-blur-xl">
          Run analysis to view risk score, recommendation, and explainability results.
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="h-48 rounded-2xl skeleton" />
          <div className="h-48 rounded-2xl skeleton" />
        </div>
        <div className="h-40 rounded-2xl skeleton" />
      </div>
    );
  }

  return (
    <section className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-2">
        <RiskScoreCard riskScores={analysisResult.risk_scores} recommendation={analysisResult.recommendation} />
        <AgentWorkflowViewer workflow={workflow} />
      </div>
      <FinancialMetricsPanel financialData={analysisResult.financial_data} />
      <RiskExplanationPanel reasons={analysisResult.reasons} researchInsights={analysisResult.research_insights} />

      <div className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
        <h3 className="text-lg font-semibold text-white">Recommendation</h3>
        <p className="mt-2 text-sm text-white/85">Decision: <span className="font-medium text-white">{analysisResult.recommendation?.decision || "n/a"}</span></p>
        <p className="mt-1 text-sm text-white/85">Recommended Loan Amount: <span className="font-medium text-white">{Number(analysisResult.recommendation?.recommended_loan_amount || 0).toLocaleString()}</span></p>
        <p className="mt-1 text-sm text-white/85">Suggested Interest Rate: <span className="font-medium text-white">{analysisResult.recommendation?.suggested_interest_rate || 0}%</span></p>
      </div>

      <div className="rounded-2xl border border-white/20 bg-white/10 p-5 text-sm text-white/85 shadow-xl backdrop-blur-xl">
        MongoDB Risk ID: <span className="font-medium text-white">{analysisResult.database_record?.risk_id || "n/a"}</span>
      </div>
    </section>
  );
}
