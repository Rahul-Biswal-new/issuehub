/**
 * api.js — thin fetch wrapper around the IssueHub backend.
 * Token is stored in localStorage as "token".
 */

const BASE = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

async function request(method, path, body) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  // 204 No Content
  if (res.status === 204) return null;

  const data = await res.json();
  if (!res.ok) {
    const msg =
      data?.error?.message ||
      data?.detail ||
      `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

// Auth
export const signup  = (d) => request("POST", "/api/auth/signup",  d);
export const login   = (d) => request("POST", "/api/auth/login",   d);
export const logout  = ()  => request("POST", "/api/auth/logout");
export const getMe   = ()  => request("GET",  "/api/me");

// Projects
export const listProjects  = ()      => request("GET",  "/api/projects");
export const createProject = (d)     => request("POST", "/api/projects", d);
export const addMember     = (id, d) => request("POST", `/api/projects/${id}/members`, d);

// Issues
export const listIssues  = (pid, params) => {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params || {}).filter(([, v]) => v != null && v !== ""))
  ).toString();
  return request("GET", `/api/projects/${pid}/issues${qs ? `?${qs}` : ""}`);
};
export const createIssue = (pid, d)  => request("POST",  `/api/projects/${pid}/issues`, d);
export const getIssue    = (id)      => request("GET",   `/api/issues/${id}`);
export const updateIssue = (id, d)   => request("PATCH", `/api/issues/${id}`, d);
export const deleteIssue = (id)      => request("DELETE",`/api/issues/${id}`);

// Comments
export const listComments  = (id)    => request("GET",  `/api/issues/${id}/comments`);
export const createComment = (id, d) => request("POST", `/api/issues/${id}/comments`, d);
