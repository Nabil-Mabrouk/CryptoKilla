import { useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";

const API = import.meta.env.VITE_API_URL ?? "";

// Page publique (hors AdminRoute) reçue par lien email — POST /api/auth/
// accept-invite définit le mot de passe et connecte directement, même motif
// que AuthContext.login() (voir refreshUser()).
export default function AcceptInvite() {
  const { t } = useTranslation();
  const { token } = useParams<{ token: string }>();
  const { refreshUser } = useAuth();
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(false);
    if (password !== confirm || password.length < 8) {
      setError(true);
      return;
    }
    const res = await fetch(`${API}/api/auth/accept-invite`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ token, password }),
    });
    if (!res.ok) {
      setError(true);
      return;
    }
    const data = (await res.json()) as { access_token: string };
    localStorage.setItem("access_token", data.access_token);
    await refreshUser();
    navigate("/learn");
  }

  return (
    <div className="mx-auto max-w-sm">
      <div className="auth-header">
        <p className="eyebrow mono">{t("landing.hero.eyebrow")}</p>
        <h1>{t("auth.invite.title")}</h1>
        <p>{t("auth.invite.subtitle")}</p>
      </div>
      <form onSubmit={onSubmit} className="grid gap-3">
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={t("auth.invite.password")}
        />
        <input
          type="password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          placeholder={t("auth.invite.confirm")}
        />
        {error && <p className="form-error">{t("auth.invite.error")}</p>}
        <button className="btn" type="submit">
          {t("auth.invite.submit")}
        </button>
      </form>
    </div>
  );
}
