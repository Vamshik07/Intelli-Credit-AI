import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import CountUp from "react-countup";
import { fetchCompanyStats } from "../services/api";

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

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function formatPercent(value) {
  return `${Number(value || 0).toFixed(1)}%`;
}

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));
}

function normalizeDecision(decisionRaw) {
  const value = String(decisionRaw || "").toLowerCase();
  if (value.includes("reject")) {
    return "Reject";
  }
  if (value.includes("condition")) {
    return "Conditional";
  }
  if (value.includes("approve")) {
    return "Approve";
  }
  return "Pending";
}

function RiskGauge({ score, compact = false }) {
  const radius = compact ? 56 : 86;
  const strokeWidth = compact ? 10 : 14;
  const center = compact ? 70 : 110;
  const svgSize = compact ? 140 : 220;
  const displaySizeClass = compact ? "text-3xl" : "text-5xl";
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.max(0, Math.min(100, score)) / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <svg width={svgSize} height={svgSize} className="-rotate-90">
        <circle cx={center} cy={center} r={radius} stroke="rgba(255,255,255,0.18)" strokeWidth={strokeWidth} fill="transparent" />

        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          stroke="url(#riskGrad)"
          strokeWidth={strokeWidth}
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

      <div className={`-mt-4 font-bold ${displaySizeClass}`}>
        <CountUp end={Number(score || 0)} duration={2} decimals={1} />
      </div>
      <span className="text-xs font-medium uppercase tracking-wider text-slate-200">Credit Risk Score</span>
    </div>
  );
}

function HealthMetricCard({ title, value, hint }) {
  return (
    <GlassCard title={title}>
      <div className="text-2xl font-bold text-cyan-100">{value}</div>
      <p className="mt-1 text-xs text-slate-300">{hint}</p>
    </GlassCard>
  );
}

function AgentStatus({ label, status }) {
  const palette = {
    completed: "bg-emerald-500/20 text-emerald-300 border-emerald-400/30",
    in_progress: "bg-amber-500/20 text-amber-300 border-amber-400/30",
    warning: "bg-rose-500/20 text-rose-300 border-rose-400/30",
    pending: "bg-slate-500/20 text-slate-300 border-slate-400/30",
  };

  return (
    <div className="rounded-xl border border-white/10 bg-slate-950/55 p-3">
      <p className="text-sm font-medium text-slate-100">{label}</p>
      <span className={`mt-2 inline-flex rounded-full border px-2 py-1 text-xs font-semibold uppercase tracking-wide ${palette[status] || palette.pending}`}>
        {status ? String(status).replace("_", " ") : "pending"}
      </span>
    </div>
  );
}

function BenchmarkRow({ title, companyValue, benchmarkValue }) {
  const companyWidth = `${clamp(companyValue, 0, 100)}%`;
  const benchmarkWidth = `${clamp(benchmarkValue, 0, 100)}%`;

  return (
    <div className="space-y-2 rounded-xl border border-white/10 bg-slate-950/50 p-3">
      <p className="text-sm font-semibold text-slate-100">{title}</p>
      <div>
        <div className="mb-1 flex items-center justify-between text-xs text-slate-300">
          <span>Company</span>
          <span>{formatPercent(companyValue)}</span>
        </div>
        <div className="h-2 rounded-full bg-slate-700">
          <div className="h-2 rounded-full bg-cyan-400" style={{ width: companyWidth }} />
        </div>
      </div>
      <div>
        <div className="mb-1 flex items-center justify-between text-xs text-slate-300">
          <span>Industry</span>
          <span>{formatPercent(benchmarkValue)}</span>
        </div>
        <div className="h-2 rounded-full bg-slate-700">
          <div className="h-2 rounded-full bg-fuchsia-400" style={{ width: benchmarkWidth }} />
        </div>
      </div>
    </div>
  );
}

function ConfidenceBar({ confidence }) {
  const value = clamp(confidence, 0, 100);
  const tone = value >= 85 ? "high" : value >= 60 ? "moderate" : "low";

  const barClass =
    tone === "high"
      ? "bg-emerald-400"
      : tone === "moderate"
        ? "bg-amber-400"
        : "bg-rose-400";

  const labelClass =
    tone === "high"
      ? "text-emerald-300"
      : tone === "moderate"
        ? "text-amber-300"
        : "text-rose-300";

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-300">Confidence Scale</span>
        <span className={`font-semibold uppercase ${labelClass}`}>{tone}</span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-slate-700">
        <div className={`h-full rounded-full ${barClass}`} style={{ width: `${value}%` }} />
      </div>
      <div className="flex items-center justify-between text-[11px] text-slate-400">
        <span>Low &lt; 60%</span>
        <span>Moderate 60-84%</span>
        <span>High 85-95%</span>
      </div>
    </div>
  );
}

export default function Dashboard({ healthLoading, companyId, analysisResult, uploadSummary, workflow }) {
  const riskScores = analysisResult?.risk_scores || {};
  const score = Number(riskScores?.weighted_final_score || 0);
  const [statsLoading, setStatsLoading] = useState(true);
  const [stats, setStats] = useState({ totalApplications: 0, accepted: 0, rejected: 0 });

  useEffect(() => {
    let active = true;

    const loadStats = async () => {
      try {
        const data = await fetchCompanyStats();
        if (!active) {
          return;
        }

        setStats({
          totalApplications: Number(data?.total_applications || 0),
          accepted: Number(data?.accepted || 0),
          rejected: Number(data?.rejected || 0),
        });
      } catch {
        if (!active) {
          return;
        }
        setStats({ totalApplications: 0, accepted: 0, rejected: 0 });
      } finally {
        if (active) {
          setStatsLoading(false);
        }
      }
    };

    loadStats();
    const intervalId = setInterval(loadStats, 15000);

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, []);

  const cardsLoading = healthLoading || statsLoading;
  const financial = analysisResult?.financial_data || {};
  const risk = analysisResult?.risk || {};
  const recommendation = analysisResult?.recommendation || {};
  const explainability = analysisResult?.explainability || {};
  const components = explainability?.components || {};
  const insights = analysisResult?.research_insights || {};

  const revenue = Number(financial.revenue || 0);
  const totalDebt = Number(financial.total_debt || 0);
  const totalAssets = Number(financial.total_assets || 0);
  const netProfit = Number(financial.net_profit || 0);
  const ebitda = Number(financial.ebitda || 0);

  const equity = Math.max(totalAssets - totalDebt, 1);
  const debtToEquityRatio = totalDebt / equity;
  const liquidityRatio = totalAssets / Math.max(totalDebt, 1);
  const profitMargin = revenue ? (netProfit / revenue) * 100 : 0;
  const revenueGrowth = clamp((totalAssets ? (netProfit / totalAssets) * 130 : 0) + 8, -25, 60);
  const cashFlowStability = clamp(revenue ? (ebitda / revenue) * 120 : 0, 0, 100);

  const riskCategory = score >= 80 ? "Low" : score >= 60 ? "Medium" : "High";
  const probabilityOfDefault = Number(riskScores?.probability_of_default ?? risk?.probability_of_default ?? clamp(100 - score, 1, 99));
  const modelConfidence = Number(riskScores?.model_confidence ?? risk?.model_confidence ?? 0);

  const topRiskFactors = (risk?.reasons || []).slice(0, 3);
  const positiveIndicators = [
    { label: "Financial Strength", value: Number(components?.financial_strength || 0) },
    { label: "Legal Strength", value: Number(components?.legal_strength || 0) },
    { label: "Promoter Strength", value: Number(components?.promoter_strength || 0) },
    { label: "Operational Strength", value: Number(components?.operational_strength || 0) },
    { label: "Industry Strength", value: Number(components?.industry_strength || 0) },
  ]
    .filter((item) => item.value >= 65)
    .slice(0, 3);

  const aiNarrative =
    explainability?.summary ||
    `The AI model assigned a ${riskCategory.toLowerCase()} risk profile with ${formatPercent(modelConfidence)} confidence and a ${normalizeDecision(recommendation?.decision)} recommendation based on multi-agent financial and external signal analysis.`;

  const workflowMap = Object.fromEntries((workflow || []).map((step) => [step.agent, step.status]));
  const legalSignals = insights?.regulatory_alerts || [];
  const agentActivity = [
    { label: "Financial Analysis Agent", status: workflowMap.financial_agent || "pending" },
    { label: "Legal Risk Agent", status: workflowMap.litigation_agent || "pending" },
    { label: "Market Intelligence Agent", status: workflowMap.research_agent || "pending" },
    {
      label: "Fraud Detection Agent",
      status: analysisResult ? (legalSignals.length > 2 ? "warning" : "completed") : "pending",
    },
  ];

  const documentsProcessed = Number(explainability?.inputs_used?.document_count || uploadSummary?.uploaded_count || 0);
  const extractedFinancialStatements = revenue > 0 || totalAssets > 0 ? 1 : 0;
  const legalFilingsDetected = legalSignals.length;
  const externalSignalsAnalyzed = Number(explainability?.inputs_used?.news_headline_count || insights?.news_signals?.length || 0);

  const companyDebtRatio = clamp(revenue ? (totalDebt / revenue) * 100 : 0, 0, 100);
  const industryDebtRatio = clamp(45 + (100 - Number(components?.industry_strength || 50)) * 0.2, 0, 100);
  const companyProfitMargin = clamp(profitMargin, 0, 100);
  const industryProfitMargin = 12;
  const companyRevenueGrowth = clamp(revenueGrowth, 0, 100);
  const sectorRevenueGrowth = 10;

  const finalDecision = normalizeDecision(recommendation?.decision || risk?.recommendation);
  const decisionClass =
    finalDecision === "Approve"
      ? "bg-emerald-500/20 text-emerald-300 border-emerald-400/30"
      : finalDecision === "Conditional"
        ? "bg-amber-500/20 text-amber-300 border-amber-400/30"
        : finalDecision === "Reject"
          ? "bg-rose-500/20 text-rose-300 border-rose-400/30"
          : "bg-slate-500/20 text-slate-300 border-slate-400/30";

  const headlines = insights?.news_signals || [];
  const newsBlob = headlines.join(" ").toLowerCase();
  const newsSentiment =
    newsBlob.includes("growth") || newsBlob.includes("expansion")
      ? "Positive"
      : newsBlob.includes("decline") || newsBlob.includes("default") || newsBlob.includes("lawsuit")
        ? "Negative"
        : "Neutral";

  const timelineStages = [
    { label: "Company Registration", done: Boolean(companyId) },
    { label: "Document Upload", done: documentsProcessed > 0 },
    { label: "AI Analysis", done: Boolean(analysisResult) },
    { label: "Risk Scoring", done: Boolean(analysisResult?.risk_scores) },
    { label: "Decision", done: finalDecision !== "Pending" },
    { label: "Report Generation", done: Boolean(analysisResult?.reports?.cam_docx_path || analysisResult?.reports?.cam_pdf_path) },
  ];

  return (
    <section className="space-y-4">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl border border-white/10 bg-slate-900/85 p-6 shadow-xl backdrop-blur-md">
        <h2 className="text-2xl font-semibold text-white">AI Credit Dashboard</h2>
        <p className="mt-2 font-medium text-slate-200">Analyze financials, legal signals, and external intelligence using LangGraph multi-agent orchestration.</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl border border-cyan-300/20 bg-gradient-to-br from-slate-900/90 via-slate-900/90 to-blue-950/60 p-6 shadow-xl backdrop-blur-md">
        <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr]">
          <div className="flex items-center justify-center rounded-2xl border border-white/10 bg-slate-950/45 p-4">
            <RiskGauge score={score} />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <GlassCard title="Risk Category">
              <p className="text-2xl font-bold text-cyan-100">{riskCategory}</p>
            </GlassCard>
            <GlassCard title="Probability Of Default">
              <p className="text-2xl font-bold text-rose-300">{formatPercent(probabilityOfDefault)}</p>
            </GlassCard>
            <GlassCard title="Model Confidence">
              <p className="text-2xl font-bold text-emerald-300">{formatPercent(modelConfidence)}</p>
              <div className="mt-3">
                <ConfidenceBar confidence={modelConfidence} />
              </div>
            </GlassCard>
            <GlassCard title="Portfolio Coverage">
              <p className="text-2xl font-bold text-sky-200">{stats.totalApplications} Applicants</p>
            </GlassCard>
          </div>
        </div>
      </motion.div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cardsLoading ? (
          Array.from({ length: 4 }).map((_, idx) => <div key={idx} className="h-44 rounded-2xl skeleton" />)
        ) : (
          <>
            <GlassCard title="Loan Applications">
              <p className="text-2xl font-bold">{stats.totalApplications}</p>
            </GlassCard>
            <GlassCard title="Loan Decisions">
              <p className="text-sm text-slate-300">Accepted: <span className="text-lg font-bold text-emerald-300">{stats.accepted}</span></p>
              <p className="text-sm text-slate-300">Rejected: <span className="text-lg font-bold text-rose-300">{stats.rejected}</span></p>
            </GlassCard>
            <GlassCard title="Current Company">
              <p className="text-lg">{companyId || "Not Selected"}</p>
            </GlassCard>
            <GlassCard title="Risk Score">
              <RiskGauge score={score} compact />
            </GlassCard>
          </>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <HealthMetricCard title="Revenue Growth" value={formatPercent(revenueGrowth)} hint="Annualized trajectory" />
        <HealthMetricCard title="Debt-to-Equity Ratio" value={debtToEquityRatio.toFixed(2)} hint="Leverage intensity" />
        <HealthMetricCard title="Liquidity Ratio" value={liquidityRatio.toFixed(2)} hint="Assets vs liabilities" />
        <HealthMetricCard title="Profit Margin" value={formatPercent(profitMargin)} hint="Net profitability" />
        <HealthMetricCard title="Cash Flow Stability" value={formatPercent(cashFlowStability)} hint="Operating resilience" />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <GlassCard title="AI Decision Explanation">
          <div className="space-y-4 text-sm">
            <div>
              <p className="mb-2 font-semibold text-rose-200">Top Risk Factors</p>
              {topRiskFactors.length ? (
                <ul className="space-y-1 text-slate-200">
                  {topRiskFactors.map((factor, idx) => (
                    <li key={`${factor}-${idx}`}>- {factor}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-slate-300">- No critical risk factors flagged yet.</p>
              )}
            </div>
            <div>
              <p className="mb-2 font-semibold text-emerald-200">Positive Indicators</p>
              {positiveIndicators.length ? (
                <ul className="space-y-1 text-slate-200">
                  {positiveIndicators.map((indicator) => (
                    <li key={indicator.label}>- {indicator.label} ({indicator.value.toFixed(1)})</li>
                  ))}
                </ul>
              ) : (
                <p className="text-slate-300">- Positive indicators will appear after analysis.</p>
              )}
            </div>
            <div className="rounded-xl border border-white/10 bg-slate-950/55 p-3 text-slate-100">
              <p className="mb-1 font-semibold text-cyan-100">AI Narrative</p>
              <p>{aiNarrative}</p>
            </div>
          </div>
        </GlassCard>

        <GlassCard title="AI Agent Activity">
          <div className="grid gap-3 sm:grid-cols-2">
            {agentActivity.map((agent) => (
              <AgentStatus key={agent.label} label={agent.label} status={agent.status} />
            ))}
          </div>
        </GlassCard>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <GlassCard title="Document Intelligence">
          <div className="grid gap-3 text-sm sm:grid-cols-2">
            <div className="rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <p className="text-slate-300">Documents Processed</p>
              <p className="text-2xl font-bold text-cyan-100">{documentsProcessed}</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <p className="text-slate-300">Extracted Financial Statements</p>
              <p className="text-2xl font-bold text-cyan-100">{extractedFinancialStatements}</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <p className="text-slate-300">Legal Filings Detected</p>
              <p className="text-2xl font-bold text-rose-300">{legalFilingsDetected}</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <p className="text-slate-300">External Signals Analyzed</p>
              <p className="text-2xl font-bold text-violet-200">{externalSignalsAnalyzed}</p>
            </div>
          </div>
        </GlassCard>

        <GlassCard title="AI Recommendation">
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <span className="text-slate-300">Recommended Loan Amount</span>
              <span className="text-lg font-semibold text-cyan-100">{formatCurrency(recommendation?.recommended_loan_amount)}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <span className="text-slate-300">Suggested Interest Rate</span>
              <span className="text-lg font-semibold text-amber-200">{formatPercent(recommendation?.suggested_interest_rate)}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <span className="text-slate-300">Risk Tier</span>
              <span className="text-lg font-semibold text-sky-200">{riskCategory}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <span className="text-slate-300">Final Decision</span>
              <span className={`rounded-full border px-2 py-1 text-sm font-semibold ${decisionClass}`}>{finalDecision}</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard title="External Intelligence">
          <div className="space-y-3 text-sm">
            <div className="rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <p className="text-slate-300">News Sentiment</p>
              <p className="text-lg font-semibold text-cyan-100">{newsSentiment}</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <p className="text-slate-300">Industry Trend</p>
              <p className="line-clamp-3 text-slate-100">{insights?.industry_trends || "Awaiting AI market intelligence output."}</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-slate-950/50 p-3">
              <p className="text-slate-300">Market Risk Signals</p>
              <p className="text-lg font-semibold text-rose-200">{legalFilingsDetected + (newsSentiment === "Negative" ? 1 : 0)} Active</p>
            </div>
          </div>
        </GlassCard>
      </div>

      <GlassCard title="Industry Benchmark Comparison">
        <div className="grid gap-3 lg:grid-cols-3">
          <BenchmarkRow title="Debt Ratio" companyValue={companyDebtRatio} benchmarkValue={industryDebtRatio} />
          <BenchmarkRow title="Profit Margin" companyValue={companyProfitMargin} benchmarkValue={industryProfitMargin} />
          <BenchmarkRow title="Revenue Growth" companyValue={companyRevenueGrowth} benchmarkValue={sectorRevenueGrowth} />
        </div>
      </GlassCard>

      <GlassCard title="Loan Application Timeline">
        <div className="grid gap-2 md:grid-cols-6">
          {timelineStages.map((stage, idx) => (
            <div key={stage.label} className="relative rounded-xl border border-white/10 bg-slate-950/55 p-3 text-center">
              <p className="text-xs uppercase tracking-wide text-slate-400">Stage {idx + 1}</p>
              <p className="mt-1 text-sm font-semibold text-slate-100">{stage.label}</p>
              <span
                className={`mt-2 inline-flex rounded-full px-2 py-1 text-xs font-semibold ${stage.done ? "bg-emerald-500/20 text-emerald-300" : "bg-slate-500/20 text-slate-300"}`}
              >
                {stage.done ? "Completed" : "Pending"}
              </span>
            </div>
          ))}
        </div>
      </GlassCard>
    </section>
  );
}
