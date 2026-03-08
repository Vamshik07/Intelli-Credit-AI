import CAMDownloadButton from "../components/CAMDownloadButton";

export default function ReportPage({ companyId, analysisResult }) {
  return (
    <section className="space-y-4">
      <div className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
        <h2 className="text-xl font-semibold text-white">Report Download</h2>
        <p className="mt-1 text-sm text-white/80">Download the generated Credit Appraisal Memo (DOCX/PDF).</p>
      </div>
      <CAMDownloadButton companyId={companyId} reports={analysisResult?.reports || {}} />
    </section>
  );
}
