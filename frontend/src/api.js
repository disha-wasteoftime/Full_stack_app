import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const client = axios.create({ baseURL: API_BASE_URL });

export async function uploadBillingLog(records) {
  const res = await client.post("/billing-log/upload", { records });
  return res.data; // { log_id, visit_count, clinic_id }
}

export async function listBillingLogs() {
  const res = await client.get("/billing-logs");
  return res.data.logs;
}

export async function getReconciliation(logId) {
  const res = await client.get("/reconciliation", { params: { log_id: logId } });
  return res.data;
}

export async function getAnalytics(logId) {
  const res = await client.get("/analytics", { params: { log_id: logId } });
  return res.data;
}

export async function getNarrative(logId) {
  const res = await client.get("/narrative", { params: { log_id: logId } });
  return res.data;
}