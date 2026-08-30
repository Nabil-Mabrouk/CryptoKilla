import { useTranslation } from "react-i18next";

// Espace réservé pour les publications de Killa (Livre, chapitre 22) —
// aucune donnée avant la couche C3 (chapitre 34, Q-19 bloquante pour C1).
// Nouveau fichier, domaine (AMEND-04) : le brancher sur de vraies données
// plus tard se limite à remplacer l'état placeholder par un fetch, sans
// retoucher la mise en page (arena-section/arena-placeholder déjà posés).
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
      <p className="arena-placeholder">{t("landing.killa.empty")}</p>
    </section>
  );
}
