from core.formatting import fmt_dec, fmt_int, fmt_pct, fmt_pp


def test_format_numbers_in_spanish():
    assert fmt_int(10000) == "10.000"
    assert fmt_dec(0.6) == "0,60"
    assert fmt_pct(0.6016) == "60,16 %"
    assert fmt_pp(0.1016) == "10,16 puntos porcentuales"
    assert fmt_int(1) == "1"
    assert fmt_int(999) == "999"
    assert fmt_int(100000) == "100.000"
    assert fmt_dec(0.5, 4) == "0,5000"
