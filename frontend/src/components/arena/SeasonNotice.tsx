import { useTranslation } from "react-i18next";

// Espace réservé "Saison" (CHARTE-GRAPHIQUE.md §9 : "les règles publiques
// en mise en page Archives (papier) encapsulée dans l'Arène — un document
// affiché au mur du Colisée"). `season_params` n'existe pas encore en base
// (couche C1 non commencée) : aucun paramètre n'est donc affiché ici, juste
// un texte honnête annonçant leur publication future.
export default function SeasonNotice() {
  const { t } = useTranslation();

  return (
    <section className="arena-section" id="saison">
      <div className="arena-section-header">
        <div>
          <h2>{t("landing.season.title")}</h2>
          <p className="subtitle">{t("landing.season.subtitle")}</p>
        </div>
      </div>
      <div className="season-document">
        <p className="season-document-eyebrow mono">{t("landing.season.eyebrow")}</p>
        <p>{t("landing.season.empty")}</p>
      </div>
    </section>
  );
}
