import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../api";
import { showToast } from "../components/Toast";
import { Modal } from "../components/Modal";
import { Navbar } from "../components/Navbar";

export default function ProjectsPage({ user, onLogout }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", key: "", description: "" });
  const [saving, setSaving] = useState(false);

  // Members modal state
  const [managingProject, setManagingProject] = useState(null);
  const [members, setMembers] = useState([]);
  const [membersLoading, setMembersLoading] = useState(false);
  const [memberForm, setMemberForm] = useState({ email: "", role: "member" });
  const [addingMember, setAddingMember] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    api.listProjects()
      .then(setProjects)
      .catch((e) => showToast(e.message, "error"))
      .finally(() => setLoading(false));
  }, []);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const setMem = (k) => (e) => setMemberForm((f) => ({ ...f, [k]: e.target.value }));

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

  function openMembersModal(e, project) {
    e.stopPropagation();
    setManagingProject(project);
    setMembersLoading(true);
    setMemberForm({ email: "", role: "member" });
    api.listMembers(project.id)
      .then(setMembers)
      .catch((err) => showToast(err.message, "error"))
      .finally(() => setMembersLoading(false));
  }

  async function handleAddMember(e) {
    e.preventDefault();
    if (!memberForm.email.trim()) return;
    setAddingMember(true);
    try {
      const newMember = await api.addMember(managingProject.id, {
        email: memberForm.email.trim(),
        role: memberForm.role,
      });
      setMembers((prev) => [...prev, newMember]);
      setMemberForm({ email: "", role: "member" });
      showToast("Member added successfully!", "success");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setAddingMember(false);
    }
  }

  return (
    <div className="page">
      <Navbar user={user} onLogout={onLogout} />

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
            <div style={{ fontSize: "2.5rem", marginBottom: "12px" }}>📁</div>
            <h2>No projects found</h2>
            <p>Get started by creating your first project to track issues.</p>
          </div>
        ) : (
          <div className="project-grid">
            {projects.map((p) => (
              <button
                key={p.id}
                className="project-card"
                onClick={() => navigate(`/projects/${p.id}/issues`)}
              >
                <div className="project-card-header">
                  <span className="project-key">{p.key}</span>
                  <span
                    className="btn btn-ghost btn-sm"
                    onClick={(e) => openMembersModal(e, p)}
                    title="Manage project members"
                  >
                    👥 {p.members_count != null ? p.members_count : "Members"}
                  </span>
                </div>
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

      {managingProject && (
        <Modal title={`Members — ${managingProject.name}`} onClose={() => setManagingProject(null)}>
          {membersLoading ? (
            <div className="spinner-wrap"><div className="spinner" /></div>
          ) : (
            <div>
              <div className="member-list">
                {members.length === 0 ? (
                  <p className="no-comments">No members found.</p>
                ) : (
                  members.map((m) => (
                    <div key={m.user_id} className="member-item">
                      <div className="member-info">
                        <span className="member-name">{m.user?.name || "User"}</span>
                        <span className="member-email">{m.user?.email}</span>
                      </div>
                      <span className="member-role">{m.role}</span>
                    </div>
                  ))
                )}
              </div>

              <form onSubmit={handleAddMember} className="add-member-form">
                <h3>Add Member</h3>
                <div className="field">
                  <label htmlFor="member-email">User Email *</label>
                  <input
                    id="member-email"
                    type="email"
                    placeholder="colleague@example.com"
                    value={memberForm.email}
                    onChange={setMem("email")}
                    required
                  />
                </div>
                <div className="field">
                  <label htmlFor="member-role">Role</label>
                  <select id="member-role" value={memberForm.role} onChange={setMem("role")}>
                    <option value="member">Member</option>
                    <option value="maintainer">Maintainer</option>
                  </select>
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn btn-ghost" onClick={() => setManagingProject(null)}>Done</button>
                  <button type="submit" className="btn btn-primary" disabled={addingMember}>
                    {addingMember ? "Adding…" : "Add Member"}
                  </button>
                </div>
              </form>
            </div>
          )}
        </Modal>
      )}
    </div>
  );
}

