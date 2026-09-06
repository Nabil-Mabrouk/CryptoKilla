"""Client Kraken — API publique uniquement (N-C14-01 : source unique v1).

Aucune clé API requise (endpoints publics OHLC/Depth) — cohérent avec
ARENA.md §3 : aucun secret Kraken hors `.env`, et il n'y en a justement pas
besoin ici. Les fonctions `fetch_*` font l'appel réseau ; `parse_*` sont des
fonctions pures testables sans réseau (fixtures JSON Kraken réelles).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

KRAKEN_BASE_URL = "https://api.kraken.com/0/public"

# Paires suivies (N-C14-01/liste_paires) -> code Kraken. Ensemble fermé et
# restreint à ce que `liste_paires` (season_params) autorise ; ajouter une
# paire ici sans l'ajouter à `liste_paires` n'aurait aucun effet (le reste
# du système ne référence que `liste_paires`).
PAIR_TO_KRAKEN: dict[str, str] = {
    "BTC/EUR": "XBTEUR",
    "ETH/EUR": "ETHEUR",
}


def kraken_code(pair: str) -> str:
    try:
        return PAIR_TO_KRAKEN[pair]
    except KeyError as exc:
        raise ValueError(f"Paire non mappée vers un code Kraken : {pair!r}") from exc


class KrakenError(RuntimeError):
    pass


async def fetch_ohlc(client: httpx.AsyncClient, pair: str, since: int | None = None) -> dict[str, Any]:
    """OHLC 1 minute (N-C14-02 : seule granularité capturée, `interval=1`)."""
    params: dict[str, Any] = {"pair": kraken_code(pair), "interval": 1}
    if since is not None:
        params["since"] = since
    resp = await client.get(f"{KRAKEN_BASE_URL}/OHLC", params=params)
    resp.raise_for_status()
    return resp.json()


async def fetch_orderbook(client: httpx.AsyncClient, pair: str) -> dict[str, Any]:
    """Instantané de carnet (N-C14-03), profondeur minimale (top-of-book)."""
    params = {"pair": kraken_code(pair), "count": 1}
    resp = await client.get(f"{KRAKEN_BASE_URL}/Depth", params=params)
    resp.raise_for_status()
    return resp.json()


def parse_ohlc(raw: dict[str, Any], pair: str) -> list[dict[str, Any]]:
    """Convertit une réponse OHLC Kraken en lignes candle prêtes pour
    `MarketCandle`. Kraken renvoie une bougie EN COURS en dernière position
    (non close) — on l'exclut toujours (on ne capture que des bougies
    closes, cohérent avec `N-C14-02`)."""
    if raw.get("error"):
        raise KrakenError(str(raw["error"]))
    result = raw["result"]
    kraken_key = kraken_code(pair)
    rows = result.get(kraken_key) or next(
        (v for k, v in result.items() if k != "last"), []
    )
    candles = []
    for row in rows[:-1]:  # dernière ligne = bougie en cours, jamais close
        ts, o, h, l, c, _vwap, vol, _count = row
        candles.append(
            {
                "pair": pair,
                "candle_time": datetime.fromtimestamp(int(ts), tz=timezone.utc),
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": float(vol),
            }
        )
    return candles


def parse_orderbook(raw: dict[str, Any], pair: str) -> dict[str, Any]:
    """Extrait `{bid, ask}` (top-of-book) — suffisant pour `ref`/`half_spread`
    du modèle de fill (Annexe F)."""
    if raw.get("error"):
        raise KrakenError(str(raw["error"]))
    result = raw["result"]
    kraken_key = kraken_code(pair)
    book = result.get(kraken_key) or next(iter(result.values()))
    best_bid = float(book["bids"][0][0])
    best_ask = float(book["asks"][0][0])
    return {"pair": pair, "bid": best_bid, "ask": best_ask}
