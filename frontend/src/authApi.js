const API_BASE = import.meta.env.VITE_API_BASE || "";

function csrfFromCookie() {
  const match = document.cookie.match(/(?:^|; )oncology_csrf=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const method = (options.method || "GET").toUpperCase();
  if (!["GET", "HEAD"].includes(method)) {
    const csrf = csrfFromCookie();
    if (csrf) headers["X-CSRF-Token"] = csrf;
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers, credentials: "include" });
  const raw = await res.text();
  let data = null;
  if (raw) {
    try { data = JSON.parse(raw); } catch { data = { detail: raw }; }
  }
  if (!res.ok) throw new Error(data?.detail || `Erro HTTP ${res.status}`);
  return data;
}

export const authApi = {
  me: () => request("/api/auth/me"),
  login: (username, password) => request("/api/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  logout: () => request("/api/auth/logout", { method: "POST", body: "{}" }),
  convenios: () => request("/api/auth/convenios"),
  users: () => request("/api/auth/users"),
  auditLog: (limit = 200) => request(`/api/auth/audit-log?limit=${limit}`),
  createUser: (payload) => request("/api/auth/users", { method: "POST", body: JSON.stringify(payload) }),
  updateUser: (id, payload) => request(`/api/auth/users/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
};
