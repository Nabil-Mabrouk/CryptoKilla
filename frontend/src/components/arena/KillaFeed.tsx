import { useTranslation } from "react-i18next";

// Espace réservé pour les publications de Killa (Livre, chapitre 22) —
// aucune donnée avant la couche C3 (chapitre 34, Q-19 bloquante pour C1).
// Deux cartes squelettes (jamais de texte inventé — des barres grises,
// pas de fausse citation) portant chacune une "type-pill" reprenant deux
// des 3 catégories fermées du chapitre 22.2 (alerte/récap/chronique) :
// ça préfigure la FORME des posts à venir sans fabriquer de contenu.
export default function KillaFeed() {
  const { t } = useTranslation();

  return (
    <section className="arena-section" id="killa">
      <div className="arena-section-header">
        <div>
          <h2>{t("landing.killa.title")}</h2>
          <p className="subtitle">{t("landing.killa.subtitle")}</p>
        </div>
      </div>
      <div className="arena-grid">
        <div className="killa-card">
          <div className="avatar" />
          <div className="body">
            <span className="type-pill mono">{t("landing.killa.types.alerte")}</span>
            <div className="skeleton-bar" style={{ width: "80%" }} />
            <div className="skeleton-bar" style={{ width: "55%" }} />
          </div>
        </div>
        <div className="killa-card">
          <div className="avatar" />
          <div className="body">
            <span className="type-pill mono">{t("landing.killa.types.recap")}</span>
            <div className="skeleton-bar" style={{ width: "65%" }} />
            <div className="skeleton-bar" style={{ width: "90%" }} />
          </div>
        </div>
      </div>
      <p className="arena-section-empty">{t("landing.killa.empty")}</p>
    </section>
  );
}
