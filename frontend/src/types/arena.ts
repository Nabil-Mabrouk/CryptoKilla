// Forme de GET /api/arena/public/status (app/domain/routers.py) — partagée
// entre Landing.tsx et les sections qu'il alimente (Leaderboard,
// DynastyShowcase, SeasonNotice), pour ne faire qu'UN appel réseau au lieu
// d'un par section.
export interface ArenaLeaderboardRow {
  dynasty: string;
  color: string;
  generation: number;
  status: string;
  capital: number;
  pnl: number;
}

export interface ArenaDynastyRow {
  name: string;
  model: string;
  color: string;
}

export interface ArenaPublicStatus {
  season: { id: string; state: string; mode: string } | null;
  alive_count: number;
  dynasties: ArenaDynastyRow[];
  leaderboard: ArenaLeaderboardRow[];
}
