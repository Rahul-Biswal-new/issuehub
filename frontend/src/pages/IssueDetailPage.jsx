import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import * as api from "../api";
import { showToast } from "../components/Toast";

const STATUS_LABELS = {
  open: "Open", in_progress: "In Progress", resolved: "Resolved", closed: "Closed",
};
const STATUSES   = ["open", "in_progress", "resolved", "closed"];
const PRIORITIES = ["low", "medium", "high", "critical"];
const PRIORITY_BADGE = {
  critical: "badge-critical", high: "badge-high", medium: "badge-medium", low: "badge-low",
};

function fmtDate(d) {
  return new Date(d).toLocaleString();
}

export default function IssueDetailPage({ user, onLogout }) {
  const { issueId }  = useParams();
  const navigate     = useNavigate();
  const [issue, setIssue]       = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [commentBody, setCommentBody] = useState("");
  const [posting, setPosting]   = useState(false);
  const [isMaintainer, setIsMaintainer] = useState(false);
  const [members, setMembers]   = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const iss = await api.getIssue(issueId);
        setIssue(iss);

        // Check if current user is maintainer
        const projs = await api.listProjects();
        const proj  = projs.find((p) => p.id === iss.project_id);
        // We detect maintainer by trying to fetch — simpler: track in user context
        // For now we load members from add-member endpoint not available for GET,
        // so we attempt a PATCH and rely on the server to reject if not maintainer.
        // Instead, store isMaintainer via a simple heuristic: reporter can be anyone.
        // We'll just always show maintainer controls and let the server enforce.
        setIsMaintainer(true); // server enforces permissions; UI shows controls for UX

        const coms = await api.listComments(issueId);
        setComments(coms);
      } catch (err) {
        showToast(err.message, "error");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [issueId]);

  async function handlePatch(patch) {
    try {
      const updated = await api.updateIssue(issueId, patch);
      setIssue(updated);
      showToast("Updated!", "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function handleComment(e) {
    e.preventDefault();
    if (!commentBody.trim()) return;
    setPosting(true);
    try {
      const c = await api.createComment(issueId, { body: commentBody });
      setComments((prev) => [...prev, c]);
      setCommentBody("");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setPosting(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Delete this issue? This cannot be undone.")) return;
    try {
      await api.deleteIssue(issueId);
      showToast("Issue deleted", "info");
      navigate(-1);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  function handleLogout() {
    api.logout().catch(() => {});
    localStorage.removeItem("token");
    onLogout();
    navigate("/");
  }

  if (loading) return (
    <div className="page">
      <div className="spinner-wrap" style={{ marginTop: "20vh" }}><div className="spinner" /></div>
    </div>
  );

  if (!issue) return (
    <div className="page"><div className="container"><p>Issue not found.</p></div></div>
  );

  return (
    <div className="page">
      <header className="topbar">
        <div className="topbar-brand">
          <span className="logo-icon">🐛</span>
          <span className="brand-name">IssueHub</span>
        </div>
        <div className="topbar-right">
          <Link to={`/projects/${issue.project_id}/issues`} className="btn btn-ghost">← Issues</Link>
          <span className="user-name">{user?.name}</span>
          <button className="btn btn-ghost" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <main className="container detail-layout">
        {/* Left: title + description + comments */}
        <div className="detail-main">
          <div className="detail-title-row">
            <h1>{issue.title}</h1>
            <button className="btn btn-danger-ghost" onClick={handleDelete}>Delete</button>
          </div>

          {issue.description && (
            <div className="detail-description">{issue.description}</div>
          )}

          <h2 className="comments-heading">Comments ({comments.length})</h2>
          <div className="comments-list">
            {comments.length === 0 && (
              <p className="no-comments">No comments yet. Be the first!</p>
            )}
            {comments.map((c) => (
              <div key={c.id} className="comment-card">
                <div className="comment-meta">
                  <span className="comment-author">{c.author?.name || "Unknown"}</span>
                  <span className="comment-date">{fmtDate(c.created_at)}</span>
                </div>
                <p className="comment-body">{c.body}</p>
              </div>
            ))}
          </div>

          <form className="comment-form" onSubmit={handleComment}>
            <textarea
              placeholder="Add a comment…"
              value={commentBody}
              onChange={(e) => setCommentBody(e.target.value)}
              rows={3}
              required
            />
            <button type="submit" className="btn btn-primary" disabled={posting}>
              {posting ? "Posting…" : "Post Comment"}
            </button>
          </form>
        </div>

        {/* Right: metadata sidebar */}
        <aside className="detail-sidebar">
          <div className="sidebar-section">
            <h3>Status</h3>
            <select
              value={issue.status}
              onChange={(e) => handlePatch({ status: e.target.value })}
              className={`status-select status-${issue.status}`}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>{STATUS_LABELS[s]}</option>
              ))}
            </select>
          </div>

          <div className="sidebar-section">
            <h3>Priority</h3>
            <select
              value={issue.priority}
              onChange={(e) => handlePatch({ priority: e.target.value })}
              className={`priority-select ${PRIORITY_BADGE[issue.priority]}`}
            >
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
              ))}
            </select>
          </div>

          <div className="sidebar-section">
            <h3>Reporter</h3>
            <span className="meta-value">{issue.reporter?.name || "—"}</span>
          </div>

          <div className="sidebar-section">
            <h3>Assignee</h3>
            <span className="meta-value">{issue.assignee?.name || "Unassigned"}</span>
          </div>

          <div className="sidebar-section">
            <h3>Created</h3>
            <span className="meta-value meta-date">{fmtDate(issue.created_at)}</span>
          </div>

          <div className="sidebar-section">
            <h3>Updated</h3>
            <span className="meta-value meta-date">{fmtDate(issue.updated_at)}</span>
          </div>
        </aside>
      </main>
    </div>
  );
}
