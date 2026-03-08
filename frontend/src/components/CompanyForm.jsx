import { useState } from "react";
import { createCompany } from "../services/api";
import AnimatedButton from "./AnimatedButton";

export default function CompanyForm({ onCreated, canCreate = true, createBlockedReason = "" }) {
  const [form, setForm] = useState({
    name: "",
    industry: "",
    cin: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [createdCompanyId, setCreatedCompanyId] = useState("");

  const onChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!canCreate) {
      setError(createBlockedReason || "Database unavailable. Please retry later.");
      setCreatedCompanyId("");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const result = await createCompany(form);
      const newCompanyId = result?.company_id;
      if (!newCompanyId) {
        throw new Error("Missing company_id in response");
      }
      setCreatedCompanyId(newCompanyId);
      onCreated(newCompanyId);
    } catch (err) {
      setCreatedCompanyId("");
      setError(err.response?.data?.detail || "Unable to create company");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
      <h2 className="text-lg font-semibold text-white">1. Create Company</h2>
      <input
        name="name"
        value={form.name}
        onChange={onChange}
        placeholder="Company Name"
        className="w-full rounded-lg border border-white/30 bg-white/10 p-2.5 text-white placeholder:text-white/60"
        required
      />
      <input
        name="industry"
        value={form.industry}
        onChange={onChange}
        placeholder="Industry"
        className="w-full rounded-lg border border-white/30 bg-white/10 p-2.5 text-white placeholder:text-white/60"
        required
      />
      <input name="cin" value={form.cin} onChange={onChange} placeholder="CIN" className="w-full rounded-lg border border-white/30 bg-white/10 p-2.5 text-white placeholder:text-white/60" required />
      <AnimatedButton
        type="submit"
        disabled={loading || !canCreate}
        className="rounded-lg bg-gradient-to-r from-fuchsia-500 via-blue-500 to-cyan-400 px-4 py-2 text-white disabled:opacity-60"
      >
        {loading ? "Creating..." : "Create Company"}
      </AnimatedButton>
      {createdCompanyId ? <p className="text-sm text-emerald-100">Company created: {createdCompanyId}</p> : null}
      {!canCreate ? <p className="text-sm text-amber-100">{createBlockedReason || "Company creation is temporarily unavailable."}</p> : null}
      {error ? <p className="text-sm text-rose-100">{error}</p> : null}
    </form>
  );
}
