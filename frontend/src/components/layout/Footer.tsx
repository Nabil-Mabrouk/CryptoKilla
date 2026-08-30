import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../api";

// Footer partagé par la landing ET le reste de l'app (Chap 24, round
// theming) — minimal par défaut, à personnaliser librement (AGENTS.md).
// Pas de contenu inventé au-delà du copyright : pas de fausses mentions
// légales, pas de liens qui ne mènent nulle part. Autonome (GET /health,
// même patron que Navbar) plutôt qu'une prop `project` : usable tel quel
// sur n'importe quelle page, sans faire remonter cet état plus haut.
//
// Le bandeau disclaimer (Livre, chapitre 25, N-C25-07 : "bandeau permanent
// sur toute la plateforme") vit ici plutôt que dans un composant sticky à
// part : le Footer est déjà présent sur chaque page — pas de nouvelle
// surface à ajouter pour satisfaire cette exigence.
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
      <p className="disclaimer">{t("landing.disclaimer")}</p>
      <p>
        © {new Date().getFullYear()} {project}
      </p>
    </footer>
  );
}
