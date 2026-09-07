"""Lecture du registre des paramètres (Annexe E) — `season_params`.

Un seul point de lecture pour tout le code arène : jamais de valeur de jeu
en dur ailleurs (ARENA.md §3 — "Aucune valeur de jeu en dur : tout passe
par le registre des paramètres").
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.arena.models import SeasonParam

# Annexe E — valeurs illustratives du Livre, PAS des décisions de saison 1
# réelle. Utilisées comme défauts de départ (dev ET création admin d'une
# saison, provisioning.py) : là où l'Annexe E dit « À fixer » (aucune
# valeur, ex. `pool_plancher`), ce registre met 0/un placeholder — jamais
# une valeur inventée pour un champ que le Livre chiffre déjà. Q-01
# (`seuil_mort`) et Q-05 (devise/nature de `capital_initial`) restent
# ouvertes ; ces valeurs de départ ne les tranchent pas silencieusement,
# elles restent éditables (PATCH /api/arena/admin/seasons/{id}/params).
DEFAULT_SEASON_PARAMS: dict[str, object] = {
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
    # C2 — cycle de vie (chapitre 5). Valeurs illustratives de développement ;
    # le Livre ne les chiffre nulle part (`[PARAM]` sans valeur).
    "allocation_funeraire": 5_000,  # tokens, budget dédié à la phase funéraire
    "duree_max_funeraire": 1_800,  # secondes (~30 min, décision 7 du plan)
    "delai_renaissance": 3_600,  # secondes avant la renaissance de la lignée
    "taille_max_testament": 2_000,  # caractères
    "memoire_k_resultats": 5,  # top-k de memory_search
    # C2 — pool d'engagement (chapitre 6.5). Le Livre déclare EXPLICITEMENT
    # les coefficients γ/réciprocité/rendements décroissants "secrets"
    # (N-C06-08/09) — ces valeurs sont des placeholders de développement
    # clairement documentés comme tels, jamais un vrai barème de saison 1.
    "n_messages_plein_rendement": 5,  # au-delà, rendements décroissants
    "poids_message_contextuel": 0.4,  # relatif à 1.0 pour un message substantiel
    "points_par_citation": 1.0,
    "points_par_like": 1.0,
    "points_par_reaction": 1.0,
    "fenetre_decote_reciprocite": 3_600,  # secondes — décote anti-collusion
}


async def get_param(db: AsyncSession, season_id: str, name: str, *, default: Any = None) -> Any:
    row = (
        await db.execute(
            select(SeasonParam.value).where(
                SeasonParam.season_id == season_id, SeasonParam.name == name
            )
        )
    ).scalar_one_or_none()
    if row is None:
        if default is not None:
            return default
        raise KeyError(f"season_param manquant : {name} (season_id={season_id})")
    return row
