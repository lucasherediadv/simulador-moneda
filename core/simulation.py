"""Lógica matemática y estadística para la simulación de monedas.

Este módulo no depende de Streamlit ni Plotly, facilitando su prueba unitaria
y desacoplamiento arquitectónico.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np
import pandas as pd

from core.formatting import fmt_dec, fmt_int, fmt_pct, fmt_pp


@dataclass(frozen=True)
class SimulationResult:
    """Resultado inmutable de una serie de lanzamientos de moneda."""

    n_flips: int
    bias: float  # P(cara) teórica/usada
    heads: int
    tails: int
    history: pd.DataFrame  # columnas: lanzamiento, caras_acum, frec_cara, frec_cruz


def relative_frequency(count: int, n: int) -> float:
    """Calcula la frecuencia relativa de un suceso.

    Args:
        count: Cantidad de ocurrencias del suceso (0 <= count <= n).
        n: Total de observaciones (n > 0).

    Returns:
        Frecuencia relativa en el intervalo [0, 1].

    Raises:
        ValueError: Si n <= 0 o count está fuera de [0, n].
    """
    if not isinstance(n, (int, np.integer)) or isinstance(n, bool) or n <= 0:
        raise ValueError(f"El total n debe ser un entero positivo (> 0), recibido: {n}")
    if (
        not isinstance(count, (int, np.integer))
        or isinstance(count, bool)
        or count < 0
        or count > n
    ):
        raise ValueError(
            f"El conteo count debe ser un entero entre 0 y {n}, recibido: {count}"
        )

    return float(count / n)


def error_margin(n: int) -> float:
    """Calcula el margen de azar esperado como 1 / sqrt(n).

    Args:
        n: Cantidad de lanzamientos (n > 0).

    Returns:
        Margen de tolerancia esperado para un nivel de confianza de ~95%.

    Raises:
        ValueError: Si n <= 0.
    """
    if not isinstance(n, (int, np.integer)) or isinstance(n, bool) or n <= 0:
        raise ValueError(f"n debe ser un entero positivo (> 0), recibido: {n}")

    return 1.0 / math.sqrt(n)


def evaluate_fairness(
    heads: int, tails: int, tolerance: float | None = None
) -> dict[str, Any]:
    """Evalúa si una moneda parece equilibrada según la evidencia observada.

    Args:
        heads: Conteo observado de caras (>= 0).
        tails: Conteo observado de cruces (>= 0).
        tolerance: Tolerancia fija opcional. Si es None, utiliza el margen
            teórico dependiente de la muestra error_margin(n) = 1 / sqrt(n).

    Returns:
        Diccionario con el diagnóstico, métricas y justificación interpretada:
            - is_fair (bool): True si la diferencia no supera el margen.
            - label (str): 'Equilibrada' o 'Sesgada'.
            - n (int): Total de lanzamientos.
            - freq_heads (float): Frecuencia relativa de caras.
            - freq_tails (float): Frecuencia relativa de cruces.
            - difference (float): |freq_heads - 0.5|.
            - margin (float): Margen de tolerancia aplicado.
            - message (str): Justificación en lenguaje claro.
            - low_n_warning (bool): True si n < 100.

    Raises:
        ValueError: Si heads o tails son negativos, o si su suma es 0.
    """
    if (
        not isinstance(heads, (int, np.integer))
        or isinstance(heads, bool)
        or heads < 0
    ):
        raise ValueError(f"heads debe ser un entero >= 0, recibido: {heads}")
    if (
        not isinstance(tails, (int, np.integer))
        or isinstance(tails, bool)
        or tails < 0
    ):
        raise ValueError(f"tails debe ser un entero >= 0, recibido: {tails}")

    n = int(heads + tails)
    if n <= 0:
        raise ValueError("El total de lanzamientos (heads + tails) debe ser mayor a 0")

    freq_heads = heads / n
    freq_tails = tails / n
    difference = abs(freq_heads - 0.5)

    if tolerance is not None:
        if tolerance < 0:
            raise ValueError(
                f"La tolerancia fija no puede ser negativa, recibido: {tolerance}"
            )
        margin = float(tolerance)
    else:
        margin = error_margin(n)

    is_fair = difference <= margin
    label = "Equilibrada" if is_fair else "Sesgada"
    low_n_warning = n < 100

    if is_fair:
        message = (
            f"Con {fmt_int(n)} lanzamientos, la frecuencia de caras fue {fmt_pct(freq_heads)}, a {fmt_pp(difference)} "
            f"de la probabilidad teórica (50 %). Esa diferencia está dentro del margen que el azar "
            f"explica (±{fmt_pp(margin)}), por lo que no hay evidencia de que la moneda esté trucada."
        )
    else:
        message = (
            f"Con {fmt_int(n)} lanzamientos, la frecuencia de caras fue {fmt_pct(freq_heads)}, a {fmt_pp(difference)} "
            f"de la probabilidad teórica (50 %). Esa diferencia supera el margen que el azar "
            f"explica (±{fmt_pp(margin)}), por lo que es poco probable que se deba solo a la casualidad: "
            f"la moneda parece sesgada."
        )

    if low_n_warning:
        message += (
            " Con pocos lanzamientos el margen es amplio: incluso una moneda sesgada puede parecer equilibrada."
        )

    return {
        "is_fair": is_fair,
        "label": label,
        "n": n,
        "freq_heads": freq_heads,
        "freq_tails": freq_tails,
        "difference": difference,
        "margin": margin,
        "message": message,
        "low_n_warning": low_n_warning,
    }


def comparison_interpretation(bias: float) -> str:
    """Explica la convergencia según la probabilidad real de la moneda."""
    if abs(bias - 0.5) < 1e-9:
        return (
            "Al aumentar n, la frecuencia relativa se acerca a la probabilidad "
            "teórica y las diferencias por azar se reducen."
        )
    return (
        "Al aumentar n, la frecuencia relativa se estabiliza, pero alrededor "
        f"de la probabilidad real de la moneda ({fmt_dec(bias)}) y no de 0,5. "
        "Por eso la diferencia con la teórica no desaparece, mientras que el "
        "margen del azar sí se achica: cuando n es suficientemente grande, el "
        "criterio detecta el sesgo."
    )


def run_simulation(
    n_flips: int, bias: float = 0.5, seed: int | np.random.Generator | None = None
) -> SimulationResult:
    """Simula una serie de lanzamientos de moneda y calcula la evolución tiro a tiro.

    Args:
        n_flips: Cantidad de lanzamientos a simular (entero >= 1).
        bias: Probabilidad real de obtener cara en cada tiro (en [0, 1]).
        seed: Semilla entera o instancia de numpy.random.Generator para reproducibilidad.

    Returns:
        SimulationResult con los conteos finales y el historial acumulado.

    Raises:
        ValueError: Si n_flips < 1 o bias no está en [0, 1].
    """
    if (
        not isinstance(n_flips, (int, np.integer))
        or isinstance(n_flips, bool)
        or n_flips < 1
    ):
        raise ValueError(f"n_flips debe ser un entero >= 1, recibido: {n_flips}")

    if (
        not isinstance(bias, (int, float, np.floating, np.integer))
        or isinstance(bias, bool)
        or not (0.0 <= float(bias) <= 1.0)
    ):
        raise ValueError(f"bias debe estar en el intervalo [0, 1], recibido: {bias}")

    bias_float = float(bias)
    rng = seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)

    flips = rng.random(n_flips) < bias_float
    heads = int(np.sum(flips))
    tails = int(n_flips - heads)

    lanzamiento = np.arange(1, n_flips + 1, dtype=int)
    caras_acum = np.cumsum(flips, dtype=int)
    frec_cara = caras_acum / lanzamiento
    frec_cruz = 1.0 - frec_cara

    history = pd.DataFrame(
        {
            "lanzamiento": lanzamiento,
            "caras_acum": caras_acum,
            "frec_cara": frec_cara,
            "frec_cruz": frec_cruz,
        }
    )

    return SimulationResult(
        n_flips=int(n_flips),
        bias=bias_float,
        heads=heads,
        tails=tails,
        history=history,
    )


def run_comparison(
    sizes: Sequence[int] = (10, 100, 1000, 10000),
    bias: float = 0.5,
    seed: int | np.random.Generator | None = None,
) -> pd.DataFrame:
    """Ejecuta experimentos para distintos tamaños de muestra y compara resultados.

    Args:
        sizes: Secuencia de tamaños de lanzamientos a evaluar.
        bias: Probabilidad de cara para los experimentos.
        seed: Semilla para reproducibilidad secuencial.

    Returns:
        DataFrame con columnas: n, caras, frec_cara, diferencia_abs, margen, veredicto.
    """
    rng = seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)
    rows = []

    for n in sizes:
        sim = run_simulation(n_flips=n, bias=bias, seed=rng)
        fairness = evaluate_fairness(heads=sim.heads, tails=sim.tails)
        rows.append(
            {
                "n": n,
                "caras": sim.heads,
                "frec_cara": fairness["freq_heads"],
                "diferencia_abs": fairness["difference"],
                "margen": fairness["margin"],
                "veredicto": fairness["label"],
            }
        )

    return pd.DataFrame(rows)
