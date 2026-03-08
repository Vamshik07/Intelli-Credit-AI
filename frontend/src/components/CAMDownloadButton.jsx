import { motion } from "framer-motion";
import { getReportDownloadUrl } from "../services/api";

export default function CAMDownloadButton({ companyId, reports = {} }) {
  if (!companyId) {
    return <p className="text-sm text-white/80">Create and analyze a company to enable report download.</p>;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="space-y-3 rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl"
    >
      <h3 className="text-lg font-semibold text-white">Credit Appraisal Memo</h3>
      <p className="text-sm text-white/80">Download the generated CAM report in DOCX or PDF format.</p>
      {reports.cam_docx_path || reports.cam_pdf_path ? (
        <p className="inline-flex items-center rounded-full bg-emerald-300/25 px-3 py-1 text-xs font-medium text-emerald-100">CAM generated and ready</p>
      ) : (
        <p className="inline-flex items-center rounded-full bg-amber-300/25 px-3 py-1 text-xs font-medium text-amber-100">Run analysis to generate CAM</p>
      )}
      <div className="flex flex-wrap gap-3">
        <motion.a
          whileHover={{ y: -2, scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          href={getReportDownloadUrl(companyId, "docx")}
          target="_blank"
          rel="noreferrer"
          className="rounded-lg bg-gradient-to-r from-fuchsia-500 via-blue-500 to-cyan-400 px-4 py-2 text-sm font-medium text-white transition"
        >
          Download DOCX
        </motion.a>
        <motion.a
          whileHover={{ y: -2, scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          href={getReportDownloadUrl(companyId, "pdf")}
          target="_blank"
          rel="noreferrer"
          className="rounded-lg bg-gradient-to-r from-cyan-400 to-emerald-400 px-4 py-2 text-sm font-medium text-slate-900 transition"
        >
          Download PDF
        </motion.a>
      </div>
      <p className="text-xs text-white/65">DOCX path: {reports.cam_docx_path || "n/a"}</p>
      <p className="text-xs text-white/65">PDF path: {reports.cam_pdf_path || "n/a"}</p>
    </motion.div>
  );
}
