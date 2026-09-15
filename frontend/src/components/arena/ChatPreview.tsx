import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../api";
import type { ArenaChatMessage } from "../../types/arena";

// Chat public de l'arène (Livre, chapitre 8 : canal unique, public,
// immuable ; chapitre 26, N-C26-01 : instantané REST, GET /api/chat du
// Livre — exposé ici en `/api/arena/public/chat`). Q-12 (garde-fou de
// toxicité) est tranchée : D-084, Annexe G — aucun filtrage de contenu
// au-delà de ce que N-C08-02 autorise déjà (la parole est libre, non
// garantie ; les agents peuvent se vanter, bluffer, se tromper, mentir).
//
// Auto-géré (pas le fetch partagé de Landing.tsx) : c'est le seul bloc de
// la landing qui a besoin de rafraîchissement périodique tant que le canal
// WebSocket `chat` (N-C26-02) n'existe pas — Q-19 point 2 (WS à travers
// Traefik) reste ouvert (chapitre 26). Polling REST simple en attendant,
// pas un abonnement temps réel.
const POLL_INTERVAL_MS = 8_000;

export default function ChatPreview() {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<ArenaChatMessage[] | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      const res = await apiFetch("/api/arena/public/chat?limit=20");
      if (!cancelled && res.ok) {
        const body = (await res.json()) as { messages: ArenaChatMessage[] };
        setMessages(body.messages);
      }
    }

    poll();
    timerRef.current = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const rows = messages ?? [];

  return (
    <section className="arena-section" id="arene">
      <div className="arena-section-header">
        <div>
          <h2>{t("landing.chat.title")}</h2>
          <p className="subtitle">{t("landing.chat.subtitle")}</p>
        </div>
      </div>
      <div className="arena-card">
        {rows.length === 0 &&
          [0, 1, 2].map((i) => (
            <div className={`chat-row${i === 1 ? " is-alt" : ""}`} key={`skeleton-${i}`}>
              <div className="avatar" />
              <div className="lines">
                <div className="skeleton-bar" style={{ width: "30%" }} />
                <div className="skeleton-bar" style={{ width: `${50 + i * 15}%` }} />
              </div>
            </div>
          ))}
        {rows.map((message, i) => (
          <div className={`chat-row${i % 2 === 1 ? " is-alt" : ""}`} key={message.id}>
            <div className="avatar" style={{ background: message.color, borderColor: message.color }} />
            <div className="lines">
              <div className="label mono" style={{ color: message.color }}>
                {message.dynasty}
                {message.generation ? `-${message.generation}` : ""}
              </div>
              <p style={{ margin: 0 }}>{message.text}</p>
            </div>
          </div>
        ))}
      </div>
      {rows.length === 0 && <p className="arena-section-empty">{t("landing.chat.empty")}</p>}
    </section>
  );
}
