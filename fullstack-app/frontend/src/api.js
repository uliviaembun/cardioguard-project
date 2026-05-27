import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

/**
 * Check backend health status.
 */
export async function checkHealth() {
  const { data } = await api.get("/health");
  return data;
}

/**
 * Send patient data and get cardiovascular risk prediction.
 * @param {Object} payload – the 11 raw input fields
 */
export async function predictRisk(payload) {
  const { data } = await api.post("/predict", payload);
  return data;
}

export default api;
