import { useTranslation } from "react-i18next";

// Espace réservé pour la grille de dynasties (Livre, chapitre 27 :
// couleur constante + avatar générationnel dès qu'elles existeront).
// Même statut que les autres sections arena/* : aucune dynastie avant le
// lancement de la saison 1 (chapitre 36).
export default function DynastyShowcase() {
  const { t } = useTranslation();

  return (
    <section className="arena-section" id="dynasties">
      <div className="arena-section-header">
        <div>
          <h2>{t("landing.dynasties.title")}</h2>
          <p className="subtitle">{t("landing.dynasties.subtitle")}</p>
        </div>
      </div>
      <p className="arena-placeholder">{t("landing.dynasties.empty")}</p>
    </section>
  );
}
