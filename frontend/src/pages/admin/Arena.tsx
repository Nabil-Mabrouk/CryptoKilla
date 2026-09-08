import { useEffect, useState, type FormEvent } from "react";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../api";

// Console admin de l'arène (couche C1) — créer une saison/des dynasties,
// observer le journal d'événements (Annexe B) et les erreurs opérationnelles
// (app/domain/arena/log.py). Sans cette page, aucune saison ne peut exister
// en production (seed_dev_season() ne s'exécute jamais hors dev, ARENA.md :
// pas de saison fabriquée en silence) et aucune erreur n'est visible sans
// shell sur le conteneur.
type Section = "seasons" | "events" | "logs" | "worker";

interface SeasonRow {
  id: string;
  state: string;
  mode: string;
  created_at: string;
  dynasty_count: number;
  agent_count: number;
}
interface AgentRow {
  id: string;
  generation: number;
  status: string;
  capital: number;
  token_balance: number;
}
interface DynastyRow {
  id: string;
  name: string;
  model: string;
  color: string;
  agents: AgentRow[];
}
interface EventRow {
  id: string;
  type: string;
  timestamp: string;
  sender: string;
  recipient: string | null;
  payload: unknown;
}
interface LogRow {
  id: number;
  created_at: string;
  level: string;
  component: string;
  message: string;
  details: unknown;
}
interface WorkerRun {
  id: number;
  started_at: string;
  finished_at: string | null;
  status: string;
  error: string | null;
}

const SECTIONS: Section[] = ["seasons", "events", "logs", "worker"];

export default function Arena() {
  const { t } = useTranslation();
  const [section, setSection] = useState<Section>("seasons");

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">{t("admin.arena.title")}</h1>
      <div className="mb-4 flex gap-2">
        {SECTIONS.map((s) => (
          <button
            key={s}
            className="admin-btn-inline"
            style={section === s ? { borderColor: "var(--torch)", color: "var(--torch)" } : undefined}
            onClick={() => setSection(s)}
            type="button"
          >
            {t(`admin.arena.sections.${s}`)}
          </button>
        ))}
      </div>
      {section === "seasons" && <SeasonsPanel />}
      {section === "events" && <EventsPanel />}
      {section === "logs" && <LogsPanel />}
      {section === "worker" && <WorkerPanel />}
    </div>
  );
}

function SeasonsPanel() {
  const { t } = useTranslation();
  const [seasons, setSeasons] = useState<SeasonRow[] | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<string>("");
  const [dynasties, setDynasties] = useState<DynastyRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [dynName, setDynName] = useState("");
  const [dynModel, setDynModel] = useState("");
  const [dynColor, setDynColor] = useState("#FF7A45");

  async function loadSeasons(selectId?: string) {
    const r = await apiFetch("/api/arena/admin/seasons");
    if (!r.ok) {
      setError(t("admin.arena.errorGeneric"));
      return;
    }
    const rows = (await r.json()) as SeasonRow[];
    setSeasons(rows);
    if (selectId) setSelectedSeason(selectId);
    else if (!selectedSeason && rows.length > 0) setSelectedSeason(rows[0].id);
  }

  useEffect(() => {
    loadSeasons();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadDynasties(seasonId: string) {
    const r = await apiFetch(`/api/arena/admin/seasons/${seasonId}/dynasties`);
    if (r.ok) setDynasties((await r.json()) as DynastyRow[]);
  }

  useEffect(() => {
    if (selectedSeason) loadDynasties(selectedSeason);
    else setDynasties(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSeason]);

  async function createSeason() {
    setError(null);
    const r = await apiFetch("/api/arena/admin/seasons", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: "perpetuelle" }),
    });
    if (r.ok) {
      const created = (await r.json()) as { id: string };
      await loadSeasons(created.id);
    } else {
      setError(t("admin.arena.errorGeneric"));
    }
  }

  async function createDynasty(e: FormEvent) {
    e.preventDefault();
    if (!selectedSeason || !dynName.trim() || !dynModel.trim()) return;
    setError(null);
    const r = await apiFetch(`/api/arena/admin/seasons/${selectedSeason}/dynasties`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: dynName.trim(), model: dynModel.trim(), color: dynColor }),
    });
    if (r.ok) {
      setDynName("");
      setDynModel("");
      await loadDynasties(selectedSeason);
      await loadSeasons(selectedSeason);
    } else {
      setError(t("admin.arena.errorGeneric"));
    }
  }

  return (
    <div className="grid gap-6">
      {error && <p className="admin-error">{error}</p>}

      <div className="admin-card p-4">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-semibold">{t("admin.arena.seasonsTitle")}</h2>
          <button className="admin-btn-inline" onClick={createSeason} type="button">
            {t("admin.arena.newSeason")}
          </button>
        </div>
        {seasons === null && <p>{t("admin.arena.loading")}</p>}
        {seasons !== null && seasons.length === 0 && <p className="admin-muted">{t("admin.arena.noSeasons")}</p>}
        {seasons !== null && seasons.length > 0 && (
          <table className="w-full text-left text-sm">
            <thead>
              <tr>
                <th className="p-2"></th>
                <th className="p-2">{t("admin.arena.columns.state")}</th>
                <th className="p-2">{t("admin.arena.columns.mode")}</th>
                <th className="p-2">{t("admin.arena.columns.created")}</th>
                <th className="p-2">{t("admin.arena.columns.dynasties")}</th>
                <th className="p-2">{t("admin.arena.columns.agents")}</th>
              </tr>
            </thead>
            <tbody>
              {seasons.map((s) => (
                <tr key={s.id}>
                  <td className="p-2">
                    <input
                      type="radio"
                      checked={selectedSeason === s.id}
                      onChange={() => setSelectedSeason(s.id)}
                    />
                  </td>
                  <td className="p-2">{s.state}</td>
                  <td className="p-2">{s.mode}</td>
                  <td className="p-2">{new Date(s.created_at).toLocaleString()}</td>
                  <td className="p-2">{s.dynasty_count}</td>
                  <td className="p-2">{s.agent_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {selectedSeason && (
        <div className="admin-card p-4">
          <h2 className="mb-3 font-semibold">{t("admin.arena.dynastiesTitle")}</h2>
          <form onSubmit={createDynasty} className="mb-4 flex flex-wrap items-center gap-2">
            <input
              placeholder={t("admin.arena.dynastyName")}
              value={dynName}
              onChange={(e) => setDynName(e.target.value)}
            />
            <input
              placeholder={t("admin.arena.dynastyModel")}
              value={dynModel}
              onChange={(e) => setDynModel(e.target.value)}
            />
            <input type="color" value={dynColor} onChange={(e) => setDynColor(e.target.value)} />
            <button className="admin-btn-inline" type="submit">
              {t("admin.arena.addDynasty")}
            </button>
          </form>

          {dynasties === null && <p>{t("admin.arena.loading")}</p>}
          {dynasties !== null && dynasties.length === 0 && (
            <p className="admin-muted">{t("admin.arena.noDynasties")}</p>
          )}
          {dynasties !== null &&
            dynasties.map((d) => (
              <div key={d.id} className="mb-3 border-b pb-3" style={{ borderColor: "var(--admin-border)" }}>
                <strong style={{ color: d.color }}>{d.name}</strong>{" "}
                <span className="admin-muted">({d.model})</span>
                <ul className="mt-1 grid gap-1 text-sm">
                  {d.agents.map((a) => (
                    <li key={a.id} className="mono">
                      #{a.generation} · {a.status} · {t("admin.arena.capital")}: {a.capital.toFixed(2)} ·{" "}
                      {t("admin.arena.tokens")}: {a.token_balance.toFixed(0)}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
        </div>
      )}

      {selectedSeason && <ParamsPanel seasonId={selectedSeason} />}
    </div>
  );
}

interface ParamRow {
  name: string;
  value: unknown;
  visibility: string;
}

function ParamsPanel({ seasonId }: { seasonId: string }) {
  const { t } = useTranslation();
  const [params, setParams] = useState<ParamRow[] | null>(null);
  const [open, setOpen] = useState(false);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [savedName, setSavedName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setError(null);
    const r = await apiFetch(`/api/arena/admin/seasons/${seasonId}/params`);
    if (r.ok) {
      const rows = (await r.json()) as ParamRow[];
      setParams(rows);
      setDrafts(Object.fromEntries(rows.map((p) => [p.name, JSON.stringify(p.value)])));
    } else {
      setError(t("admin.arena.errorGeneric"));
    }
  }

  useEffect(() => {
    if (open && params === null) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  async function save(name: string) {
    setError(null);
    setSavedName(null);
    let value: unknown;
    try {
      value = JSON.parse(drafts[name]);
    } catch {
      setError(t("admin.arena.invalidJson"));
      return;
    }
    const r = await apiFetch(`/api/arena/admin/seasons/${seasonId}/params/${encodeURIComponent(name)}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value }),
    });
    if (r.ok) {
      setSavedName(name);
      await load();
    } else {
      setError(t("admin.arena.errorGeneric"));
    }
  }

  return (
    <div className="admin-card p-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">{t("admin.arena.paramsTitle")}</h2>
        <button className="admin-btn-inline" onClick={() => setOpen((v) => !v)} type="button">
          {open ? t("admin.arena.hide") : t("admin.arena.show")}
        </button>
      </div>
      {open && (
        <>
          <p className="admin-muted mt-2 text-xs">{t("admin.arena.paramsHint")}</p>
          {error && <p className="admin-error">{error}</p>}
          {params === null && <p>{t("admin.arena.loading")}</p>}
          {params !== null && (
            <table className="mt-3 w-full text-left text-sm">
              <thead>
                <tr>
                  <th className="p-2">{t("admin.arena.columns.paramName")}</th>
                  <th className="p-2">{t("admin.arena.columns.paramValue")}</th>
                  <th className="p-2">{t("admin.arena.columns.visibility")}</th>
                  <th className="p-2"></th>
                </tr>
              </thead>
              <tbody>
                {params.map((p) => (
                  <tr key={p.name}>
                    <td className="p-2 mono">{p.name}</td>
                    <td className="p-2">
                      <input
                        className="w-full"
                        value={drafts[p.name] ?? ""}
                        onChange={(e) => setDrafts((d) => ({ ...d, [p.name]: e.target.value }))}
                      />
                    </td>
                    <td className="p-2">{p.visibility}</td>
                    <td className="p-2">
                      <button className="admin-btn-inline" onClick={() => save(p.name)} type="button">
                        {savedName === p.name ? t("admin.arena.saved") : t("admin.arena.save")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  );
}

function EventsPanel() {
  const { t } = useTranslation();
  const [events, setEvents] = useState<EventRow[] | null>(null);
  const [typeFilter, setTypeFilter] = useState("");

  async function load() {
    const qs = typeFilter ? `?type=${encodeURIComponent(typeFilter)}` : "";
    const r = await apiFetch(`/api/arena/admin/events${qs}`);
    if (r.ok) setEvents((await r.json()) as EventRow[]);
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [typeFilter]);

  return (
    <div className="admin-card p-4">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <h2 className="font-semibold">{t("admin.arena.eventsTitle")}</h2>
        <input
          placeholder={t("admin.arena.filterType")}
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="ml-auto"
        />
      </div>
      {events === null && <p>{t("admin.arena.loading")}</p>}
      {events !== null && events.length === 0 && <p className="admin-muted">{t("admin.arena.noEvents")}</p>}
      {events !== null && events.length > 0 && (
        <table className="w-full text-left text-sm">
          <thead>
            <tr>
              <th className="p-2">{t("admin.arena.columns.time")}</th>
              <th className="p-2">{t("admin.arena.columns.type")}</th>
              <th className="p-2">{t("admin.arena.columns.sender")}</th>
              <th className="p-2">{t("admin.arena.columns.payload")}</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.id}>
                <td className="p-2">{new Date(e.timestamp).toLocaleString()}</td>
                <td className="p-2 mono">{e.type}</td>
                <td className="p-2">{e.sender}</td>
                <td className="p-2">
                  <pre className="whitespace-pre-wrap text-xs">{JSON.stringify(e.payload)}</pre>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function LogsPanel() {
  const { t } = useTranslation();
  const [logs, setLogs] = useState<LogRow[] | null>(null);
  const [level, setLevel] = useState("");

  async function load() {
    const qs = level ? `?level=${encodeURIComponent(level)}` : "";
    const r = await apiFetch(`/api/arena/admin/logs${qs}`);
    if (r.ok) setLogs((await r.json()) as LogRow[]);
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [level]);

  return (
    <div className="admin-card p-4">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <h2 className="font-semibold">{t("admin.arena.logsTitle")}</h2>
        <select value={level} onChange={(e) => setLevel(e.target.value)} className="ml-auto">
          <option value="">{t("admin.arena.allLevels")}</option>
          <option value="error">error</option>
          <option value="warning">warning</option>
          <option value="info">info</option>
        </select>
      </div>
      {logs === null && <p>{t("admin.arena.loading")}</p>}
      {logs !== null && logs.length === 0 && <p className="admin-muted">{t("admin.arena.noLogs")}</p>}
      {logs !== null && logs.length > 0 && (
        <table className="w-full text-left text-sm">
          <thead>
            <tr>
              <th className="p-2">{t("admin.arena.columns.time")}</th>
              <th className="p-2">{t("admin.arena.columns.level")}</th>
              <th className="p-2">{t("admin.arena.columns.component")}</th>
              <th className="p-2">{t("admin.arena.columns.message")}</th>
              <th className="p-2">{t("admin.arena.columns.details")}</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l.id}>
                <td className="p-2">{new Date(l.created_at).toLocaleString()}</td>
                <td className="p-2" style={l.level === "error" ? { color: "var(--pnl-down)" } : undefined}>
                  {l.level}
                </td>
                <td className="p-2 mono">{l.component}</td>
                <td className="p-2">{l.message}</td>
                <td className="p-2">
                  {l.details != null && <pre className="whitespace-pre-wrap text-xs">{JSON.stringify(l.details)}</pre>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function WorkerPanel() {
  const { t } = useTranslation();
  const [runs, setRuns] = useState<WorkerRun[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    apiFetch("/api/worker/status").then(async (r) => {
      if (r.ok) setRuns((await r.json()) as WorkerRun[]);
      else setError(true);
    });
  }, []);

  if (error) return <p className="admin-error">{t("admin.arena.errorGeneric")}</p>;

  return (
    <div className="admin-card p-4">
      <h2 className="mb-3 font-semibold">{t("admin.arena.workerTitle")}</h2>
      {runs === null && <p>{t("admin.arena.loading")}</p>}
      {runs !== null && runs.length === 0 && <p className="admin-muted">{t("admin.arena.noRuns")}</p>}
      {runs !== null && runs.length > 0 && (
        <table className="w-full text-left text-sm">
          <thead>
            <tr>
              <th className="p-2">{t("admin.arena.columns.started")}</th>
              <th className="p-2">{t("admin.arena.columns.finished")}</th>
              <th className="p-2">{t("admin.arena.columns.status")}</th>
              <th className="p-2">{t("admin.arena.columns.error")}</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.id}>
                <td className="p-2">{new Date(r.started_at).toLocaleString()}</td>
                <td className="p-2">{r.finished_at ? new Date(r.finished_at).toLocaleString() : "—"}</td>
                <td
                  className="p-2"
                  style={r.status === "failed" || r.status === "interrupted" ? { color: "var(--pnl-down)" } : undefined}
                >
                  {r.status}
                </td>
                <td className="p-2 text-xs">{r.error ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
