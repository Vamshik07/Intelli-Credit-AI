import FileUpload from "../components/FileUpload";

export default function DocumentUpload({ companyId, onUploaded }) {
  return (
    <section className="space-y-4">
      <div className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
        <h2 className="text-xl font-semibold text-white">Document Upload</h2>
        <p className="mt-1 text-sm text-white/80">Upload annual reports, bank statements, GST records, and other financial evidence.</p>
      </div>
      <FileUpload companyId={companyId} onUploaded={onUploaded} />
    </section>
  );
}
