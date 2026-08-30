import { useTranslation } from "react-i18next";

// Espace réservé pour l'aperçu du chat public de l'arène (Livre, chapitre
// 8 : canal unique, public, immuable). Même statut que KillaFeed.tsx :
// aucune donnée avant la couche C1/C3, structure déjà posée.
export default function ChatPreview() {
  const { t } = useTranslation();

  return (
    <section className="arena-section" id="chat">
      <div className="arena-section-header">
        <div>
          <h2>{t("landing.chat.title")}</h2>
          <p className="subtitle">{t("landing.chat.subtitle")}</p>
        </div>
      </div>
      <p className="arena-placeholder">{t("landing.chat.empty")}</p>
    </section>
  );
}
