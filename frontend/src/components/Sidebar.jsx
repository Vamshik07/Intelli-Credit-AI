import { motion } from "framer-motion";
import { Activity, BarChart3, Download, FileText, ShieldCheck, Upload } from "lucide-react";

const ICONS = {
  dashboard: Activity,
  company: FileText,
  documents: Upload,
  analysis: BarChart3,
  results: ShieldCheck,
  reports: Download,
  observations: FileText,
};

export default function Sidebar({ items, activePage, onNavigate }) {
  return (
    <aside className="w-full md:w-72 md:shrink-0 rounded-2xl border border-white/10 bg-slate-900/85 p-4 shadow-xl backdrop-blur-md">
      <p className="mb-2 px-1 text-xs font-semibold uppercase tracking-wide text-slate-200 md:px-2">Workflow</p>
      <nav className="flex gap-2 overflow-x-auto pb-1 md:block md:space-y-1 md:overflow-visible md:pb-0">
        {items.map((item, index) => {
          const active = activePage === item.key;
          const Icon = ICONS[item.key] || Activity;
          return (
            <motion.button
              key={item.key}
              type="button"
              onClick={() => onNavigate(item.key)}
              whileHover={{ x: 2, scale: 1.02, boxShadow: "0 10px 20px rgba(34,211,238,0.28)" }}
              whileTap={{ scale: 0.98 }}
              className={`relative flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition ${
                active
                  ? "border border-cyan-200/80 bg-gradient-to-r from-indigo-500 via-blue-500 to-cyan-400 text-white shadow-[0_12px_24px_rgba(56,189,248,0.35)]"
                  : "text-slate-200 hover:bg-white/10"
              }`}
            >
              {active ? <motion.span layoutId="sidebar-active-pill" className="absolute inset-0 rounded-lg border border-cyan-200/80 bg-gradient-to-r from-indigo-500 via-blue-500 to-cyan-400" transition={{ type: "spring", stiffness: 320, damping: 28 }} /> : null}
              <span className={`relative inline-flex h-5 w-5 items-center justify-center rounded-full text-xs ${active ? "bg-white/25" : "bg-white/10"}`}>
                {index + 1}
              </span>
              <Icon size={16} className="relative" />
              <span className="relative">{item.label}</span>
            </motion.button>
          );
        })}
      </nav>
    </aside>
  );
}
