import { useTranslation } from "react-i18next";
import manifest from "../landing-manifest.json";
import EmailCapture from "../components/blocks/EmailCapture";
import Navbar from "../components/layout/Navbar";
import Footer from "../components/layout/Footer";
import KillaFeed from "../components/arena/KillaFeed";
import ChatPreview from "../components/arena/ChatPreview";
import Leaderboard from "../components/arena/Leaderboard";
import DynastyShowcase from "../components/arena/DynastyShowcase";
import "../landing.css";

// Seuls `project`/`domain` du manifest Studio sont encore lus ici (repris
// tels quels par EmailCapture pour le POST /leads) — `skin`/`blocks`/
// `hero_image` ne le sont plus : CryptoKilla a une identité unique fixe
// (landing.css), pas un thème configurable par blocs génériques. Les
// polices ne sont plus injectées en JS par skin (ancien mécanisme
// FONT_HREF_BY_SKIN) : landing.css les charge par @import, une seule fois,
// pour toutes les pages du site (round theming), pas seulement la landing.
const data = manifest as { project: string; domain: string };

export default function Landing() {
  const { t } = useTranslation();

  return (
    <div className="landing" data-testid="landing-page">
      <Navbar />

      <section className="arena-hero">
        <p className="eyebrow">{t("landing.hero.eyebrow")}</p>
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
      </section>

      {/* Espaces réservés (Livre, chapitres 8/22/24.1/27) : aucune donnée
          réelle avant la couche C3 (chapitre 34) — structure déjà posée
          pour un branchement futur sans retoucher la mise en page. */}
      <KillaFeed />
      <ChatPreview />
      <Leaderboard />
      <DynastyShowcase />

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
