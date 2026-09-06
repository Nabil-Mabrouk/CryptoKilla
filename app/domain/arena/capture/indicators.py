"""Indicateurs techniques — calculés par code, jamais par le LLM (N-C14-06).

Sous-ensemble C1 (décision de portée du plan) : SMA, EMA, RSI. Le reste de
la liste proposée par le Livre (MACD, ATR, Bollinger, VWAP, volume profile,
ADX, stochastique) s'ajoute au même patron plus tard, sans reprise
structurelle — `get_market_data` (agents/tools.py) ne connaît que la liste
des clés de `INDICATORS`, pas leur implémentation.
"""

from __future__ import annotations

import numpy as np


def sma(closes: list[float], period: int) -> list[float | None]:
    """Moyenne mobile simple. `None` tant que la fenêtre n'est pas pleine."""
    out: list[float | None] = [None] * len(closes)
    if period <= 0 or len(closes) < period:
        return out
    arr = np.asarray(closes, dtype=float)
    window_sums = np.convolve(arr, np.ones(period), mode="valid") / period
    out[period - 1 :] = window_sums.tolist()
    return out


def ema(closes: list[float], period: int) -> list[float | None]:
    """Moyenne mobile exponentielle, amorcée par la SMA des `period`
    premiers points (convention standard)."""
    out: list[float | None] = [None] * len(closes)
    if period <= 0 or len(closes) < period:
        return out
    alpha = 2.0 / (period + 1)
    seed = float(np.mean(closes[:period]))
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(closes)):
        prev = closes[i] * alpha + prev * (1 - alpha)
        out[i] = prev
    return out


def rsi(closes: list[float], period: int = 14) -> list[float | None]:
    """RSI de Wilder. `None` tant que `period` variations ne sont pas
    disponibles (nécessite `period + 1` clôtures)."""
    out: list[float | None] = [None] * len(closes)
    if period <= 0 or len(closes) <= period:
        return out
    deltas = np.diff(np.asarray(closes, dtype=float))
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = float(np.mean(gains[:period]))
    avg_loss = float(np.mean(losses[:period]))
    out[period] = _rsi_from_averages(avg_gain, avg_loss)

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        out[i + 1] = _rsi_from_averages(avg_gain, avg_loss)
    return out


def _rsi_from_averages(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


# Registre exposé à `get_market_data` (agents/tools.py) — nom -> fonction.
INDICATORS = {
    "SMA_20": lambda closes: sma(closes, 20),
    "EMA_12": lambda closes: ema(closes, 12),
    "RSI_14": lambda closes: rsi(closes, 14),
}
