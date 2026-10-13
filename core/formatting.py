"""Helpers puros para mostrar números con convenciones de español."""


def _grouped_number(value: int | float, decimals: int) -> str:
    rendered = f"{value:,.{decimals}f}"
    return rendered.replace(",", "\0").replace(".", ",").replace("\0", ".")


def fmt_int(n: int) -> str:
    """Formatea un entero con punto como separador de miles."""
    return f"{n:,}".replace(",", ".")


def fmt_dec(x: float, dec: int = 2) -> str:
    """Formatea un decimal con coma decimal y punto de miles."""
    return _grouped_number(x, dec)


def fmt_pct(x: float, dec: int = 2) -> str:
    """Formatea una proporción como porcentaje en español."""
    return f"{_grouped_number(x * 100, dec)} %"


def fmt_pp(x: float, dec: int = 2) -> str:
    """Formatea una diferencia expresada en puntos porcentuales."""
    return f"{_grouped_number(x * 100, dec)} puntos porcentuales"
