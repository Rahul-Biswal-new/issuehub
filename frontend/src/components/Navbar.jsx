import { Link, useNavigate } from "react-router-dom";
import * as api from "../api";

export function Navbar({ user, onLogout, backLink, backText }) {
  const navigate = useNavigate();

  function handleLogout() {
    api.logout().catch(() => {});
    localStorage.removeItem("token");
    onLogout();
    navigate("/");
  }

  return (
    <header className="topbar">
      <div className="topbar-brand">
        <span className="logo-icon">🐛</span>
        <span className="brand-name">IssueHub</span>
      </div>
      <div className="topbar-right">
        {backLink && (
          <Link to={backLink} className="btn btn-ghost">
            {backText || "← Back"}
          </Link>
        )}
        <span className="user-name">{user?.name}</span>
        <button className="btn btn-ghost" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}
