import { useState } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../api";
import { showToast } from "../components/Toast";

export default function AuthPage({ onAuth }) {
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      let data;
      if (mode === "login") {
        data = await api.login({ email: form.email, password: form.password });
      } else {
        if (!form.name.trim()) { showToast("Name is required", "error"); setLoading(false); return; }
        data = await api.signup({ name: form.name, email: form.email, password: form.password });
      }
      localStorage.setItem("token", data.access_token);
      onAuth();
      navigate("/projects");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <span className="logo-icon">🐛</span>
          <h1>IssueHub</h1>
          <p>Lightweight bug tracker for teams</p>
        </div>

        <div className="auth-tabs">
          <button
            className={mode === "login" ? "tab active" : "tab"}
            onClick={() => setMode("login")}
          >Login</button>
          <button
            className={mode === "signup" ? "tab active" : "tab"}
            onClick={() => setMode("signup")}
          >Sign up</button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {mode === "signup" && (
            <div className="field">
              <label htmlFor="auth-name">Full name</label>
              <input
                id="auth-name"
                type="text"
                placeholder="Jane Smith"
                value={form.name}
                onChange={set("name")}
                required
              />
            </div>
          )}

          <div className="field">
            <label htmlFor="auth-email">Email</label>
            <input
              id="auth-email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={set("email")}
              required
            />
          </div>

          <div className="field">
            <label htmlFor="auth-password">Password</label>
            <input
              id="auth-password"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={set("password")}
              required
              minLength={6}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Please wait…" : mode === "login" ? "Log in" : "Create account"}
          </button>
        </form>

        <p className="auth-demo">
          Demo credentials: <code>alice@demo.com</code> / <code>password123</code>
        </p>
      </div>
    </div>
  );
}
