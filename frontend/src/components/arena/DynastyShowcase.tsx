import { useTranslation } from "react-i18next";

// Espace réservé pour la grille de dynasties (Livre, chapitre 27, N-C27-01 :
// une couleur constante par dynastie ; CHARTE-GRAPHIQUE.md §2 : palette de
// 8 couleurs calibrées AA). Aucune dynastie n'existe avant le lancement de
// la saison 1 — ces 8 cartes ne sont donc PAS des dynasties inventées :
// chaque carte ne porte qu'un numéro générique ("landing.dynasties.slot"),
// jamais un nom de lignée fabriqué.
const DYN_TOKENS = [
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
// (polygone régulier filaire) pour les 8 emplacements, seuls le nombre de
// côtés et la rotation varient par carte (seed = index), pour préfigurer
// honnêtement le système sans dessiner un vrai blason de lignée.
function Blason({ seed, colorVar }: { seed: number; colorVar: string }) {
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
      <polygon points={points} fill="none" stroke={`var(${colorVar})`} strokeWidth="1.5" />
    </svg>
  );
}

export default function DynastyShowcase() {
  const { t } = useTranslation();

  return (
    <section className="arena-section" id="dynasties">
      <div className="arena-section-header">
        <div>
          <h2>{t("landing.dynasties.title")}</h2>
          <p className="subtitle">{t("landing.dynasties.subtitle")}</p>
        </div>
      </div>
      <div className="arena-grid">
        {DYN_TOKENS.map((colorVar, i) => (
          <div className="dynasty-card" key={colorVar}>
            <Blason seed={i} colorVar={colorVar} />
            <div className="label mono">{t("landing.dynasties.slot", { n: i + 1 })}</div>
          </div>
        ))}
      </div>
      <p className="arena-section-empty">{t("landing.dynasties.empty")}</p>
    </section>
  );
}
