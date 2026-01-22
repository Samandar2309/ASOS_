import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000", // backend
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
