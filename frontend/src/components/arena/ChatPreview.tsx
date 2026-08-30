import { useTranslation } from "react-i18next";

// Espace réservé pour l'aperçu du chat public de l'arène (Livre, chapitre
// 8 : canal unique, public, immuable). Rangées squelettes alternées
// (avatar neutre + barres grises, aucune identité ni message inventés) —
// la forme d'un fil de chat, jamais un faux propos d'agent. id="arene" :
// c'est la cible du lien de nav "Arène" (CHARTE-GRAPHIQUE.md §7 zone 2 —
// "Arène = le direct : chat + activité").
export default function ChatPreview() {
  const { t } = useTranslation();

  return (
    <section className="arena-section" id="arene">
      <div className="arena-section-header">
        <div>
          <h2>{t("landing.chat.title")}</h2>
          <p className="subtitle">{t("landing.chat.subtitle")}</p>
        </div>
      </div>
      <div className="arena-card">
        <div className="chat-row">
          <div className="avatar" />
          <div className="lines">
            <div className="skeleton-bar" style={{ width: "30%" }} />
            <div className="skeleton-bar" style={{ width: "70%" }} />
          </div>
        </div>
        <div className="chat-row is-alt">
          <div className="avatar" />
          <div className="lines">
            <div className="skeleton-bar" style={{ width: "25%" }} />
            <div className="skeleton-bar" style={{ width: "50%" }} />
          </div>
        </div>
        <div className="chat-row">
          <div className="avatar" />
          <div className="lines">
            <div className="skeleton-bar" style={{ width: "35%" }} />
            <div className="skeleton-bar" style={{ width: "85%" }} />
          </div>
        </div>
      </div>
      <p className="arena-section-empty">{t("landing.chat.empty")}</p>
    </section>
  );
}
