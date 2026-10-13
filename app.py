"""Aplicación interactiva: ¿La moneda está trucada?

Muestra cómo se comporta la frecuencia relativa y decide con un criterio
estadístico justificable si la moneda parece equilibrada.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.simulation import (
    comparison_interpretation,
    evaluate_fairness,
    run_comparison,
    run_simulation,
)
from core.formatting import fmt_dec, fmt_int

# ==============================================================================
# 3.2 Configuración global
# ==============================================================================
st.set_page_config(
    page_title="¿La moneda está trucada?",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==============================================================================
# Funciones auxiliares para visualización
# ==============================================================================
def create_simulation_plot(
    history: pd.DataFrame, n_flips: int, log_scale: bool
) -> go.Figure:
    """Crea el gráfico de convergencia con Plotly y franja de azar en embudo.

    Args:
        history: DataFrame con columnas lanzamiento, caras_acum, frec_cara, frec_cruz.
        n_flips: Total de lanzamientos realizados.
        log_scale: Si True, el eje horizontal usa escala logarítmica.

    Returns:
        Figura de Plotly configurada.
    """
    x = history["lanzamiento"].to_numpy()
    frec = history["frec_cara"].to_numpy()

    margin = 1.0 / np.sqrt(x)
    upper = np.clip(0.5 + margin, 0.0, 1.0)
    lower = np.clip(0.5 - margin, 0.0, 1.0)

    fig = go.Figure()

    # Franja en embudo: límite superior (invisible)
    fig.add_trace(
        go.Scatter(
            x=x,
            y=upper,
            mode="lines",
            line=dict(color="rgba(0,0,0,0)", width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # Franja en embudo: límite inferior con relleno hasta el superior
    fig.add_trace(
        go.Scatter(
            x=x,
            y=lower,
            mode="lines",
            line=dict(color="rgba(0,0,0,0)", width=0),
            fill="tonexty",
            fillcolor="rgba(180, 180, 180, 0.25)",
            name="Margen esperado por azar (±1/√n)",
            hoverinfo="skip",
        )
    )

    # Línea teórica en 0.5
    fig.add_trace(
        go.Scatter(
            x=[1, n_flips],
            y=[0.5, 0.5],
            mode="lines",
            line=dict(color="#d62728", dash="dash", width=2),
            name="Probabilidad teórica (0,5)",
            hoverinfo="name+y",
        )
    )

    # Serie principal: Frecuencia relativa acumulada (Scattergl para alto rendimiento)
    trace_mode = "lines+markers" if n_flips <= 50 else "lines"
    fig.add_trace(
        go.Scattergl(
            x=x,
            y=frec,
            mode=trace_mode,
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=6) if n_flips <= 50 else None,
            name="Frecuencia relativa acumulada",
            hovertemplate="Lanzamiento: %{x}<br>Frecuencia de caras: %{y:.4f}<extra></extra>",
        )
    )

    xaxis_config = {"type": "log" if log_scale else "linear"}
    if log_scale:
        powers = [10**power for power in range(0, 20) if 10**power <= n_flips]
        xaxis_config.update(tickvals=powers, ticktext=[fmt_int(value) for value in powers])
    else:
        xaxis_config["tickformat"] = ",d"

    fig.update_layout(
        title="Evolución de la frecuencia relativa acumulada de caras",
        xaxis_title="Número de lanzamiento",
        yaxis_title="Frecuencia relativa acumulada",
        yaxis=dict(range=[-0.02, 1.02]),
        xaxis=xaxis_config,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        hovermode="closest",
        separators=",.",
        font=dict(size=14),
    )

    return fig


def format_comparison_table(df: pd.DataFrame) -> pd.DataFrame:
    """Formatea la tabla comparativa con separador de miles y comas decimales."""
    formatted = pd.DataFrame()
    formatted["n"] = df["n"].apply(fmt_int)
    formatted["Caras"] = df["caras"].apply(fmt_int)
    formatted["Frecuencia de caras"] = df["frec_cara"].apply(
        lambda val: fmt_dec(val, 4)
    )
    formatted["|Diferencia con 0,5|"] = df["diferencia_abs"].apply(
        lambda val: fmt_dec(val, 4)
    )
    formatted["Margen esperado (±1/√n)"] = df["margen"].apply(
        lambda val: fmt_dec(val, 4)
    )
    formatted["Veredicto"] = df["veredicto"]
    return formatted


def create_comparison_plot(df: pd.DataFrame) -> go.Figure:
    """Crea el gráfico de convergencia que compara la diferencia absoluta observada contra el margen esperado."""
    fig = go.Figure()

    # Serie 1: Margen esperado por azar
    fig.add_trace(
        go.Scatter(
            x=df["n"],
            y=df["margen"],
            mode="lines+markers",
            name="Margen esperado por azar (1/√n)",
            line=dict(color="#ff7f0e", dash="dash", width=2),
            marker=dict(size=8),
            hovertemplate="n = %{x}<br>Margen teórico: %{y:.4f}<extra></extra>",
        )
    )

    # Serie 2: Diferencia observada
    fig.add_trace(
        go.Scatter(
            x=df["n"],
            y=df["diferencia_abs"],
            mode="lines+markers",
            name="|Frecuencia − 0,5| observada",
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=8),
            hovertemplate="n = %{x}<br>Diferencia observada: %{y:.4f}<extra></extra>",
        )
    )

    max_val = max(0.35, float(df["margen"].max()) * 1.05)

    fig.update_layout(
        title="Convergencia del margen de azar y la diferencia observada",
        xaxis_title="Cantidad de lanzamientos (n, escala logarítmica)",
        yaxis_title="Diferencia respecto a 0,5",
        xaxis=dict(
            type="log",
            tickvals=[10**power for power in range(0, 20) if 10**power <= int(df["n"].max())],
            ticktext=[fmt_int(10**power) for power in range(0, 20) if 10**power <= int(df["n"].max())],
        ),
        yaxis=dict(range=[-0.01, max_val]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=40, r=20, t=60, b=40),
        hovermode="x unified",
        separators=",.",
        font=dict(size=14),
    )

    return fig


# ==============================================================================
# 3.3 Sidebar: "Configuración de la moneda"
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Configuración de la moneda")
    test_mode = st.toggle("Modo prueba: moneda trucada", value=False)
    if test_mode:
        bias = st.slider(
            "Probabilidad real de cara",
            min_value=0.00,
            max_value=1.00,
            value=0.60,
            step=0.01,
        )
    else:
        bias = 0.50

    st.caption(
        "Con el modo apagado la moneda es justa (P(cara) = 0,5). "
        "Con el modo encendido podés probar si la app detecta una moneda alterada."
    )


# ==============================================================================
# 3.4 Encabezado y etiqueta de moneda activa
# ==============================================================================
st.title("🪙 ¿La moneda está trucada?")
st.markdown(
    "Simulá lanzamientos y comprobá si los resultados se parecen a lo que predice la teoría."
)

if test_mode:
    coin_badge = f"Moneda trucada (P(cara) = {fmt_dec(bias)})"
    st.warning(f"🪙 **Moneda activa:** {coin_badge}")
else:
    coin_badge = "Moneda justa"
    st.info("🪙 **Moneda activa:** Moneda justa (P(cara) = 0,50)")

st.write("")


# ==============================================================================
# Estructura de pestañas principales
# ==============================================================================
tab_sim, tab_comp, tab_teoria = st.tabs(
    [
        "🪙 Simulador",
        "📊 Comparar cantidades",
        "📖 Teoría",
    ]
)


# ==============================================================================
# 3.5 Pestaña 1: Simulador
# ==============================================================================
with tab_sim:
    # ① Controles de lanzamiento
    with st.container(border=True):
        col_ctrl1, col_ctrl2 = st.columns([3, 1], vertical_alignment="bottom")
        with col_ctrl1:
            n_flips_selected = st.radio(
                "Cantidad de lanzamientos",
                options=[10, 100, 1000, 10000],
                index=1,
                horizontal=True,
                format_func=fmt_int,
            )
        with col_ctrl2:
            launch_clicked = st.button(
                "🪙 Lanzar moneda",
                type="primary",
                use_container_width=True,
            )

    # Disparador de simulación (guarda en session_state)
    if launch_clicked:
        sim_res = run_simulation(n_flips=n_flips_selected, bias=bias)
        eval_res = evaluate_fairness(heads=sim_res.heads, tails=sim_res.tails)

        label_coin = (
            "moneda justa"
            if bias == 0.50
            else f"moneda trucada (P(cara) = {fmt_dec(bias)})"
        )
        st.session_state["resultado"] = sim_res
        st.session_state["evaluacion"] = eval_res
        st.session_state["rotulo"] = (
            f"Resultado de {fmt_int(n_flips_selected)} lanzamientos · {label_coin}"
        )

    # ② Estado vacío (antes del primer lanzamiento)
    if "resultado" not in st.session_state:
        st.info("Elegí la cantidad de lanzamientos y presioná «Lanzar moneda».")
    else:
        # ③ Resultado del experimento
        sim = st.session_state["resultado"]
        evaluation = st.session_state["evaluacion"]
        rotulo = st.session_state["rotulo"]

        st.divider()

        # 1. Rótulo del experimento (indica origen del resultado visible)
        st.caption(f"📌 **{rotulo}**")

        # 2. Veredicto (lo primero y más visible)
        if evaluation["is_fair"]:
            st.success(
                f"### Veredicto: {evaluation['label']}\n\n{evaluation['message']}"
            )
        else:
            st.warning(
                f"### Veredicto: {evaluation['label']}\n\n{evaluation['message']}"
            )

        st.caption("Criterio: se considera equilibrada si |frecuencia − 0,5| ≤ 1/√n.")

        # 3. Fila de métricas (conteos)
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Caras", fmt_int(sim.heads))
        with col_m2:
            st.metric("Cruces", fmt_int(sim.tails))

        # 4. Tabla comparativa
        df_table = pd.DataFrame(
            {
                "Resultado": ["Cara", "Cruz"],
                "Prob. teórica": ["0,5000", "0,5000"],
                "Frecuencia relativa": [
                    fmt_dec(evaluation["freq_heads"], 4),
                    fmt_dec(evaluation["freq_tails"], 4),
                ],
                "Diferencia": [
                    fmt_dec(evaluation["freq_heads"] - 0.5, 4),
                    fmt_dec(evaluation["freq_tails"] - 0.5, 4),
                ],
            }
        )
        st.dataframe(df_table, hide_index=True, use_container_width=True)

        # 5. Gráfico Plotly
        st.write("")
        col_chart_hdr, col_chart_opt = st.columns([3, 1], vertical_alignment="center")
        with col_chart_hdr:
            st.markdown("#### Gráfico de convergencia")
        with col_chart_opt:
            use_log = st.toggle(
                "Escala logarítmica",
                value=(sim.n_flips >= 100),
                help="Facilita observar los primeros lanzamientos donde la variabilidad es mayor.",
            )

        fig = create_simulation_plot(sim.history, sim.n_flips, log_scale=use_log)
        st.plotly_chart(fig, use_container_width=True)


# ==============================================================================
# 3.6 Pestaña 2: Comparar cantidades
# ==============================================================================
with tab_comp:
    st.subheader("Comparar cantidades de lanzamientos")
    st.markdown(
        "Muestra cómo cambia la diferencia con $n$, ilustrando el comportamiento "
        "de la frecuencia relativa según la **Ley de los grandes números**."
    )

    btn_comp = st.button("🚀 Ejecutar las 4 cantidades", type="primary")

    if btn_comp:
        df_comp = run_comparison(sizes=(10, 100, 1000, 10000), bias=bias)
        label_coin = (
            "moneda justa"
            if bias == 0.50
            else f"moneda trucada (P(cara) = {fmt_dec(bias)})"
        )
        st.session_state["comparativa"] = df_comp
        st.session_state["comparativa_bias"] = bias
        st.session_state["comparativa_rotulo"] = (
            f"Resultados para las 4 cantidades · {label_coin}"
        )

    if "comparativa" not in st.session_state:
        st.info(
            "Presioná «Ejecutar las 4 cantidades» para simular simultáneamente "
            "$n = 10, 100, 1.000$ y $10.000$ con la configuración activa."
        )
    else:
        st.caption(f"📌 **{st.session_state.get('comparativa_rotulo', '')}**")
        df_comp = st.session_state["comparativa"]

        # Tabla comparativa formateada
        df_table = format_comparison_table(df_comp)
        st.dataframe(df_table, hide_index=True, use_container_width=True)

        st.write("")
        # Gráfico comparativo
        fig_comp = create_comparison_plot(df_comp)
        st.plotly_chart(fig_comp, use_container_width=True)

        comparison_bias = st.session_state.get("comparativa_bias", 0.5)
        st.info(
            f"💡 **Interpretación:** *{comparison_interpretation(comparison_bias)}*"
        )

# ==============================================================================
# 3.7 Pestaña 3: Teoría
# ==============================================================================
with tab_teoria:
    st.subheader("Fundamentos de Probabilidad y Estadística")
    st.markdown(
        "Conceptos teóricos de la materia aplicados en este simulador para interpretar "
        "los resultados y justificar las decisiones con rigor estadístico."
    )

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        with st.container(border=True):
            st.markdown("#### 🎲 Experimento Aleatorio e Independencia")
            st.markdown(
                "- **Experimento aleatorio:** Resultado individual impredecible, pero con "
                "resultados posibles bien definidos: $\\{\\text{Cara}, \\text{Cruz}\\}$.\n"
                "- **Independencia:** Cada lanzamiento es independiente de los anteriores. "
                "El resultado de un tiro no condiciona ni altera la probabilidad del siguiente."
            )

        with st.container(border=True):
            st.markdown("#### 📐 Probabilidad Clásica vs. Frecuencial")
            st.markdown(
                "- **Probabilidad clásica (a priori):** Casos favorables sobre casos posibles "
                "(resultados equiprobables):\n\n"
                "  $$P(\\text{Cara}) = \\frac{\\text{Casos favorables}}{\\text{Casos posibles}} = \\frac{1}{2} = 0,50$$\n\n"
                "- **Probabilidad frecuencial (a posteriori):** Se aproxima mediante la experimentación empírica:\n\n"
                "  $$f = \\frac{\\text{Caras observadas}}{n}$$\n\n"
                "  La frecuencia relativa se estabiliza y aproxima a la probabilidad real al crecer $n$."
            )

    with col_t2:
        with st.container(border=True):
            st.markdown("#### 📈 Ley de los Grandes Números")
            st.markdown(
                "Al aumentar $n$, la frecuencia relativa de caras $f$ oscila con menor amplitud y "
                "**se acerca a la probabilidad real de la moneda** ($0,50$ si es justa).\n\n"
                "- Con **$n = 10$**, el azar produce desvíos amplios respecto al 50 %.\n"
                "- Con **$n = 10.000$**, la frecuencia empírica se adhiere fuertemente a la probabilidad real de la moneda."
            )
            st.markdown(
                "En el modo prueba la curva se estabiliza en el valor real de la moneda trucada "
                "(por ejemplo 0,60), no en 0,50: así la aplicación puede detectar el sesgo."
            )

        with st.container(border=True):
            st.markdown("#### ⚖️ Cómo decide la aplicación")
            st.markdown(
                "La aplicación evalúa la equidad comparando la diferencia observada contra el margen de azar esperado:\n\n"
                "$$\\text{Margen} = \\frac{1}{\\sqrt{n}} \\approx 1,96 \\cdot \\sqrt{\\frac{0,5 \\cdot 0,5}{n}} \\quad (\\approx 95\\% \\text{ de confianza})$$\n\n"
                "- **$|f - 0,5| \\le 1/\\sqrt{n}$** $\\rightarrow$ **Equilibrada** (no hay evidencia de que la moneda esté trucada).\n"
                "- **$|f - 0,5| > 1/\\sqrt{n}$** $\\rightarrow$ **Sesgada** (la diferencia supera lo explicable por azar)."
            )
            st.warning(
                "⚠️ **Límite del criterio:** *Es un criterio práctico, no una prueba formal; con pocos lanzamientos "
                "no puede detectar sesgos chicos.* Por eso concluimos «no hay evidencia de sesgo», "
                "**nunca** «queda demostrado que es justa»."
            )
