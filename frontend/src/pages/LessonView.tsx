import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { apiFetch } from "../api";

interface LessonData {
  id: number;
  title: string;
  order: number;
  content: string;
}

type LoadState = "loading" | "ok" | "not_found" | "unauthorized" | "forbidden";

const MARKER_RE = /\[(NORME|PARAM|LORE|OUVERT)\]/g;

function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(new RegExp("[\\u0300-\\u036f]", "g"), "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

function flattenText(node: ReactNode): string {
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(flattenText).join("");
  if (node && typeof node === "object" && "props" in node) {
    return flattenText((node as { props: { children?: ReactNode } }).props.children);
  }
  return "";
}

// Marqueurs du Livre (Chap 0.1 — conventions de rédaction) : [NORME]/
// [PARAM]/[LORE]/[OUVERT] deviennent un système visuel (CHARTE-GRAPHIQUE.md
// §9). Pas de dépendance rehype-raw : on scinde les enfants texte de
// ReactMarkdown sur la regex et on enveloppe chaque marqueur trouvé d'un
// <span> stylé, appliqué aux nœuds où ces marqueurs apparaissent en prose.
function withMarkers(children: ReactNode): ReactNode {
  if (typeof children === "string") {
    const parts = children.split(MARKER_RE);
    if (parts.length === 1) return children;
    return parts.map((part, i) =>
      i % 2 === 1 ? (
        <span key={i} className={`marker marker--${part.toLowerCase()}`}>
          [{part}]
        </span>
      ) : (
        part
      ),
    );
  }
  if (Array.isArray(children)) {
    return children.map((c, i) => <span key={i}>{withMarkers(c)}</span>);
  }
  return children;
}

// Contenu d'une leçon (Chap 11) — le contrôle d'accès est fait côté API
// (401 non connecté, 403 rôle insuffisant) : ce composant ne fait que
// refléter ces réponses, jamais sa propre logique de permission.
//
// Monde Archives (CHARTE-GRAPHIQUE.md §9) : fond papier, Chronique, sommaire
// latéral sticky (généré depuis les ## / ### du markdown source — version
// simplifiée sans piste de progression au scroll), marqueurs du Livre
// stylés, blocs de code en Terminal.
export default function LessonView() {
  const { t } = useTranslation();
  const { slug, lessonId } = useParams<{ slug: string; lessonId: string }>();
  const [lesson, setLesson] = useState<LessonData | null>(null);
  const [state, setState] = useState<LoadState>("loading");

  useEffect(() => {
    setLesson(null);
    setState("loading");
    apiFetch(`/api/content/tutorials/${slug}/lessons/${lessonId}`).then(async (r) => {
      if (r.ok) {
        setLesson((await r.json()) as LessonData);
        setState("ok");
      } else if (r.status === 401) setState("unauthorized");
      else if (r.status === 403) setState("forbidden");
      else setState("not_found");
    });
  }, [slug, lessonId]);

  const toc = useMemo(() => {
    if (!lesson) return [];
    return lesson.content
      .split("\n")
      .filter((l) => /^#{2,3}\s/.test(l))
      .map((l) => {
        const level = l.match(/^#+/)![0].length;
        const text = l.replace(/^#+\s*/, "").trim();
        return { level, text, id: slugify(text) };
      });
  }, [lesson]);

  const backLink = (
    <Link to={`/learn/${slug}`} className="archives-back">
      {t("learn.detail.back")}
    </Link>
  );

  if (state === "loading")
    return (
      <div className="world-archives">
        <p>{t("learn.detail.loading")}</p>
      </div>
    );
  if (state === "not_found")
    return (
      <div className="world-archives">
        {backLink}
        <p className="archives-error">{t("learn.detail.notFound")}</p>
      </div>
    );
  if (state === "unauthorized")
    return (
      <div className="world-archives">
        {backLink}
        <p>
          {t("learn.lesson.unauthorized")}{" "}
          <Link to="/login">{t("nav.login")}</Link>
        </p>
      </div>
    );
  if (state === "forbidden")
    return (
      <div className="world-archives">
        {backLink}
        <p>{t("learn.lesson.forbidden")}</p>
      </div>
    );

  return (
    <div className="world-archives">
      <div className="archives-layout">
        <article className="archives-article">
          {backLink}
          <h1 className="archives-title">{lesson!.title}</h1>
          <div className="archives-prose">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p>{withMarkers(children)}</p>,
                li: ({ children }) => <li>{withMarkers(children)}</li>,
                strong: ({ children }) => <strong>{withMarkers(children)}</strong>,
                em: ({ children }) => <em>{withMarkers(children)}</em>,
                td: ({ children }) => <td>{withMarkers(children)}</td>,
                h2: ({ children }) => <h2 id={slugify(flattenText(children))}>{children}</h2>,
                h3: ({ children }) => <h3 id={slugify(flattenText(children))}>{children}</h3>,
              }}
            >
              {lesson!.content}
            </ReactMarkdown>
          </div>
        </article>
        {toc.length > 0 && (
          <nav className="archives-toc" aria-label={t("learn.detail.toc")}>
            <p className="archives-toc-title mono">{t("learn.detail.toc")}</p>
            {toc.map((h) => (
              <a key={h.id} href={`#${h.id}`} className={`archives-toc-link level-${h.level}`}>
                {h.text}
              </a>
            ))}
          </nav>
        )}
      </div>
    </div>
  );
}
