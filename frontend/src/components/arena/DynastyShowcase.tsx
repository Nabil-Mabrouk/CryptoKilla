import { useTranslation } from "react-i18next";
import type { ArenaPublicStatus } from "../../types/arena";

// Grille de dynasties (Livre, chapitre 27, N-C27-01 : une couleur constante
// par dynastie ; CHARTE-GRAPHIQUE.md §2 : palette de 8 couleurs calibrées
// AA). Branché sur GET /api/arena/public/status (`data`, fourni par
// Landing.tsx) : si de vraies dynasties existent, leurs blasons/couleurs
// réels remplacent les 8 cartes fantômes — jamais l'inverse (pas de nom de
// lignée inventé quand aucune dynastie n'existe encore).
const GHOST_DYN_TOKENS = [
  "--dyn-ember",
  "--dyn-glacier",
  "--dyn-venom",
  "--dyn-orchid",
  "--dyn-gold",
  "--dyn-rose",
  "--dyn-cyanide",
  "--dyn-cobalt",
];

// Blason : forme géométrique générative simple (§4) — même construction
// (polygone régulier filaire), seuls le nombre de côtés et la rotation
// varient (seed = index/nom), pour préfigurer honnêtement le système sans
// dessiner un vrai blason de lignée.
function Blason({ seed, color }: { seed: number; color: string }) {
  const sides = 5 + (seed % 3);
  const rotation = (seed * 47) % 360;
  const points = Array.from({ length: sides }, (_, i) => {
    const angle = (Math.PI * 2 * i) / sides - Math.PI / 2;
    const x = 16 + 12 * Math.cos(angle);
    const y = 16 + 12 * Math.sin(angle);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  return (
    <svg
      className="dynasty-blason"
      viewBox="0 0 32 32"
      width="36"
      height="36"
      style={{ transform: `rotate(${rotation}deg)` }}
      aria-hidden="true"
    >
      <polygon points={points} fill="none" stroke={color} strokeWidth="1.5" />
    </svg>
  );
}

function seedFromName(name: string): number {
  let acc = 0;
  for (let i = 0; i < name.length; i++) acc += name.charCodeAt(i);
  return acc;
}

export default function DynastyShowcase({ data }: { data: ArenaPublicStatus | null }) {
  const { t } = useTranslation();
  const dynasties = data?.dynasties ?? [];

  return (
    <section className="arena-section" id="dynasties">
      <div className="arena-section-header">
        <div>
          <h2>{t("landing.dynasties.title")}</h2>
          <p className="subtitle">{t("landing.dynasties.subtitle")}</p>
        </div>
      </div>
      <div className="arena-grid">
        {dynasties.length > 0
          ? dynasties.map((d) => (
              <div className="dynasty-card" key={d.name}>
                <Blason seed={seedFromName(d.name)} color={d.color} />
                <div className="label mono" style={{ color: d.color }}>
                  {d.name}
                </div>
              </div>
            ))
          : GHOST_DYN_TOKENS.map((colorVar, i) => (
              <div className="dynasty-card" key={colorVar}>
                <Blason seed={i} color={`var(${colorVar})`} />
                <div className="label mono">{t("landing.dynasties.slot", { n: i + 1 })}</div>
              </div>
            ))}
      </div>
      {dynasties.length === 0 && <p className="arena-section-empty">{t("landing.dynasties.empty")}</p>}
    </section>
  );
}
