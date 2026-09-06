"""Fixtures numériques de l'Annexe F — déjà relues/validées dans le Livre.
Pas de dépendance DB : `fill_model` est pur.
"""

import pytest

from app.domain.arena.engine import fill_model


def test_market_buy_fixture_1():
    """Achat 2100 EUR sur BTC/EUR, ref=42001.10, volume_1h=184.62 BTC."""
    ref = 42001.10
    volume_1h = 184.62 * ref
    hs = 0.00035519  # half_spread donné par l'exemple (carnet fil rouge)

    slip = fill_model.slippage(2100, volume_1h, k_slippage=0.002, slippage_max=0.002)
    assert slip == pytest.approx(0.0000329, abs=1e-6)

    fill = fill_model.market_fill(ref, hs, slip, "buy")
    assert fill == pytest.approx(42017.40, abs=0.05)

    fees = fill_model.fees(2100, 0.0025)
    assert fees == pytest.approx(5.25, abs=0.01)


def test_liquidity_guard_fixture_2():
    """T=500 000 EUR > 5% x 7 754 243 EUR -> rejet, aucun fill."""
    volume_1h = 7_754_243
    assert fill_model.check_liquidity(500_000, volume_1h, part_max_liquidite=0.05) is False
    assert fill_model.check_liquidity(2_100, volume_1h, part_max_liquidite=0.05) is True


def test_stop_fill_fixture_3():
    """Stop en mèche à 40800.00, liquidité 90 BTC au niveau du stop."""
    stop = 40800.00
    volume_1h = 90 * stop
    hs = 0.00084558

    slip = fill_model.slippage(2036, volume_1h, k_slippage=0.002, slippage_max=0.002)
    fill = fill_model.stop_fill(stop, hs, slip, closing_side="sell")
    assert fill < stop  # défavorable pour une position longue (N-C13-07)
    assert fill == pytest.approx(40763.55, abs=0.5)


def test_take_profit_no_extra_slippage():
    """Asymétrie verrouillée (N-C13-07) : TP exécuté exactement au niveau."""
    assert fill_model.take_profit_fill(45000.0) == 45000.0


def test_pnl_net_fixture_4():
    """Trade complet pos-88a1 (fil rouge Annexe B/F)."""
    result = fill_model.pnl_net(
        taille_ouverture=2100,
        fill_entree=42017.40,
        fill_sortie=40763.55,
        frais_par_ordre=0.0025,
        side="buy",
    )
    assert result["quantity"] == pytest.approx(0.0499793, abs=1e-6)
    assert result["pnl_brut"] == pytest.approx(-62.67, abs=0.05)
    assert result["frais_entree"] == pytest.approx(5.25, abs=0.01)
    assert result["frais_sortie"] == pytest.approx(5.09, abs=0.02)
    assert result["pnl_net"] == pytest.approx(-73.01, abs=0.05)


def test_closing_side_is_opposite():
    assert fill_model.closing_side("buy") == "sell"
    assert fill_model.closing_side("sell") == "buy"


def test_limit_fill_never_worse_than_limit():
    # Achat limite à 100, ref grimpe à 105 -> exécuté à 100 (le meilleur des deux)
    assert fill_model.limit_fill(100, 105, "buy") == 100
    # Achat limite à 100, ref tombe à 95 -> exécuté à 95 (mieux que la limite)
    assert fill_model.limit_fill(100, 95, "buy") == 95
