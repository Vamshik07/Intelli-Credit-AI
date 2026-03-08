import CompanyForm from "../components/CompanyForm";

export default function CompanyRegistration({ onCompanyCreated, health }) {
  return (
    <section className="space-y-4">
      <div className="rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
        <h2 className="text-xl font-semibold text-white">Company Registration</h2>
        <p className="mt-1 text-sm text-white/80">Create a company profile before uploading financial documents and running credit analysis.</p>
      </div>
      <CompanyForm
        onCreated={onCompanyCreated}
        canCreate={health.apiUp && health.mongoConnected}
        createBlockedReason={health.message}
      />
    </section>
  );
}
