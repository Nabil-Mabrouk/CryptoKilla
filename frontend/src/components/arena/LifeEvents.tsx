import { useTranslation } from "react-i18next";
import type { ArenaPublicStatus } from "../../types/arena";

// Historique public mort/renaissance (Livre, Annexe B.2, types `agent.death`/
// `agent.birth` — "orchestrateur → public", jamais un testament, N-C21-04).
// Branché sur GET /api/arena/public/status (`data`, fourni par Landing.tsx —
// un seul fetch partagé). Volontairement distinct de ChatPreview/KillaFeed :
// ceux-là restent des espaces réservés tant que Q-12 (garde-fou de toxicité
// du chat public) et Q-20 (Killa/spectateurs/notation) ne sont pas tranchées
// — ce composant-ci n'affiche que des faits structurés émis par
// l'orchestrateur, jamais un propos d'agent.
export default function LifeEvents({ data }: { data: ArenaPublicStatus | null }) {
  const { t } = useTranslation();
  const events = data?.recent_events ?? [];

  return (
    <section className="arena-section" id="vie">
      <div className="arena-section-header">
        <div>
          <h2>{t("landing.life_events.title")}</h2>
          <p className="subtitle">{t("landing.life_events.subtitle")}</p>
        </div>
      </div>
      <div className="arena-card" style={{ padding: 0, overflowX: "auto" }}>
        <table className="arena-table">
          <thead>
            <tr>
              <th>{t("landing.life_events.columns.when")}</th>
              <th>{t("landing.life_events.columns.event")}</th>
              <th>{t("landing.life_events.columns.dynasty")}</th>
              <th>{t("landing.life_events.columns.detail")}</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 && (
              <tr>
                <td colSpan={4}>{t("landing.life_events.empty")}</td>
              </tr>
            )}
            {events.map((event, i) => (
              <tr key={`${event.type}-${event.dynasty}-${event.generation}-${i}`}>
                <td className="mono">{new Date(event.timestamp).toLocaleString()}</td>
                <td>{t(event.type === "birth" ? "landing.life_events.birth" : "landing.life_events.death")}</td>
                <td style={{ color: event.color }}>
                  {event.dynasty}-{event.generation}
                </td>
                <td className="mono">
                  {event.type === "death" && event.final_stats
                    ? t("landing.life_events.death_detail", {
                        capital: event.final_stats.capital_final.toFixed(2),
                        pnl: event.final_stats.pnl_total.toFixed(2),
                        trades: event.final_stats.nb_trades,
                      })
                    : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
