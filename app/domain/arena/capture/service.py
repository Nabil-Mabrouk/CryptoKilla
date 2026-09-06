"""Service de capture (N-C14-02/03/04) — ingestion continue OHLCV 1m +
instantanés de carnet, agrégation à la demande, marquage `stale`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.capture.kraken_client import fetch_ohlc, fetch_orderbook, parse_ohlc, parse_orderbook
from app.domain.arena.log import log
from app.domain.arena.models import MarketCandle, OrderbookSnapshot

# Au-delà de cet âge, une bougie est jugée périmée (N-C14-04). Généreux
# (5 min) : le tick de capture tourne toutes les ~30-60s, cette marge
# absorbe un aller-retour Kraken lent sans faux positif de panne.
STALE_AFTER = timedelta(minutes=5)


async def capture_tick(db: AsyncSession, client: httpx.AsyncClient, pairs: list[str]) -> None:
    """Un tick de capture pour toutes les paires suivies. Idempotent :
    l'upsert sur `(pair, candle_time)` ne duplique jamais une bougie déjà
    connue (Kraken peut renvoyer plusieurs fois la même bougie close)."""
    for pair in pairs:
        try:
            raw_ohlc = await fetch_ohlc(client, pair)
            candles = parse_ohlc(raw_ohlc, pair)
            for candle in candles:
                await _upsert_candle(db, candle)

            raw_book = await fetch_orderbook(client, pair)
            book = parse_orderbook(raw_book, pair)
            db.add(OrderbookSnapshot(pair=book["pair"], bid=book["bid"], ask=book["ask"]))
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            # Panne de flux (N-C14-04) : ne fait PAS remonter — le tick
            # suivant réessaiera. La fraîcheur des données déjà en base
            # (is_stale) porte la conséquence, pas une exception qui
            # arrêterait la boucle du worker pour une seule paire en panne.
            # Loggé en base (visible admin) EN PLUS du print (logs conteneur).
            print(f"capture_tick: échec paire={pair}: {exc!r}")
            await log(db, "error", "capture", f"Échec de capture pour {pair}", {"error": repr(exc)})
    await db.commit()


async def _upsert_candle(db: AsyncSession, candle: dict) -> None:
    # Portable Postgres/SQLite (décision 4 du plan) : pas de
    # `on_conflict_do_nothing` dialect-spécifique. Un seul processus de
    # capture (C1, un seul worker) écrit ici — pas de course possible entre
    # le SELECT et l'INSERT.
    exists = (
        await db.execute(
            select(MarketCandle.id).where(
                MarketCandle.pair == candle["pair"],
                MarketCandle.candle_time == candle["candle_time"],
            )
        )
    ).scalar_one_or_none()
    if exists is None:
        db.add(MarketCandle(**candle))


async def latest_candles(
    db: AsyncSession, pair: str, limit: int = 200
) -> tuple[list[MarketCandle], bool, float]:
    """Les `limit` dernières bougies 1m (ordre chronologique croissant) +
    indicateur de fraîcheur (N-C14-04 : `stale`, `age_seconds`)."""
    rows = (
        await db.execute(
            select(MarketCandle)
            .where(MarketCandle.pair == pair)
            .order_by(MarketCandle.candle_time.desc())
            .limit(limit)
        )
    ).scalars().all()
    rows = list(reversed(rows))
    if not rows:
        return [], True, float("inf")
    age = datetime.now(timezone.utc) - rows[-1].candle_time.replace(tzinfo=timezone.utc)
    return rows, age > STALE_AFTER, age.total_seconds()


async def latest_orderbook(db: AsyncSession, pair: str) -> OrderbookSnapshot | None:
    return (
        await db.execute(
            select(OrderbookSnapshot)
            .where(OrderbookSnapshot.pair == pair)
            .order_by(OrderbookSnapshot.captured_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
