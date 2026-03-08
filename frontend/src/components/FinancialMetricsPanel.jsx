export default function FinancialMetricsPanel({ financialData }) {
  const metrics = [
    ["Revenue", financialData?.revenue],
    ["EBITDA", financialData?.ebitda],
    ["Net Profit", financialData?.net_profit],
    ["Total Assets", financialData?.total_assets],
    ["Total Debt", financialData?.total_debt],
  ];

  return (
    <section className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
      <h3 className="text-lg font-semibold text-white">Extracted Financial Data</h3>
      <div className="mt-3 grid gap-2 sm:grid-cols-2">
        {metrics.map(([label, value]) => (
          <div key={label} className="rounded-lg border border-white/15 bg-white/5 p-3">
            <p className="text-xs uppercase tracking-wide text-white/70">{label}</p>
            <p className="text-lg font-semibold text-white">{Number(value || 0).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
