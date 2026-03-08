export default function AgentWorkflowViewer({ workflow }) {
  return (
    <section className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
      <h3 className="text-lg font-semibold text-white">Agent Workflow Status</h3>
      <ul className="mt-3 space-y-2 text-sm">
        {workflow.map((step) => {
          const icon = step.status === "completed" ? "OK" : step.status === "warning" ? "!" : ".";
          return (
            <li key={step.agent} className="flex items-center justify-between rounded-lg border border-white/20 bg-white/5 px-3 py-2">
              <span className="text-white/90">{step.label}</span>
              <span className={`font-medium ${step.status === "completed" ? "text-emerald-200" : step.status === "warning" ? "text-amber-200" : "text-white/70"}`}>
                {icon} {step.status.replace("_", " ")}
              </span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
