import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../api";

interface Tutorial {
  id: number;
  title: string;
  slug: string;
  lang: string;
  access_role: string;
}

// Catalogue public : ne montre que les cours de la langue courante (Chap 11).
// Monde Archives (CHARTE-GRAPHIQUE.md §9) : fond papier, Chronique.
export default function Learn() {
  const { t, i18n } = useTranslation();
  const [tutorials, setTutorials] = useState<Tutorial[]>([]);

  useEffect(() => {
    const lang = i18n.language.split("-")[0];
    apiFetch(`/api/content/tutorials?lang=${lang}`).then(async (r) => {
      if (r.ok) setTutorials((await r.json()) as Tutorial[]);
    });
  }, [i18n.language]);

  return (
    <div className="world-archives">
      <h1 className="archives-title">{t("learn.title")}</h1>
      <ul className="archives-list">
        {tutorials.map((tut) => (
          <li key={tut.id} className="list-row">
            <Link to={`/learn/${tut.slug}`}>{tut.title}</Link>
            {tut.access_role !== "anonymous" && (
              <span className="badge">{t("learn.premium")}</span>
            )}
          </li>
        ))}
        {tutorials.length === 0 && <li className="archives-empty">{t("learn.empty")}</li>}
      </ul>
    </div>
  );
}
