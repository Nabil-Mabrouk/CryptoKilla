import { useTranslation } from "react-i18next";
import type { ArenaPublicStatus } from "../../types/arena";

// Encart "Saison" (CHARTE-GRAPHIQUE.md §9). Branché sur GET
// /api/arena/public/status (`data`, fourni par Landing.tsx) : reflète
// honnêtement qu'une saison existe et son état — jamais le détail des
// season_params (dont certains sont `visibility: secret`, ARENA.md §3 :
// aucun coefficient de fill ni barème de pool ne doit être exposé).
export default function SeasonNotice({ data }: { data: ArenaPublicStatus | null }) {
  const { t } = useTranslation();
  const season = data?.season ?? null;

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
        <p>{season ? t("landing.season.active", { state: season.state }) : t("landing.season.empty")}</p>
      </div>
    </section>
  );
}
