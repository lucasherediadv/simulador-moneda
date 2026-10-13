"""Módulo core para la lógica de simulación matemática."""

from core.simulation import (
    SimulationResult,
    error_margin,
    evaluate_fairness,
    relative_frequency,
    run_comparison,
    run_simulation,
)

__all__ = [
    "SimulationResult",
    "run_simulation",
    "relative_frequency",
    "error_margin",
    "evaluate_fairness",
    "run_comparison",
]
