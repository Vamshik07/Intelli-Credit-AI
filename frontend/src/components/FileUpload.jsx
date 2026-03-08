import { useState } from "react";
import { motion } from "framer-motion";
import { uploadDocument } from "../services/api";
import AnimatedButton from "./AnimatedButton";

export default function FileUpload({ companyId, onUploaded }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [successPulse, setSuccessPulse] = useState(false);

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!companyId || !files.length) {
      setMessage("Create a company and select files before uploading.");
      return;
    }

    setLoading(true);
    setMessage("");
    setProgress(12);

    const progressTimer = window.setInterval(() => {
      setProgress((prev) => (prev >= 88 ? prev : prev + 8));
    }, 160);

    try {
      const result = await uploadDocument({ companyId, files });
      window.clearInterval(progressTimer);
      setProgress(100);
      setMessage(`Uploaded ${result.uploaded_count || 0} file(s) successfully.`);
      setSuccessPulse(true);
      window.setTimeout(() => setSuccessPulse(false), 1100);
      onUploaded(result);
    } catch (error) {
      window.clearInterval(progressTimer);
      setProgress(0);
      setMessage(error.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className="space-y-4 rounded-2xl border border-white/20 bg-white/10 p-5 shadow-xl backdrop-blur-xl">
      <h2 className="text-lg font-semibold text-white">Document Upload</h2>
      <label
        onDrop={(event) => {
          event.preventDefault();
          setIsDragging(false);
          setFiles(Array.from(event.dataTransfer?.files || []));
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={(event) => {
          event.preventDefault();
          setIsDragging(false);
        }}
        className={`block cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition ${
          isDragging ? "border-cyan-300 bg-white/15" : "border-white/35 bg-white/5"
        }`}
      >
        <p className="font-medium text-white">Drag and drop corporate documents</p>
        <p className="mt-1 text-sm text-white/70">or click to browse files</p>
        <input type="file" multiple className="hidden" onChange={(e) => setFiles(Array.from(e.target.files || []))} />
      </label>

      {files.length ? (
        <div className="rounded-lg bg-white/10 p-3 text-sm text-white/90">
          <p className="font-medium">Selected files ({files.length})</p>
          <ul className="mt-2 list-disc pl-5">
            {files.map((file) => (
              <li key={`${file.name}-${file.lastModified}`}>{file.name}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {loading || progress > 0 ? (
        <div className="space-y-2">
          <div className="h-2 w-full overflow-hidden rounded-full bg-white/30">
            <motion.div initial={{ width: 0 }} animate={{ width: `${progress}%` }} className="h-2 rounded-full bg-cyan-300" />
          </div>
          <p className="text-xs text-white/70">Upload progress: {progress}%</p>
        </div>
      ) : null}

      <AnimatedButton type="submit" disabled={loading} className="rounded-lg bg-gradient-to-r from-fuchsia-500 via-blue-500 to-cyan-400 px-4 py-2 font-medium text-white transition disabled:opacity-60" withConfetti>
        {loading ? "Uploading..." : "Upload Documents"}
      </AnimatedButton>

      {successPulse ? <p className="text-sm font-medium text-emerald-100">Upload complete</p> : null}
      {message ? <p className="text-sm text-white/85">{message}</p> : null}
    </form>
  );
}
