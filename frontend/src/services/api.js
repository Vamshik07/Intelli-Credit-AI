import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

export async function createCompany(payload) {
  const { data } = await api.post("/api/company/create", payload);
  return data;
}

export async function uploadDocument({ companyId, file, files }) {
  const formData = new FormData();
  formData.append("company_id", companyId);

  const fileList = Array.isArray(files) ? files : file ? [file] : [];
  fileList.forEach((selectedFile) => formData.append("files", selectedFile));

  const { data } = await api.post("/api/document/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function runAnalysis(payload) {
  const { data } = await api.post("/api/analysis/run", payload);
  return data;
}

export async function fetchCompany(companyId) {
  const { data } = await api.get(`/api/company/${companyId}`);
  return data;
}

export async function fetchReport(companyId) {
  const { data } = await api.get(`/api/report/${companyId}`);
  return data;
}

export function getReportDownloadUrl(companyId, format) {
  return `${API_BASE_URL}/api/report/${companyId}/download/${format}`;
}

export async function fetchHealth() {
  const { data } = await api.get("/");
  return data;
}

export async function fetchCompanyStats() {
  const { data } = await api.get("/api/company/stats");
  return data;
}
