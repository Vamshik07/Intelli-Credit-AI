import ObservationInput from "../components/ObservationInput";
import AnimatedButton from "../components/AnimatedButton";

export default function ObservationPage({
  primaryInsightsText,
  setPrimaryInsightsText,
  creditOfficerObservations,
  setCreditOfficerObservations,
  setActivePage,
}) {
  return (
    <section className="space-y-4">
      <div className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
        <h2 className="text-xl font-semibold text-white">Credit Officer Inputs</h2>
        <p className="mt-1 text-sm text-white/80">Add qualitative findings and primary due-diligence insights for explainable decisions.</p>
      </div>
      <ObservationInput
        primaryInsightsText={primaryInsightsText}
        setPrimaryInsightsText={setPrimaryInsightsText}
        creditOfficerObservations={creditOfficerObservations}
        setCreditOfficerObservations={setCreditOfficerObservations}
      />

      <div className="flex justify-end">
        <AnimatedButton
          type="button"
          onClick={() => setActivePage("analysis")}
          className="rounded-lg bg-gradient-to-r from-fuchsia-500 via-blue-500 to-cyan-400 px-4 py-2 text-sm font-medium text-white"
          withConfetti
        >
          Next: Analysis
        </AnimatedButton>
      </div>
    </section>
  );
}
