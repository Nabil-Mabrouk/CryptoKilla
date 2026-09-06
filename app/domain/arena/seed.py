"""Seed de développement — UNE saison, UNE dynastie, UN agent.

Pas un fixture de production : les valeurs de `season_params` sont reprises
telles quelles de l'Annexe E (registre des paramètres) là où le Livre donne
un exemple explicitement marqué « illustratif » — jamais inventées par ce
code. Là où l'Annexe E dit « À fixer » (aucune valeur, ex. `pool_plancher`),
ce module met 0 : correct pour C1 (un seul agent, le calcul du pool est un
no-op tant qu'il n'y a personne d'autre à financer, décision de portée du
plan C1) mais PAS une vraie valeur de saison 1 — Q-01 (`seuil_mort`) et
Q-05 (devise/nature de `capital_initial`) restent ouvertes, jamais
tranchées silencieusement ici.

Usage : `python -m app.domain.arena.seed` (dev uniquement, idempotent —
ne recrée rien si une saison existe déjà).
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.database import SessionLocal
from app.domain.arena.models import Agent, CapitalLedger, Dynasty, Season, SeasonParam

# Annexe E — valeurs illustratives du Livre, PAS des décisions de saison 1.
SEED_PARAMS: dict[str, object] = {
    "capital_initial": 10_000,  # illustratif (Q-05 : devise non tranchée)
    "seuil_mort": 0,  # illustratif (Q-01 non tranchée)
    "liste_paires": ["BTC/EUR", "ETH/EUR"],  # illustratif
    "risque_max_trade": 1.5,  # % — illustratif
    "taille_max_ordre": 5_000,  # "À fixer" dans l'Annexe E — placeholder dev
    "taille_max_logique": 300,  # caractères — illustratif
    "duree_max_ordre_limite": 3600,  # secondes — "À fixer", placeholder dev
    "k_slippage": 0.002,  # illustratif
    "slippage_max": 0.002,  # illustratif (0,2 %)
    "part_max_liquidite": 0.05,  # illustratif (5 %)
    "frais_par_ordre": 0.0025,  # illustratif (0,25 %)
    "latence_simulee": 1,  # secondes — illustratif
    "fenetres_max_data": {"1m": 1440, "1h": 720},  # "À fixer par timeframe" — placeholder dev
    "frequence_snapshot_carnet": 10,  # secondes — illustratif
    "retention_carnet": 86_400,  # secondes (24h) — non chiffré au Livre, placeholder dev
    "plafond_solde_tokens": 10,  # multiple de l'allocation horaire — illustratif (x10)
    "budget_horaire_dollars": 0.50,  # illustratif
    # Dérivé en pratique de budget_horaire_dollars × un tarif modèle réel ;
    # C1 le fixe directement pour ne pas implémenter cette conversion tout
    # de suite (aucun [NORME] ne l'exige pour la DoD C1 — un seul agent,
    # pas de comparaison inter-modèles à faire).
    "allocation_horaire_par_modele": 50_000,  # placeholder dev, en tokens
    "pool_plancher": 0,  # "À fixer (secret)" — no-op avec un seul agent
    "pool_bonus_audience": 0,  # "À fixer (secret)" — no-op avec un seul agent
}


async def seed_dev_season(dynasty_name: str = "claude-nord", model: str = "claude") -> str:
    """Crée saison + dynastie + agent + season_params s'ils n'existent pas
    déjà. Retourne l'`agent_id` (existant ou créé)."""
    async with SessionLocal() as db:
        existing = (await db.execute(select(Season).limit(1))).scalar_one_or_none()
        if existing is not None:
            agent = (
                await db.execute(select(Agent).where(Agent.status != "mort").limit(1))
            ).scalar_one_or_none()
            if agent is not None:
                return agent.id
            season = existing
        else:
            season = Season(state="active", mode="perpetuelle")
            db.add(season)
            await db.flush()
            for name, value in SEED_PARAMS.items():
                db.add(SeasonParam(season_id=season.id, name=name, value=value, visibility="public"))

        dynasty = Dynasty(season_id=season.id, name=dynasty_name, model=model, color="#FF7A45")
        db.add(dynasty)
        await db.flush()

        agent = Agent(dynasty_id=dynasty.id, generation=1, status="actif")
        db.add(agent)
        await db.flush()

        # Sans ce crédit, l'agent ne pourrait jamais passer la validation
        # E-INSUFFICIENT-CAPITAL — capital_initial est un [PARAM] de la
        # charte (Annexe E), pas une valeur en dur ici (ARENA.md §3).
        capital_initial = SEED_PARAMS["capital_initial"]
        db.add(CapitalLedger(agent_id=agent.id, event_id=None, kind="capital_initial", amount=capital_initial))

        await db.commit()
        await db.refresh(agent)
        return agent.id


if __name__ == "__main__":
    agent_id = asyncio.run(seed_dev_season())
    print(f"Seed OK — agent_id={agent_id}")
