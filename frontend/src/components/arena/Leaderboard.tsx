import { useTranslation } from "react-i18next";

// Espace réservé pour le classement (Livre, chapitre 24.1 : capital, PnL,
// statut — recalculable depuis l'historique public, chapitre 29). Les
// colonnes sont déjà posées pour que le branchement futur sur de vraies
// données n'ait qu'à remplacer la ligne d'état vide par une liste réelle.
export default function Leaderboard() {
  const { t } = useTranslation();

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
            <tr>
              <td colSpan={5}>{t("landing.leaderboard.empty")}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}
