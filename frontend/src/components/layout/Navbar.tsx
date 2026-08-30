import { useCallback, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { apiFetch } from "../../api";

// Navbar — cadre constant des deux mondes (CHARTE-GRAPHIQUE.md §7) :
// toujours sombre, toujours la même, dans l'Arène comme dans les Archives.
// Monogramme filaire "CK" + micro ligne de vie (statique en
// prefers-reduced-motion, cf. landing.css). Autonome (GET /health), même
// patron que Footer.tsx.
function Monogram() {
  return (
    <svg className="nav-monogram" viewBox="0 0 32 32" width="26" height="26" aria-hidden="true">
      <rect x="1" y="1" width="30" height="30" rx="2" fill="none" stroke="currentColor" strokeWidth="1.4" />
      <path d="M11 8v16M21 8l-7.5 8 7.5 8" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="square" />
      <polyline
        className="nav-monogram-pulse"
        points="3,23 7,23 9,17 12,27 15,23 29,23"
        fill="none"
        stroke="var(--torch)"
        strokeWidth="1"
      />
    </svg>
  );
}

// Les 5 entrées fixes de navigation primaire (§7 zone 2). Arène/Classement/
// Dynasties/Saison pointent vers des ancres de la landing : aucune page
// dédiée n'existe encore (couches C1+ non commencées, cf. ARENA.md §6) —
// pas question d'anticiper des routes vides. "Le Livre" est séparé et
// distinct (voir rendu ci-dessous : seule entrée en Chronique italique).
const NAV_LINKS = [
  { key: "nav.arena", href: "/#arene" },
  { key: "nav.leaderboard", href: "/#classement" },
  { key: "nav.dynasties", href: "/#dynasties" },
  { key: "nav.season", href: "/#saison" },
];

export default function Navbar() {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuth();
  const location = useLocation();
  const [project, setProject] = useState("");
  const [modules, setModules] = useState<Record<string, boolean>>({});
  const [shrunk, setShrunk] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    apiFetch("/health")
      .then(async (r) =>
        r.ok
          ? ((await r.json()) as { project?: string; modules?: Record<string, boolean> })
          : null,
      )
      .then((data) => {
        setProject(data?.project ?? "");
        setModules(data?.modules ?? {});
      })
      .catch(() => setModules({}));
  }, []);

  useEffect(() => {
    const onScroll = () => setShrunk(window.scrollY > 120);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => setDrawerOpen(false), [location.pathname]);

  const toggleLang = useCallback(
    () => i18n.changeLanguage(i18n.language.startsWith("fr") ? "en" : "fr"),
    [i18n],
  );

  const onArchives = location.pathname.startsWith("/learn");

  return (
    <>
      <a className="skip-link" href="#main-content">
        {t("nav.skip")}
      </a>
      <nav className={`site-nav ${shrunk ? "is-shrunk" : ""}`}>
        <a className="nav-brand" href="/">
          <Monogram />
          <span className="nav-brand-name">{project || "CRYPTOKILLA"}</span>
        </a>

        <div className="nav-links" role="navigation">
          {NAV_LINKS.map((link) => (
            <a key={link.key} className="nav-link" href={link.href}>
              {t(link.key)}
            </a>
          ))}
          {modules.tutorials && (
            <a
              className="nav-link nav-link--book"
              href="/learn"
              aria-current={onArchives ? "page" : undefined}
            >
              {t("nav.learn")}
            </a>
          )}
        </div>

        <div className="nav-vitals" aria-live="off">
          <span className="nav-vital nav-metronome" title={t("nav.vitals.pre_season")}>
            <span aria-hidden="true">⏱</span> <span className="mono">—:—</span>
          </span>
          <span className="nav-vital nav-alive" title={t("nav.vitals.pre_season")}>
            <span className="nav-alive-dot" aria-hidden="true" />
            <span className="mono">—</span>
          </span>
        </div>

        <div className="nav-utils">
          {modules.i18n && (
            <button className="nav-lang" onClick={toggleLang} type="button">
              {i18n.language.startsWith("fr") ? "FR·EN" : "EN·FR"}
            </button>
          )}
          {user?.role === "admin" && (
            <a className="nav-link" href="/admin">
              {t("admin.nav")}
            </a>
          )}
          {user ? (
            <button className="btn" onClick={logout} type="button">
              {t("nav.logout")}
            </button>
          ) : (
            <a className="btn" href="/login">
              {t("nav.login")}
            </a>
          )}
        </div>

        <button
          className="nav-hamburger"
          type="button"
          aria-label={t("nav.menu")}
          aria-expanded={drawerOpen}
          onClick={() => setDrawerOpen((v) => !v)}
        >
          <span />
          <span />
          <span />
        </button>
      </nav>

      {/* Cible du skip-link : Navbar précède toujours le contenu (Landing.tsx
          et App.tsx::AppShell), donc cette ancre marque systématiquement le
          début du contenu principal sans avoir à toucher App.tsx (fichier
          châssis, hors périmètre "à vous" d'ARENA.md §2). */}
      <span id="main-content" tabIndex={-1} className="visually-hidden" />

      {drawerOpen && (
        <div className="nav-drawer" role="dialog" aria-modal="true">
          {NAV_LINKS.map((link) => (
            <a key={link.key} className="nav-drawer-link" href={link.href} onClick={() => setDrawerOpen(false)}>
              {t(link.key)}
            </a>
          ))}
          {modules.tutorials && (
            <a className="nav-drawer-link nav-drawer-link--book" href="/learn" onClick={() => setDrawerOpen(false)}>
              {t("nav.learn")}
            </a>
          )}
          <div className="nav-drawer-utils">
            {user ? (
              <button className="btn" onClick={logout} type="button">
                {t("nav.logout")}
              </button>
            ) : (
              <a className="btn" href="/login">
                {t("nav.login")}
              </a>
            )}
          </div>
        </div>
      )}
    </>
  );
}
