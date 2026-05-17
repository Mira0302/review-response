// Environment-aware API base URL.
// In dev: Vite proxy handles /api → localhost:8000
// In prod: set VITE_API_BASE to your deployed backend URL (e.g. https://your-app.railway.app)
export const API_BASE = import.meta.env.VITE_API_BASE || "";
