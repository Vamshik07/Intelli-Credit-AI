import { useEffect, useState } from "react";
import AnalysisRunner from "../components/AnalysisRunner";
import CompanyForm from "../components/CompanyForm";
import DocumentUploader from "../components/DocumentUploader";
import ReportViewer from "../components/ReportViewer";
import { fetchHealth, fetchReport } from "../services/api";

export default function DashboardPage() {
  const [companyId, setCompanyId] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [latestReport, setLatestReport] = useState(null);
  const [health, setHealth] = useState({ apiUp: false, mongoConnected: false, message: "Checking API..." });

  useEffect(() => {
    let active = true;

    const loadHealth = async () => {
      try {
        const data = await fetchHealth();
        if (!active) {
          return;
        }

        const mongoConnected = data?.mongodb === "connected";
        setHealth({
          apiUp: true,
          mongoConnected,
          message: mongoConnected ? "API and MongoDB connected" : "API is up, but MongoDB is disconnected",
        });
      } catch {
        if (!active) {
          return;
        }

        setHealth({
          apiUp: false,
          mongoConnected: false,
          message: "Backend API is unreachable",
        });
      }
    };

    loadHealth();
    const intervalId = setInterval(loadHealth, 15000);

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, []);

  const onCompanyCreated = (newCompanyId) => {
    setCompanyId(newCompanyId);
    setAnalysisResult(null);
    setLatestReport(null);
  };

  const onAnalysisComplete = async (result) => {
    setAnalysisResult(result);
    try {
      const report = await fetchReport(companyId);
      setLatestReport(report);
    } catch {
      setLatestReport(null);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-100 to-white p-4 md:p-8">
      <div className="mx-auto max-w-5xl space-y-4">
        <header className="rounded-xl border bg-white p-5 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-900">INTELLI-CREDIT AI</h1>
          <p className="text-slate-600">Corporate credit appraisal engine using FastAPI, LangGraph, MongoDB, and dual-LLM orchestration.</p>
          <p className="mt-2 text-sm text-slate-700">Current Company ID: {companyId || "not created"}</p>
          <p className={`mt-2 text-sm ${health.apiUp && health.mongoConnected ? "text-emerald-700" : "text-amber-700"}`}>{health.message}</p>
        </header>

        <div className="grid gap-4 md:grid-cols-2">
          <CompanyForm
            onCreated={onCompanyCreated}
            canCreate={health.apiUp && health.mongoConnected}
            createBlockedReason={health.message}
          />
          <DocumentUploader companyId={companyId} onUploaded={() => undefined} />
        </div>

        <AnalysisRunner companyId={companyId} onComplete={onAnalysisComplete} />
        <ReportViewer analysisResult={analysisResult} latestReport={latestReport} />
      </div>
    </main>
  );
}
