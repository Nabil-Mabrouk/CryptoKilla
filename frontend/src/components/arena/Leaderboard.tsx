import { useTranslation } from "react-i18next";
import type { ArenaPublicStatus } from "../../types/arena";

// Classement (Livre, chapitre 24.1 : capital, PnL, statut — recalculable
// depuis l'historique public, chapitre 29). Branché sur GET
// /api/arena/public/status (`data`, fourni par Landing.tsx — un seul fetch
// partagé) : tant qu'aucune saison active n'a d'agent, l'état vide honnête
// reste affiché, jamais une ligne inventée.
export default function Leaderboard({ data }: { data: ArenaPublicStatus | null }) {
  const { t } = useTranslation();
  const rows = data?.leaderboard ?? [];

  return (
    <section className="arena-section" id="classement">
      <div className="arena-section-header">
        <div>
          <h2>{t("landing.leaderboard.title")}</h2>
          <p className="subtitle">{t("landing.leaderboard.subtitle")}</p>
        </div>
      </div>
      <div className="arena-card" style={{ padding: 0, overflowX: "auto" }}>
        <table className="arena-table">
          <thead>
            <tr>
              <th>{t("landing.leaderboard.columns.dynasty")}</th>
              <th>{t("landing.leaderboard.columns.generation")}</th>
              <th>{t("landing.leaderboard.columns.capital")}</th>
              <th>{t("landing.leaderboard.columns.pnl")}</th>
              <th>{t("landing.leaderboard.columns.status")}</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr>
                <td colSpan={5}>{t("landing.leaderboard.empty")}</td>
              </tr>
            )}
            {rows.map((row, i) => (
              <tr key={`${row.dynasty}-${row.generation}-${i}`}>
                <td style={{ color: row.color }}>{row.dynasty}</td>
                <td className="mono">{row.generation}</td>
                <td className="mono">{row.capital.toFixed(2)}</td>
                <td className="mono" style={{ color: row.pnl >= 0 ? "var(--pnl-up)" : "var(--pnl-down)" }}>
                  {row.pnl >= 0 ? "+" : ""}
                  {row.pnl.toFixed(2)}
                </td>
                <td>{row.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
