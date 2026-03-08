import { motion } from "framer-motion";

export default function Navbar({ health, companyId }) {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="z-20 rounded-2xl border border-white/10 bg-slate-900/85 backdrop-blur-md"
    >
      <div className="mx-auto flex flex-wrap items-center gap-3 px-4 py-3 md:px-6">
        <div>
          <h1 className="text-lg font-semibold tracking-tight text-white">INTELLI-CREDIT</h1>
          <p className="text-xs font-medium text-slate-200">AI Corporate Credit Appraisal Engine</p>
        </div>
      </div>
    </motion.header>
  );
}
