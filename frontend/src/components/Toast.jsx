/* Toast.jsx — simple top-right notification */
import { useState, useEffect } from "react";

let _setToast = null;

export function showToast(message, type = "info") {
  if (_setToast) _setToast({ message, type, id: Date.now() });
}

export function ToastContainer() {
  const [toast, setToast] = useState(null);
  _setToast = setToast;

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 3500);
    return () => clearTimeout(t);
  }, [toast]);

  if (!toast) return null;

  return (
    <div className={`toast toast-${toast.type}`} key={toast.id}>
      {toast.message}
    </div>
  );
}
