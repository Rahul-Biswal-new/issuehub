import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../api";
import { showToast } from "../components/Toast";
import { Modal } from "../components/Modal";

export default function ProjectsPage({ user, onLogout }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", key: "", description: "" });
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api.listProjects()
      .then(setProjects)
      .catch((e) => showToast(e.message, "error"))
      .finally(() => setLoading(false));
  }, []);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  async function handleCreate(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const proj = await api.createProject({
        name: form.name,
        key: form.key.toUpperCase(),
        description: form.description,
      });
      setProjects((p) => [proj, ...p]);
      setShowCreate(false);
      setForm({ name: "", key: "", description: "" });
      showToast("Project created!", "success");
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
          <span className="user-name">{user?.name}</span>
          <button className="btn btn-ghost" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <main className="container">
        <div className="page-heading">
          <h1>Projects</h1>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            + New Project
          </button>
        </div>

        {loading ? (
          <div className="spinner-wrap"><div className="spinner" /></div>
        ) : projects.length === 0 ? (
          <div className="empty-state">
            <p>No projects yet. Create your first one!</p>
          </div>
        ) : (
          <div className="project-grid">
            {projects.map((p) => (
              <button
                key={p.id}
                className="project-card"
                onClick={() => navigate(`/projects/${p.id}/issues`)}
              >
                <div className="project-key">{p.key}</div>
                <div className="project-name">{p.name}</div>
                {p.description && (
                  <div className="project-desc">{p.description}</div>
                )}
                <div className="project-meta">
                  Created {new Date(p.created_at).toLocaleDateString()}
                </div>
              </button>
            ))}
          </div>
        )}
      </main>

      {showCreate && (
        <Modal title="New Project" onClose={() => setShowCreate(false)}>
          <form onSubmit={handleCreate}>
            <div className="field">
              <label htmlFor="proj-name">Project name *</label>
              <input id="proj-name" type="text" value={form.name} onChange={set("name")} required placeholder="My Awesome App" />
            </div>
            <div className="field">
              <label htmlFor="proj-key">Key * (short identifier)</label>
              <input id="proj-key" type="text" value={form.key} onChange={set("key")} required maxLength={10} placeholder="APP" style={{ textTransform: "uppercase" }} />
            </div>
            <div className="field">
              <label htmlFor="proj-desc">Description</label>
              <textarea id="proj-desc" value={form.description} onChange={set("description")} rows={3} placeholder="What is this project about?" />
            </div>
            <div className="modal-actions">
              <button type="button" className="btn btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? "Creating…" : "Create Project"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
