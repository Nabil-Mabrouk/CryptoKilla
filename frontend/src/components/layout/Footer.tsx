import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../api";

// Footer — trois colonnes (CHARTE-GRAPHIQUE.md §9) : l'Arène (ancres de la
// landing), les Archives (le Livre), la Maison (à propos/disclaimer). Pas
// de colonne contact/réseaux sociaux : aucun compte réel n'existe dans le
// Livre ni la configuration du projet — en inventer un serait une donnée
// fabriquée (R-93). Autonome (GET /health), même patron que Navbar.
export default function Footer() {
  const { t } = useTranslation();
  const [project, setProject] = useState("");

  useEffect(() => {
    apiFetch("/health")
      .then(async (r) => (r.ok ? ((await r.json()) as { project?: string }) : null))
      .then((data) => setProject(data?.project ?? ""))
      .catch(() => {});
  }, []);

  return (
    <footer className="site-footer">
      <div className="footer-columns">
        <div className="footer-col">
          <p className="footer-col-title">{t("footer.columns.arena")}</p>
          <a href="/#arene">{t("nav.arena")}</a>
          <a href="/#classement">{t("nav.leaderboard")}</a>
          <a href="/#dynasties">{t("nav.dynasties")}</a>
          <a href="/#saison">{t("nav.season")}</a>
        </div>
        <div className="footer-col">
          <p className="footer-col-title">{t("footer.columns.archives")}</p>
          <a href="/learn">{t("nav.learn")}</a>
        </div>
        <div className="footer-col">
          <p className="footer-col-title">{t("footer.columns.house")}</p>
          <a href="#disclaimer">{t("footer.about")}</a>
        </div>
      </div>

      <p className="disclaimer" id="disclaimer">
        {t("landing.disclaimer")}
      </p>
      <p className="footer-mono mono" data-testid="footer-copyright">
        <span aria-hidden="true">CK</span> · © {new Date().getFullYear()} {project}
      </p>
    </footer>
  );
}
