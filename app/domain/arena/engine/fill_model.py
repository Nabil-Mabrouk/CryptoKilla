"""Modèle de fill — formules exactes de l'Annexe F (Livre).

Fonctions pures, sans DB ni réseau : testables directement contre les 4
exemples numériques vérifiés de l'Annexe F (déjà relus/validés dans le
Livre — fixtures de `tests/arena/test_fill_model.py`).

Notation reprise telle quelle de l'Annexe F : `ref` = milieu de carnet à
l'instant du fill (fallback dernier prix connu, géré par l'appelant) ;
`half_spread` = (ask-bid)/(2*ref) ; `T` = taille de l'ordre en devise de
cotation ; `volume_1h` = volume horaire en devise de cotation
(volume_1h_base × ref).
"""

from __future__ import annotations

import math
from typing import Literal

Side = Literal["buy", "sell"]


def half_spread(bid: float, ask: float, ref: float) -> float:
    return (ask - bid) / (2 * ref)


def slippage(size: float, volume_1h: float, k_slippage: float, slippage_max: float) -> float:
    """`min(k_slippage × √(T/volume_1h), slippage_max)` (N-C13-04)."""
    if volume_1h <= 0:
        return slippage_max
    return min(k_slippage * math.sqrt(size / volume_1h), slippage_max)


def check_liquidity(size: float, volume_1h: float, part_max_liquidite: float) -> bool:
    """`True` si l'ordre passe la garde de liquidité (N-C13-05) — au-delà,
    `E-LIQUIDITY`, aucun fill partiel (ch.7.4)."""
    return size <= part_max_liquidite * volume_1h


def market_fill(ref: float, hs: float, slip: float, side: Side) -> float:
    """Ordre marché (N-C13-04) : achat majore, vente minore."""
    if side == "buy":
        return ref * (1 + hs + slip)
    return ref * (1 - hs - slip)


def stop_fill(stop_level: float, hs: float, slip: float, closing_side: Side) -> float:
    """Stop touché (règle de la mèche, N-C13-10) : exécuté comme un ordre
    marché AU niveau du stop, avec slippage défavorable (N-C13-07).
    `closing_side` = le sens de la clôture (opposé du sens de la position :
    'sell' pour une position longue, 'buy' pour une position courte)."""
    return market_fill(stop_level, hs, slip, closing_side)


def take_profit_fill(tp_level: float) -> float:
    """TP touché : exécuté exactement au niveau, sans slippage
    supplémentaire (asymétrie verrouillée, N-C13-07)."""
    return tp_level


def limit_fill(limit_price: float, ref: float, side: Side) -> float:
    """Ordre limite exécuté dès croisement (N-C13-08) : au meilleur entre
    la limite et le prix de référence, jamais pire que la limite pour
    l'agent."""
    if side == "buy":
        return min(limit_price, ref)
    return max(limit_price, ref)


def fees(notional: float, frais_par_ordre: float) -> float:
    return frais_par_ordre * notional


def quantity_from_open(taille_ouverture: float, fill_entree: float) -> float:
    return taille_ouverture / fill_entree


def pnl_net(
    *,
    taille_ouverture: float,
    fill_entree: float,
    fill_sortie: float,
    frais_par_ordre: float,
    side: Side,
) -> dict[str, float]:
    """PnL net d'une position complète (Annexe F). `side` = sens
    d'OUVERTURE de la position (buy=long, sell=short)."""
    qty = quantity_from_open(taille_ouverture, fill_entree)
    direction = 1 if side == "buy" else -1
    pnl_brut = (fill_sortie - fill_entree) * qty * direction
    frais_entree = fees(taille_ouverture, frais_par_ordre)
    frais_sortie = fees(qty * fill_sortie, frais_par_ordre)
    return {
        "quantity": qty,
        "pnl_brut": pnl_brut,
        "frais_entree": frais_entree,
        "frais_sortie": frais_sortie,
        "pnl_net": pnl_brut - frais_entree - frais_sortie,
    }


def closing_side(position_side: Side) -> Side:
    """Le sens d'une clôture est toujours l'opposé du sens d'ouverture."""
    return "sell" if position_side == "buy" else "buy"
