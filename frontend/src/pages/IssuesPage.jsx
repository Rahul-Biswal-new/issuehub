import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import * as api from "../api";
import { showToast } from "../components/Toast";
import { Modal } from "../components/Modal";

const STATUSES  = ["", "open", "in_progress", "resolved", "closed"];
const PRIORITIES = ["", "critical", "high", "medium", "low"];
const SORTS = [
  { value: "created_at", label: "Newest first" },
  { value: "priority",   label: "Priority" },
  { value: "status",     label: "Status" },
];

const STATUS_LABELS = {
  open: "Open", in_progress: "In Progress", resolved: "Resolved", closed: "Closed",
};
const PRIORITY_BADGE = {
  critical: "badge-critical", high: "badge-high", medium: "badge-medium", low: "badge-low",
};

export default function IssuesPage({ user, onLogout }) {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [issues, setIssues]     = useState([]);
  const [loading, setLoading]   = useState(true);
  const [filters, setFilters]   = useState({ q: "", status: "", priority: "", sort: "created_at" });
  const [showNew, setShowNew]   = useState(false);
  const [form, setForm]         = useState({ title: "", description: "", priority: "medium", assignee_id: "" });
  const [saving, setSaving]     = useState(false);
  const [projectName, setProjectName] = useState("");

  const loadIssues = useCallback(() => {
    setLoading(true);
    api.listIssues(projectId, { q: filters.q, status: filters.status, priority: filters.priority, sort: filters.sort })
      .then((data) => { setIssues(data); })
      .catch((e) => showToast(e.message, "error"))
      .finally(() => setLoading(false));
  }, [projectId, filters]);

  useEffect(() => {
    // Get project name from the issues list or projects list
    api.listProjects()
      .then((ps) => {
        const p = ps.find((x) => String(x.id) === String(projectId));
        if (p) setProjectName(p.name);
      })
      .catch(() => {});
  }, [projectId]);

  useEffect(() => { loadIssues(); }, [loadIssues]);

  const setFilter = (k) => (e) => setFilters((f) => ({ ...f, [k]: e.target.value }));
  const setFormField = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  async function handleCreate(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const issue = await api.createIssue(projectId, {
        title: form.title,
        description: form.description,
        priority: form.priority,
        assignee_id: form.assignee_id ? Number(form.assignee_id) : null,
      });
      setIssues((prev) => [issue, ...prev]);
      setShowNew(false);
      setForm({ title: "", description: "", priority: "medium", assignee_id: "" });
      showToast("Issue created!", "success");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setSaving(false);
    }
  }

  function handleLogout() {
    api.logout().catch(() => {});
    localStorage.removeItem("token");
    onLogout();
    navigate("/");
  }

  return (
    <div className="page">
      <header className="topbar">
        <div className="topbar-brand">
          <span className="logo-icon">🐛</span>
          <span className="brand-name">IssueHub</span>
        </div>
        <div className="topbar-right">
          <Link to="/projects" className="btn btn-ghost">← Projects</Link>
          <span className="user-name">{user?.name}</span>
          <button className="btn btn-ghost" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <main className="container">
        <div className="page-heading">
          <div>
            <h1>{projectName || `Project #${projectId}`}</h1>
            <p className="subtitle">{issues.length} issue{issues.length !== 1 ? "s" : ""}</p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowNew(true)}>+ New Issue</button>
        </div>

        {/* Filters */}
        <div className="filters-bar">
          <input
            className="search-input"
            type="search"
            placeholder="Search issues…"
            value={filters.q}
            onChange={setFilter("q")}
          />
          <select value={filters.status} onChange={setFilter("status")}>
            <option value="">All statuses</option>
            {STATUSES.slice(1).map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
          </select>
          <select value={filters.priority} onChange={setFilter("priority")}>
            <option value="">All priorities</option>
            {PRIORITIES.slice(1).map((p) => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
          </select>
          <select value={filters.sort} onChange={setFilter("sort")}>
            {SORTS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>

        {/* Issue list */}
        {loading ? (
          <div className="spinner-wrap"><div className="spinner" /></div>
        ) : issues.length === 0 ? (
          <div className="empty-state">No issues match your filters.</div>
        ) : (
          <div className="issue-list">
            {issues.map((issue) => (
              <button
                key={issue.id}
                className="issue-row"
                onClick={() => navigate(`/issues/${issue.id}`)}
              >
                <div className="issue-left">
                  <span className={`badge ${PRIORITY_BADGE[issue.priority]}`}>{issue.priority}</span>
                  <span className="issue-title">{issue.title}</span>
                </div>
                <div className="issue-right">
                  <span className={`status-chip status-${issue.status}`}>{STATUS_LABELS[issue.status]}</span>
                  {issue.assignee && <span className="assignee-chip">{issue.assignee.name}</span>}
                  <span className="issue-date">{new Date(issue.created_at).toLocaleDateString()}</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </main>

      {showNew && (
        <Modal title="New Issue" onClose={() => setShowNew(false)}>
          <form onSubmit={handleCreate}>
            <div className="field">
              <label htmlFor="issue-title">Title *</label>
              <input id="issue-title" type="text" value={form.title} onChange={setFormField("title")} required placeholder="Brief description of the bug" />
            </div>
            <div className="field">
              <label htmlFor="issue-desc">Description</label>
              <textarea id="issue-desc" value={form.description} onChange={setFormField("description")} rows={4} placeholder="Steps to reproduce, expected behavior, etc." />
            </div>
            <div className="field">
              <label htmlFor="issue-priority">Priority</label>
              <select id="issue-priority" value={form.priority} onChange={setFormField("priority")}>
                {PRIORITIES.slice(1).map((p) => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
              </select>
            </div>
            <div className="modal-actions">
              <button type="button" className="btn btn-ghost" onClick={() => setShowNew(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? "Creating…" : "Create Issue"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
