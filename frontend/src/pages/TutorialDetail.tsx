import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../api";

interface LessonSummary {
  id: number;
  title: string;
  order: number;
}

interface TutorialDetailData {
  id: number;
  title: string;
  slug: string;
  lang: string;
  access_role: string;
  lessons: LessonSummary[];
}

const ROMAN: [number, string][] = [
  [1000, "M"], [900, "CM"], [500, "D"], [400, "CD"], [100, "C"], [90, "XC"],
  [50, "L"], [40, "XL"], [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"],
];
function toRoman(n: number): string {
  let out = "";
  let rest = n;
  for (const [value, symbol] of ROMAN) {
    while (rest >= value) {
      out += symbol;
      rest -= value;
    }
  }
  return out;
}

// Liste des leçons d'un tutoriel (Chap 11) — GET /api/content/tutorials/{slug}
// est public, le contrôle d'accès réel se fait par leçon (LessonView).
// Monde Archives (CHARTE-GRAPHIQUE.md §9) : "table des matières de
// l'outline : chaque partie précédée de son numéro en romain, hairlines."
export default function TutorialDetail() {
  const { t } = useTranslation();
  const { slug } = useParams<{ slug: string }>();
  const [tutorial, setTutorial] = useState<TutorialDetailData | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    setTutorial(null);
    setNotFound(false);
    apiFetch(`/api/content/tutorials/${slug}`).then(async (r) => {
      if (r.ok) setTutorial((await r.json()) as TutorialDetailData);
      else setNotFound(true);
    });
  }, [slug]);

  if (notFound)
    return (
      <div className="world-archives">
        <p className="archives-error">{t("learn.detail.notFound")}</p>
      </div>
    );
  if (!tutorial)
    return (
      <div className="world-archives">
        <p>{t("learn.detail.loading")}</p>
      </div>
    );

  return (
    <div className="world-archives">
      <Link to="/learn" className="archives-back">
        {t("learn.detail.back")}
      </Link>
      <h1 className="archives-title">{tutorial.title}</h1>
      <ol className="archives-toc-list">
        {[...tutorial.lessons]
          .sort((a, b) => a.order - b.order)
          .map((lesson, i) => (
            <li key={lesson.id} className="list-row archives-toc-item">
              <span className="archives-toc-num mono">{toRoman(i + 1)}</span>
              <Link to={`/learn/${tutorial.slug}/lessons/${lesson.id}`}>{lesson.title}</Link>
            </li>
          ))}
      </ol>
    </div>
  );
}
