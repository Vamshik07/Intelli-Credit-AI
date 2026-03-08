import { useEffect, useState } from "react";
import { uploadDocument } from "../services/api";

export default function DocumentUploader({ companyId, onUploaded }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  const setSelectedFiles = (selectedFiles) => {
    if (!selectedFiles || !selectedFiles.length) {
      return;
    }
    setFiles(selectedFiles);
    setMessage(`Selected ${selectedFiles.length} file(s)`);
  };

  useEffect(() => {
    const onWindowPaste = (event) => {
      const clipboardItems = event.clipboardData?.items || [];
      const pastedFiles = [];
      for (const item of clipboardItems) {
        if (item.kind === "file") {
          const pastedFile = item.getAsFile();
          if (pastedFile) {
            pastedFiles.push(pastedFile);
          }
        }
      }
      if (pastedFiles.length) {
        setSelectedFiles(pastedFiles);
      }
    };

    window.addEventListener("paste", onWindowPaste);
    return () => window.removeEventListener("paste", onWindowPaste);
  }, []);

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!companyId || !files.length) {
      setMessage("Create company and select file(s) first.");
      return;
    }

    setLoading(true);
    setMessage("");
    try {
      const result = await uploadDocument({ companyId, files });
      const count = result.uploaded_count || 0;
      setMessage(`Uploaded ${count} file(s) successfully`);
      onUploaded(result);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(event.dataTransfer?.files || []);
    setSelectedFiles(droppedFiles);
  };

  const onDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = (event) => {
    event.preventDefault();
    setIsDragging(false);
  };

  return (
    <form onSubmit={onSubmit} className="space-y-3 rounded-xl border bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">2. Upload Documents</h2>

      <label
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        className={`block w-full cursor-pointer rounded border-2 border-dashed p-4 text-sm ${
          isDragging ? "border-blue-500 bg-blue-50" : "border-slate-300 bg-slate-50"
        }`}
      >
        <div className="space-y-1 text-center">
          <p className="font-medium text-slate-800">Drag and drop document(s) here</p>
          <p className="text-slate-600">or click to browse files</p>
          <p className="text-slate-500">Tip: Use Ctrl or Shift while selecting to pick multiple files</p>
        </div>
        <input
          type="file"
          name="files"
          multiple
          onChange={(e) => setSelectedFiles(Array.from(e.target.files || []))}
          className="hidden"
        />
      </label>

      {files.length ? (
        <div className="text-sm text-slate-700">
          <p className="font-medium">Ready ({files.length}):</p>
          <ul className="list-disc pl-5">
            {files.map((selectedFile) => (
              <li key={`${selectedFile.name}-${selectedFile.lastModified}`}>{selectedFile.name}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <button type="submit" disabled={loading} className="rounded bg-accent px-4 py-2 text-white disabled:opacity-60">
        {loading ? "Uploading..." : "Upload"}
      </button>
      {message ? <p className="text-sm text-slate-700">{message}</p> : null}
    </form>
  );
}
