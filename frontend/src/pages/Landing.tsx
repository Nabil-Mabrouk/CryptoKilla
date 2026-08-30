import { useTranslation } from "react-i18next";
import manifest from "../landing-manifest.json";
import EmailCapture from "../components/blocks/EmailCapture";
import Navbar from "../components/layout/Navbar";
import Footer from "../components/layout/Footer";
import KillaFeed from "../components/arena/KillaFeed";
import ChatPreview from "../components/arena/ChatPreview";
import Leaderboard from "../components/arena/Leaderboard";
import DynastyShowcase from "../components/arena/DynastyShowcase";
import SeasonNotice from "../components/arena/SeasonNotice";
import "../landing.css";

// Seuls `project`/`domain` du manifest Studio sont encore lus ici (repris
// tels quels par EmailCapture pour le POST /leads). CryptoKilla a une
// identité unique fixe (CHARTE-GRAPHIQUE.md), pas un thème configurable
// par blocs génériques.
const data = manifest as { project: string; domain: string };

// Ticker décoratif (landing.css .ticker) : uniquement des NOMS de paires,
// jamais un prix fabriqué (R-93). Dupliqué une fois pour la boucle CSS.
const TICKER_PAIRS = ["BTC/EUR", "ETH/EUR", "SOL/EUR"];

export default function Landing() {
  const { t } = useTranslation();

  return (
    <div className="landing" data-testid="landing-page">
      <Navbar />

      <section className="arena-hero">
        <p className="eyebrow mono">{t("landing.hero.eyebrow")}</p>
        <h1>{t("landing.hero.title")}</h1>
        <p className="subtitle">{t("landing.hero.subtitle")}</p>
        <div className="actions">
          <a className="btn" href="#email-capture">
            {t("landing.hero.cta_waitlist")}
          </a>
          <a className="btn btn--ghost" href="/learn">
            {t("landing.hero.cta_book")}
          </a>
        </div>

        {/* Signature de la charte (§1 : "la ligne de vie") — préfiguration
            honnête, pas une vraie courbe : un tracé plat et gris, jamais
            une donnée inventée qui pourrait passer pour un vrai agent
            vivant. S'allumera dans les couleurs de dynastie au lancement
            de la saison 1. */}
        <div className="hero-lifeline" aria-hidden="true">
          <svg viewBox="0 0 400 24" preserveAspectRatio="none">
            <line x1="0" y1="12" x2="400" y2="12" />
          </svg>
        </div>
        <p className="hero-lifeline-caption">{t("landing.hero.lifeline_caption")}</p>
      </section>

      <div className="ticker" aria-hidden="true">
        <div className="ticker-track">
          {[...TICKER_PAIRS, ...TICKER_PAIRS].map((pair, i) => (
            <span key={i}>{pair}</span>
          ))}
        </div>
      </div>

      {/* Espaces réservés (Livre, chapitres 8/22/24.1/27) : aucune donnée
          réelle avant la couche C3 (chapitre 34) — structure déjà posée
          pour un branchement futur sans retoucher la mise en page. */}
      <ChatPreview />
      <Leaderboard />
      <KillaFeed />
      <DynastyShowcase />
      <SeasonNotice />

      <EmailCapture
        block={{
          type: "email_capture",
          headline: t("landing.waitlist.headline"),
          subhead: t("landing.waitlist.subhead"),
          cta: t("landing.waitlist.cta"),
          field_placeholder: t("landing.waitlist.placeholder"),
        }}
        project={data.project}
        domain={data.domain}
      />

      <Footer />
    </div>
  );
}
