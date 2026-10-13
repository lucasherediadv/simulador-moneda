"""Pruebas unitarias para la capa de simulación matemática (core/simulation.py)."""

import numpy as np
import pandas as pd
import pytest

from core.simulation import (
    error_margin,
    evaluate_fairness,
    relative_frequency,
    run_comparison,
    run_simulation,
)


# ==============================================================================
# Pruebas de Evaluación de Equidad (evaluate_fairness y error_margin)
# ==============================================================================


def test_fair_coin_evaluation():
    """510 caras en 1.000 lanzamientos debe considerarse Equilibrada."""
    result = evaluate_fairness(heads=510, tails=490)
    assert result["is_fair"] is True
    assert result["label"] == "Equilibrada"
    assert result["n"] == 1000
    assert result["freq_heads"] == pytest.approx(0.510)
    assert result["difference"] == pytest.approx(0.010)
    assert result["low_n_warning"] is False
    assert "no hay evidencia" in result["message"]


def test_biased_coin_evaluation():
    """700 caras en 1.000 lanzamientos debe considerarse Sesgada."""
    result = evaluate_fairness(heads=700, tails=300)
    assert result["is_fair"] is False
    assert result["label"] == "Sesgada"
    assert result["n"] == 1000
    assert result["freq_heads"] == pytest.approx(0.700)
    assert result["difference"] == pytest.approx(0.200)
    assert result["low_n_warning"] is False
    assert "moneda parece sesgada" in result["message"]


def test_small_n_is_lenient():
    """6 caras en 10 lanzamientos: con margen 1/sqrt(10) ~ 0.316 debe ser Equilibrada."""
    result = evaluate_fairness(heads=6, tails=4)
    assert result["is_fair"] is True
    assert result["label"] == "Equilibrada"
    assert result["low_n_warning"] is True
    assert "Con pocos lanzamientos el margen es amplio" in result["message"]


def test_large_n_detects_small_bias():
    """5.400 caras en 10.000 lanzamientos: diferencia de 0.04 > margen 0.01 -> Sesgada."""
    result = evaluate_fairness(heads=5400, tails=4600)
    assert result["is_fair"] is False
    assert result["label"] == "Sesgada"
    assert result["low_n_warning"] is False


def test_fixed_tolerance_override():
    """Al proveer tolerance fija, anula el margen dinámico 1/sqrt(n)."""
    # 6 caras en 10: diferencia = 0.10. Con tolerancia fija 0.05, debe ser Sesgada
    result = evaluate_fairness(heads=6, tails=4, tolerance=0.05)
    assert result["is_fair"] is False
    assert result["label"] == "Sesgada"
    assert result["margin"] == 0.05

    # 51 caras en 100: diferencia = 0.01. Con tolerancia fija 0.05, debe ser Equilibrada
    result_fair = evaluate_fairness(heads=51, tails=49, tolerance=0.05)
    assert result_fair["is_fair"] is True
    assert result_fair["label"] == "Equilibrada"
    assert result_fair["margin"] == 0.05


def test_margin_decreases_with_n():
    """El margen de error 1/sqrt(n) debe decrecer estrictamente al aumentar n."""
    m10 = error_margin(10)
    m100 = error_margin(100)
    m1000 = error_margin(1000)
    m10000 = error_margin(10000)

    assert m10 > m100 > m1000 > m10000
    assert m100 == pytest.approx(0.10)
    assert m10000 == pytest.approx(0.01)


# ==============================================================================
# Pruebas de Simulación (run_simulation)
# ==============================================================================


@pytest.mark.parametrize("n", [10, 100, 1000, 10000])
def test_counts_add_up(n):
    """heads + tails debe ser exactamente igual a n_flips."""
    sim = run_simulation(n_flips=n, bias=0.5, seed=123)
    assert sim.heads + sim.tails == n
    assert sim.n_flips == n


def test_history_consistency():
    """El historial tiro a tiro debe tener largo n, coherencia acumulada y suma 1."""
    n = 200
    sim = run_simulation(n_flips=n, bias=0.5, seed=42)
    history = sim.history

    assert len(history) == n
    assert list(history.columns) == ["lanzamiento", "caras_acum", "frec_cara", "frec_cruz"]
    assert history["caras_acum"].iloc[-1] == sim.heads
    assert history["frec_cara"].iloc[-1] == pytest.approx(sim.heads / n)
    assert np.allclose(history["frec_cara"] + history["frec_cruz"], 1.0)


def test_probability_bounds():
    """Toda frecuencia relativa en el historial debe estar en [0, 1]."""
    sim = run_simulation(n_flips=500, bias=0.5, seed=7)
    assert (sim.history["frec_cara"] >= 0.0).all()
    assert (sim.history["frec_cara"] <= 1.0).all()
    assert (sim.history["frec_cruz"] >= 0.0).all()
    assert (sim.history["frec_cruz"] <= 1.0).all()


def test_extreme_bias():
    """Con bias=0 debe dar 0 caras; con bias=1 debe dar n caras."""
    sim_zeros = run_simulation(n_flips=50, bias=0.0)
    assert sim_zeros.heads == 0
    assert sim_zeros.tails == 50

    sim_ones = run_simulation(n_flips=50, bias=1.0)
    assert sim_ones.heads == 50
    assert sim_ones.tails == 0


def test_reproducible_with_seed():
    """Dos simulaciones con la misma semilla numérica deben producir resultados idénticos."""
    sim1 = run_simulation(n_flips=1000, bias=0.5, seed=42)
    sim2 = run_simulation(n_flips=1000, bias=0.5, seed=42)

    assert sim1.heads == sim2.heads
    assert sim1.tails == sim2.tails
    pd.testing.assert_frame_equal(sim1.history, sim2.history)


def test_simulated_fair_coin_is_fair():
    """Moneda justa simulada con n=10.000 y seed=42 es clasificada como Equilibrada."""
    sim = run_simulation(n_flips=10000, bias=0.5, seed=42)
    eval_res = evaluate_fairness(heads=sim.heads, tails=sim.tails)
    assert eval_res["is_fair"] is True
    assert eval_res["label"] == "Equilibrada"


def test_simulated_biased_coin_detected():
    """Moneda sesgada (bias=0.54) con n=10.000 y seed=42 es clasificada como Sesgada."""
    sim = run_simulation(n_flips=10000, bias=0.54, seed=42)
    eval_res = evaluate_fairness(heads=sim.heads, tails=sim.tails)
    assert eval_res["is_fair"] is False
    assert eval_res["label"] == "Sesgada"


# ==============================================================================
# Pruebas de Validación de Entradas
# ==============================================================================


def test_invalid_inputs_raise():
    """Verifica que entradas fuera de dominio o tipo inválido disparen ValueError."""
    # n_flips inválido
    with pytest.raises(ValueError):
        run_simulation(n_flips=0)
    with pytest.raises(ValueError):
        run_simulation(n_flips=-5)

    # bias inválido
    with pytest.raises(ValueError):
        run_simulation(n_flips=10, bias=-0.1)
    with pytest.raises(ValueError):
        run_simulation(n_flips=10, bias=1.2)

    # relative_frequency
    with pytest.raises(ValueError):
        relative_frequency(count=5, n=0)
    with pytest.raises(ValueError):
        relative_frequency(count=-1, n=10)
    with pytest.raises(ValueError):
        relative_frequency(count=11, n=10)

    # error_margin
    with pytest.raises(ValueError):
        error_margin(0)
    with pytest.raises(ValueError):
        error_margin(-10)

    # evaluate_fairness
    with pytest.raises(ValueError):
        evaluate_fairness(heads=-1, tails=10)
    with pytest.raises(ValueError):
        evaluate_fairness(heads=10, tails=-1)
    with pytest.raises(ValueError):
        evaluate_fairness(heads=0, tails=0)
    with pytest.raises(ValueError):
        evaluate_fairness(heads=10, tails=10, tolerance=-0.01)


# ==============================================================================
# Pruebas de Comparación (run_comparison)
# ==============================================================================


def test_run_comparison_structure():
    """run_comparison debe devolver un DataFrame con las columnas esperadas y tamaños correctos."""
    sizes = (10, 100, 1000)
    df = run_comparison(sizes=sizes, bias=0.5, seed=42)

    expected_cols = ["n", "caras", "frec_cara", "diferencia_abs", "margen", "veredicto"]
    assert list(df.columns) == expected_cols
    assert len(df) == 3
    assert list(df["n"]) == list(sizes)
    assert set(df["veredicto"]).issubset({"Equilibrada", "Sesgada"})
