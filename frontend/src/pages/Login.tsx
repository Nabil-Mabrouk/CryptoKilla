import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";

// auth-header (landing.css, retour de revue design) : un formulaire nu ne
// portait aucune trace de marque au-delà de la couleur du bouton — un
// simple rappel eyebrow + tagline, pas une refonte en deux colonnes.
export default function Login() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(false);
    if (await login(email, password)) navigate("/learn");
    else setError(true);
  }

  return (
    <div className="mx-auto max-w-sm">
      <div className="auth-header">
        <p className="eyebrow mono">{t("landing.hero.eyebrow")}</p>
        <h1>{t("auth.login.title")}</h1>
        <p>{t("auth.login.tagline")}</p>
      </div>
      <form onSubmit={onSubmit} className="grid gap-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={t("auth.login.email")}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={t("auth.login.password")}
        />
        {error && <p className="form-error">{t("auth.login.error")}</p>}
        <button className="btn" type="submit">
          {t("auth.login.submit")}
        </button>
      </form>
    </div>
  );
}
