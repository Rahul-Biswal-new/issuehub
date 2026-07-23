import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import * as api from "./api";
import { ToastContainer } from "./components/Toast";
import AuthPage from "./pages/AuthPage";
import ProjectsPage from "./pages/ProjectsPage";
import IssuesPage from "./pages/IssuesPage";
import IssueDetailPage from "./pages/IssueDetailPage";

function PrivateRoute({ authed, children }) {
  return authed ? children : <Navigate to="/" replace />;
}

export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem("token"));
  const [user, setUser]     = useState(null);

  useEffect(() => {
    if (!authed) { setUser(null); return; }
    api.getMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("token");
        setAuthed(false);
      });
  }, [authed]);

  const onAuth   = () => setAuthed(true);
  const onLogout = () => { setAuthed(false); setUser(null); };

  return (
    <BrowserRouter>
      <ToastContainer />
      <Routes>
        <Route
          path="/"
          element={authed ? <Navigate to="/projects" replace /> : <AuthPage onAuth={onAuth} />}
        />
        <Route
          path="/projects"
          element={
            <PrivateRoute authed={authed}>
              <ProjectsPage user={user} onLogout={onLogout} />
            </PrivateRoute>
          }
        />
        <Route
          path="/projects/:projectId/issues"
          element={
            <PrivateRoute authed={authed}>
              <IssuesPage user={user} onLogout={onLogout} />
            </PrivateRoute>
          }
        />
        <Route
          path="/issues/:issueId"
          element={
            <PrivateRoute authed={authed}>
              <IssueDetailPage user={user} onLogout={onLogout} />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
