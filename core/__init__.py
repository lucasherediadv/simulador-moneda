"""Módulo core para la lógica de simulación matemática."""

from core.simulation import (
    MAX_FLIPS,
    SimulationResult,
    error_margin,
    evaluate_fairness,
    relative_frequency,
    run_comparison,
    run_simulation,
)

__all__ = [
    "MAX_FLIPS",
    "SimulationResult",
    "run_simulation",
    "relative_frequency",
    "error_margin",
    "evaluate_fairness",
    "run_comparison",
]
