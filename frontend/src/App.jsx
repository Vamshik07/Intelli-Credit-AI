import { Suspense, lazy, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Sidebar from "./components/Sidebar";
import { fetchHealth, runAnalysis } from "./services/api";
import Navbar from "./components/Navbar";

const AnalysisPage = lazy(() => import("./pages/AnalysisPage"));
const CompanyRegistration = lazy(() => import("./pages/CompanyRegistration"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const DocumentUpload = lazy(() => import("./pages/DocumentUpload"));
const ObservationPage = lazy(() => import("./pages/ObservationPage"));
const ReportPage = lazy(() => import("./pages/ReportPage"));
const ResultsPage = lazy(() => import("./pages/ResultsPage"));

const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard" },
  { key: "company", label: "Company Registration" },
  { key: "documents", label: "Document Upload" },
  { key: "observations", label: "Credit Officer Notes" },
  { key: "analysis", label: "Analysis" },
  { key: "results", label: "Results" },
  { key: "reports", label: "Report Download" },
];

const AGENT_LABELS = {
  ingestion_agent: "Document Ingestion Agent",
  financial_agent: "Financial Analysis Agent",
  research_agent: "Research Agent",
  litigation_agent: "Litigation Analysis Agent",
  risk_agent: "Risk Scoring Agent",
  cam_agent: "CAM Generator Agent",
};

function defaultWorkflow() {
  return Object.entries(AGENT_LABELS).map(([agent, label]) => ({
    agent,
    label,
    status: "pending",
  }));
}

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [health, setHealth] = useState({ apiUp: false, mongoConnected: false, message: "Checking API..." });
  const [healthLoading, setHealthLoading] = useState(true);
  const [companyId, setCompanyId] = useState("");
  const [uploadSummary, setUploadSummary] = useState(null);
  const [primaryInsightsText, setPrimaryInsightsText] = useState("");
  const [creditOfficerObservations, setCreditOfficerObservations] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState("");
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [workflow, setWorkflow] = useState(defaultWorkflow());
  const workflowTimerRef = useRef(null);

  const clearWorkflowTimer = () => {
    if (workflowTimerRef.current) {
      clearInterval(workflowTimerRef.current);
      workflowTimerRef.current = null;
    }
  };

  const beginWorkflowSimulation = () => {
    clearWorkflowTimer();
    let current = 0;
    setWorkflow((prev) => prev.map((step, idx) => ({ ...step, status: idx === 0 ? "in_progress" : "pending" })));

    workflowTimerRef.current = setInterval(() => {
      current += 1;
      setWorkflow((prev) =>
        prev.map((step, idx) => {
          if (idx < current) {
            return { ...step, status: "completed" };
          }
          if (idx === current) {
            return { ...step, status: "in_progress" };
          }
          return { ...step, status: "pending" };
        })
      );

      if (current >= defaultWorkflow().length - 1) {
        clearWorkflowTimer();
      }
    }, 1200);
  };

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
        setHealth({ apiUp: false, mongoConnected: false, message: "Backend API is unreachable" });
      } finally {
        if (active) {
          setHealthLoading(false);
        }
      }
    };

    loadHealth();
    const intervalId = setInterval(loadHealth, 15000);

    return () => {
      active = false;
      clearWorkflowTimer();
      clearInterval(intervalId);
    };
  }, []);

  const onCompanyCreated = (newCompanyId) => {
    setCompanyId(newCompanyId);
    setAnalysisResult(null);
    setAnalysisError("");
    setActivePage("documents");
  };

  const onUploaded = (summary) => {
    setUploadSummary(summary);
    setActivePage("observations");
  };

  const runFullAnalysis = async () => {
    if (!companyId) {
      setAnalysisError("Create a company before analysis.");
      setActivePage("company");
      return;
    }

    setAnalysisLoading(true);
    setAnalysisError("");
    setAnalysisResult(null);
    beginWorkflowSimulation();

    try {
      const result = await runAnalysis({
        company_id: companyId,
        primary_insights: primaryInsightsText
          .split("\n")
          .map((item) => item.trim())
          .filter(Boolean),
        credit_officer_observations: creditOfficerObservations,
      });

      const mergedWorkflow = (result.agent_workflow || defaultWorkflow()).map((step) => ({
        ...step,
        label: step.label || AGENT_LABELS[step.agent] || step.agent,
        status: step.status || "completed",
      }));

      clearWorkflowTimer();
      setWorkflow(mergedWorkflow);
      setAnalysisResult(result);
      setActivePage("results");
    } catch (error) {
      clearWorkflowTimer();
      setWorkflow((prev) => prev.map((step, idx) => ({ ...step, status: idx === 0 ? "warning" : step.status })));
      setAnalysisError(error.response?.data?.detail || "Analysis failed");
      setActivePage("analysis");
    } finally {
      setAnalysisLoading(false);
    }
  };

  const sharedProps = {
    health,
    healthLoading,
    companyId,
    uploadSummary,
    primaryInsightsText,
    creditOfficerObservations,
    setPrimaryInsightsText,
    setCreditOfficerObservations,
    analysisResult,
    analysisError,
    analysisLoading,
    workflow,
    onCompanyCreated,
    onUploaded,
    runFullAnalysis,
    setActivePage,
  };

  const pages = {
    dashboard: <Dashboard {...sharedProps} />,
    company: <CompanyRegistration {...sharedProps} />,
    documents: <DocumentUpload {...sharedProps} />,
    observations: <ObservationPage {...sharedProps} />,
    analysis: <AnalysisPage {...sharedProps} />,
    results: <ResultsPage {...sharedProps} />,
    reports: <ReportPage {...sharedProps} />,
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-slate-950 to-[#020617] text-white">
      <motion.div
        animate={{ x: [0, 40, -40, 0], y: [0, -30, 30, 0] }}
        transition={{ duration: 20, repeat: Infinity }}
        className="pointer-events-none absolute -left-40 -top-40 h-[700px] w-[700px] rounded-full bg-slate-700/25 blur-3xl"
      />
      <motion.div
        animate={{ x: [0, -40, 40, 0], y: [0, 40, -40, 0] }}
        transition={{ duration: 25, repeat: Infinity }}
        className="pointer-events-none absolute -bottom-40 -right-40 h-[640px] w-[640px] rounded-full bg-blue-950/30 blur-3xl"
      />

      <div className="relative z-10 mx-auto flex max-w-[1400px] gap-4 p-4 md:p-6">
        <Sidebar items={NAV_ITEMS} activePage={activePage} onNavigate={setActivePage} />
        <main className="min-h-[calc(100vh-3rem)] flex-1 space-y-4">
          <Navbar health={health} companyId={companyId} />
          <Suspense
            fallback={
              <div className="space-y-3 rounded-2xl border border-white/10 bg-slate-900/85 p-5 shadow-xl backdrop-blur-md">
                <div className="h-4 w-1/3 rounded skeleton" />
                <div className="h-3 w-full rounded skeleton" />
                <div className="h-3 w-10/12 rounded skeleton" />
                <div className="h-28 w-full rounded skeleton" />
              </div>
            }
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={activePage}
                initial={{ opacity: 0, x: 32 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -24 }}
                transition={{ duration: 0.32, ease: "easeOut" }}
                className="h-full"
              >
                {pages[activePage]}
              </motion.div>
            </AnimatePresence>
          </Suspense>
        </main>
      </div>
    </div>
  );
}
