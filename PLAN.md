# PLAN: Simulador "¿La moneda está trucada?"

> Estadística y Probabilidad Aplicada — Unidad 2, Ejercicio 2.
> Stack: Python · Streamlit · Plotly · NumPy/Pandas · pytest.

---

## 0. Objetivo y principios de diseño

Simular lanzamientos de una moneda, mostrar cómo se comporta la frecuencia relativa y **decidir con un criterio justificable** si la moneda parece equilibrada.

Principios que guían todas las decisiones de abajo:

1. **Una pantalla, un recorrido:** *elegir → lanzar → leer el veredicto → ver la evidencia*. Lo primero que se ve es la conclusión; el detalle viene después.
2. **Poca información por vez:** lo secundario (comparativa y teoría) va en pestañas, no apilado en una sola página larga.
3. **Pensado para exponer:** legible en proyector, sin scroll para el flujo principal, y con una demo de moneda trucada a un clic.
4. **El criterio de decisión debe converger con n:** la tolerancia se achica al aumentar los lanzamientos, igual que la frecuencia relativa.

---

## 1. Estructura del proyecto

```
simulador-moneda/
├── app.py                    # Capa de presentación (Streamlit)
├── core/
│   ├── __init__.py
│   ├── formatting.py        # Formato numérico en español
│   └── simulation.py         # Lógica matemática (sin Streamlit)
├── tests/
│   ├── test_simulation.py    # Pruebas unitarias (pytest)
│   └── test_formatting.py    # Pruebas de formato numérico
├── pytest.ini                # pythonpath = .
├── requirements.txt          # streamlit, plotly, pandas, numpy, pytest
└── README.md                 # Cómo instalar, ejecutar y testear
```

Regla de oro: `core/` **no importa** Streamlit ni Plotly. Así se puede testear y explicar por separado.

`pytest.ini`:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

---

## 2. Capa de lógica (`core/simulation.py`)

### 2.1 Tipos de datos

```python
@dataclass(frozen=True)
class SimulationResult:
    n_flips: int
    bias: float                # P(cara) realmente usada
    heads: int
    tails: int
    history: pd.DataFrame      # columnas: lanzamiento, caras_acum, frec_cara, frec_cruz
```

### 2.2 Funciones

| Función | Descripción |
|---|---|
| `run_simulation(n_flips, bias=0.5, seed=None)` | Genera `n_flips` lanzamientos con `numpy.random.default_rng(seed)`: `flips = rng.random(n) < bias`. Devuelve `SimulationResult`. El `history` contiene la frecuencia relativa acumulada tiro a tiro (`cumsum / arange(1, n+1)`). |
| `relative_frequency(count, n)` | `count / n`. Valida `n > 0` y `0 ≤ count ≤ n`. |
| `error_margin(n)` | Margen de azar esperado: `1 / sqrt(n)`. |
| `evaluate_fairness(heads, tails, tolerance=None)` | Dictamen (ver 2.3). Si `tolerance` es `None` usa `error_margin(n)`; si se pasa un número, usa esa tolerancia fija (permite comparar ambos criterios). |
| `run_comparison(sizes=(10, 100, 1000, 10000), bias=0.5, seed=None)` | Corre un experimento por tamaño y devuelve un `DataFrame` con: `n`, `caras`, `frec_cara`, `diferencia_abs`, `margen`, `veredicto`. |

**Validaciones** (lanzar `ValueError`): `n_flips` entero ≥ 1 y `bias` en [0, 1].

### 2.3 Criterio de equidad (reemplaza a la tolerancia fija de 0.05)

**Problema de la tolerancia fija:** con ±0.05, para n = 10 solo 5 caras cuentan como "equilibrada" (una moneda justa sería declarada sesgada ~75 % de las veces), y para n = 10.000 una moneda con P(cara) = 0.54 (≈ 8 desvíos estándar de lo esperado) pasaría como "equilibrada" ~98 % de las veces.

**Criterio nuevo:**

```
f      = caras / n                  # frecuencia relativa de caras
margen = 1 / sqrt(n)                # ≈ 1.96 · sqrt(0.5·0.5 / n)  (≈ 95 % de confianza)
diferencia = |f − 0.5|

diferencia ≤ margen  →  "Equilibrada"
diferencia  > margen →  "Sesgada"
```

Equivalente en conteos: `|caras − n/2| ≤ √n`.

| n | Margen | Caras compatibles con moneda justa |
|---|---|---|
| 10 | ±0.316 | 2 a 8 |
| 100 | ±0.100 | 40 a 60 |
| 1.000 | ±0.032 | 469 a 531 |
| 10.000 | ±0.010 | 4.900 a 5.100 |

Comportamiento verificado (probabilidad exacta de que el criterio diga "Equilibrada"):

| P(cara) real | n = 10 | n = 100 | n = 1.000 | n = 10.000 |
|---|---|---|---|---|
| 0.50 (justa) | 98 % | 96 % | 95 % | 96 % |
| 0.55 | 97 % | 87 % | 12 % | 0 % |
| 0.60 | 95 % | 54 % | 0 % | 0 % |
| 0.70 | 85 % | 2 % | 0 % | 0 % |

Lectura: con pocos lanzamientos casi cualquier moneda parece justa (poca capacidad de detección); con muchos, hasta sesgos pequeños se detectan. Eso es exactamente lo que enseña la ley de los grandes números, y se usa en la exposición.

**Valor devuelto por `evaluate_fairness`** (diccionario, para testear el booleano y no el texto):

```python
{
  "is_fair": bool,
  "label": "Equilibrada" | "Sesgada",
  "n": int,
  "freq_heads": float, "freq_tails": float,
  "difference": float,      # |f − 0.5|
  "margin": float,
  "message": str,           # justificación interpretada
  "low_n_warning": bool,    # True si n < 100
}
```

**Plantillas de `message`:**

- Equilibrada: *"Con {n} lanzamientos, la frecuencia de caras fue {f:.2%}, a {d:.2%} de la probabilidad teórica (50 %). Esa diferencia está dentro del margen que el azar explica (±{m:.2%}), por lo que no hay evidencia de que la moneda esté trucada."*
- Sesgada: *"…esa diferencia supera el margen que el azar explica (±{m:.2%}), por lo que es poco probable que se deba solo a la casualidad: la moneda parece sesgada."*
- Si `low_n_warning`: agregar *"Con pocos lanzamientos el margen es amplio: incluso una moneda sesgada puede parecer equilibrada."*

Importante en la redacción: "no hay evidencia de sesgo", **nunca** "queda demostrado que es justa".

---

## 3. Capa de presentación (`app.py`)

### 3.1 Evaluación de la UI/UX del plan original

| Elemento del plan v1 | Evaluación | Decisión v2 |
|---|---|---|
| Sidebar con 4 botones de lanzamiento | Funciona, pero cada botón lanza al instante y mezcla "configurar" con "ejecutar". En proyector, el sidebar compite con el contenido. | Elegir n en el área principal (`st.radio` horizontal) y un único botón primario **"Lanzar moneda"**. |
| Checkbox "Modo Prueba" + slider | Correcto como idea (es la demo clave). | Se mantiene, pero en el **sidebar como "Configuración de la moneda"**, porque es un ajuste global que afecta a todas las pestañas. |
| Todo en una página (métricas, tabla, veredicto, gráfico, 3 expanders) | Demasiada información simultánea; no hay jerarquía clara. | Pestañas: **Simulador · Comparar cantidades · Teoría**; en Simulador, veredicto primero. |
| Teoría en `st.expander` al final | Queda enterrada bajo scroll; mala para exponer. | Pestaña propia **Teoría**. |
| `session_state` "para que no se borre al abrir un expander" | Justificación incorrecta (abrir un expander no reejecuta el script). | Se mantiene `session_state`, por el motivo real: mover el slider o el radio reejecuta el script y `st.button` vuelve a `False`, borrando los resultados. |
| Downsampling > 1.000 puntos | Innecesario: Plotly maneja 10.000 puntos con `Scattergl`, y descartar puntos pierde el comienzo, que es lo más informativo. | Se elimina. Se grafican todos los puntos. |
| "Curva logarítmica" | Término incorrecto. | Se habla de *oscilaciones que se amortiguan* (~1/√n). Eje X logarítmico opcional para ver los primeros tiros. |
| Franja de tolerancia constante | Con criterio dependiente de n queda inconsistente. | Franja en forma de **embudo** `0.5 ± 1/√n`. |
| Estado inicial | No definido (pantalla vacía o confusa). | Mensaje guía hasta el primer lanzamiento. |

### 3.2 Configuración global

```python
st.set_page_config(page_title="¿La moneda está trucada?", page_icon="🪙", layout="wide")
```

### 3.3 Sidebar: "Configuración de la moneda"

- `st.toggle("Modo prueba: moneda trucada")`, apagado por defecto.
- Al activarlo aparece `st.slider("Probabilidad real de cara", 0.00, 1.00, 0.60, 0.01)`.
- Texto de ayuda: *"Con el modo apagado la moneda es justa (P(cara) = 0,5). Con el modo encendido podés probar si la app detecta una moneda alterada."*
- Si el modo está apagado, `bias = 0.5`.

### 3.4 Encabezado

Título y una línea de subtítulo (*"Simulá lanzamientos y comprobá si los resultados se parecen a lo que predice la teoría."*). Debajo, una etiqueta con la moneda activa: **"Moneda justa"** o **"Moneda trucada (P(cara) = 0,60)"**, visible en todas las pestañas.

### 3.5 Pestaña 1: Simulador

Flujo vertical:

**① Controles** (contenedor con borde, en una fila):
- `st.radio("Cantidad de lanzamientos", [10, 100, 1000, 10000], horizontal=True, format_func=<con separador de miles>)`
- `st.button("Lanzar moneda", type="primary")`

**② Estado vacío** (antes del primer lanzamiento): `st.info("Elegí la cantidad de lanzamientos y presioná «Lanzar moneda».")`

**③ Resultado** (solo si hay experimento guardado en `session_state`):

1. **Rótulo del experimento** (siempre visible, evita confusión si se mueven los controles después de lanzar): *"Resultado de 1.000 lanzamientos · moneda justa"*.
2. **Veredicto** (lo primero y más grande): `st.success` (equilibrada) o `st.warning` (sesgada) con título + `message`; debajo, `st.caption` con el criterio: *"Criterio: se considera equilibrada si |frecuencia − 0,5| ≤ 1/√n."*
3. **Fila de métricas** (2 columnas): `st.metric("Caras", conteo)` y `st.metric("Cruces", conteo)`.
4. **Tabla comparativa** (`st.dataframe` / `st.table`, sin índice):

   | Resultado | Prob. teórica | Frecuencia relativa | Diferencia |
   |---|---|---|---|
   | Cara | 0,5000 | 0,5130 | +0,0130 |
   | Cruz | 0,5000 | 0,4870 | −0,0130 |

5. **Gráfico Plotly** (ver 3.8).

### 3.6 Pestaña 2: Comparar cantidades

Muestra cómo cambia la diferencia con n (el corazón de "comportamiento de la frecuencia relativa").

- Botón **"Ejecutar las 4 cantidades"** (usa la moneda del sidebar), resultado guardado en `session_state["comparativa"]`.
- Tabla: n · caras · frecuencia de caras · |diferencia| · margen 1/√n · veredicto.
- Un gráfico pequeño: |diferencia| y margen vs n (eje X logarítmico), donde se ve que ambas se achican.
- Frase de interpretación dependiente de la moneda ejecutada: si es justa, *"Al aumentar n, la frecuencia relativa se acerca a la probabilidad teórica y las diferencias por azar se reducen."*; si es trucada, explica que se estabiliza alrededor de la probabilidad real y la diferencia con la teórica no desaparece.

### 3.7 Pestaña 3: Teoría

Contenido breve y con ejemplos de esta app (no definiciones copiadas):

- **Experimento aleatorio:** resultado impredecible individualmente, pero con resultados posibles conocidos (cara, cruz). Cada lanzamiento es independiente.
- **Probabilidad clásica:** P(A) = casos favorables / casos posibles (resultados equiprobables). Cara: 1/2 = 0,5.
- **Probabilidad frecuencial:** P(A) ≈ frecuencia relativa f = caras/n, y se estabiliza al crecer n.
- **Ley de los grandes números:** al aumentar n, f se acerca a la probabilidad real de la moneda (0,50 si es justa). En modo prueba, la curva se estabiliza en el valor real de la moneda trucada (por ejemplo, 0,60), no en 0,50.
- **Cómo decide la app:** explicación de `margen = 1/√n` en tres líneas, y el límite: *"Es un criterio práctico, no una prueba formal; con pocos lanzamientos no puede detectar sesgos chicos."*

### 3.8 Gráfico (Plotly)

- Eje X: número de lanzamiento. Eje Y: frecuencia relativa acumulada de caras, rango [0, 1].
- Serie principal: `go.Scattergl`, todos los puntos (sin downsampling).
- Línea horizontal **roja punteada** en y = 0,5 (probabilidad teórica).
- Franja gris translúcida **en embudo** `0.5 ± 1/√x` (recortada a [0, 1]), con leyenda "Margen esperado por azar".
- Toggle `st.toggle("Escala logarítmica", value=(n >= 100))` junto al gráfico.
- Título y ejes en español, hover con lanzamiento y frecuencia.

### 3.9 Gestión de estado

```python
st.session_state["resultado"]    # SimulationResult del último experimento
st.session_state["comparativa"]  # DataFrame de la comparativa
```

- Los experimentos solo se ejecutan al presionar su botón (nunca al mover un slider o radio).
- El rótulo del experimento (3.5-①) siempre indica con qué configuración se obtuvo el resultado mostrado.

### 3.10 Accesibilidad y proyector

- No depender solo del color: el veredicto lleva texto explícito (Equilibrada/Sesgada).
- Textos de al menos tamaño por defecto de Streamlit; evitar tablas con más de 5 columnas.
- Todos los textos en español rioplatense neutro y consistente.

---

## 4. Pruebas unitarias (`tests/test_simulation.py`)

Semilla fija `seed=42` para reproducibilidad. Valores verificados con NumPy:
`bias=0.5, n=10.000 → 4.991 caras`; `bias=0.54, n=10.000 → 5.434 caras`.

**Evaluador**

| Test | Qué verifica |
|---|---|
| `test_fair_coin_evaluation` | 510 caras en 1.000 → `is_fair is True`, `label == "Equilibrada"`. |
| `test_biased_coin_evaluation` | 700 caras en 1.000 → `is_fair is False`, `label == "Sesgada"`. |
| `test_small_n_is_lenient` | 6 caras en 10 → equilibrada (el criterio antiguo la rechazaba). |
| `test_large_n_detects_small_bias` | 5.400 caras en 10.000 → sesgada (el criterio antiguo la aceptaba). |
| `test_fixed_tolerance_override` | `tolerance=0.05` aplica la tolerancia fija cuando se pasa. |
| `test_margin_decreases_with_n` | `error_margin(10) > error_margin(100) > error_margin(1000) > error_margin(10000)`. |

**Simulación**

| Test | Qué verifica |
|---|---|
| `test_counts_add_up` | `heads + tails == n_flips` para varios n. |
| `test_history_consistency` | `len(history) == n`, la última `frec_cara == heads/n`, y `frec_cara + frec_cruz == 1`. |
| `test_probability_bounds` | Toda frecuencia relativa del historial está en [0, 1]. |
| `test_extreme_bias` | `bias=0` → 0 caras; `bias=1` → n caras. |
| `test_reproducible_with_seed` | Dos corridas con la misma semilla dan lo mismo. |
| `test_simulated_fair_coin_is_fair` | `bias=0.5, n=10000, seed=42` → "Equilibrada". |
| `test_simulated_biased_coin_detected` | `bias=0.54, n=10000, seed=42` → "Sesgada". |

**Validaciones**

| Test | Qué verifica |
|---|---|
| `test_invalid_inputs_raise` | `n_flips=0`, `n_flips=-5`, `bias=-0.1`, `bias=1.2` → `ValueError`. |

Evitar tests justo en el borde del margen (error de punto flotante); usar valores claramente dentro o fuera.

---

## 5. Trazabilidad: consigna ↔ plan

| Consigna | Dónde se cumple |
|---|---|
| Lanzamientos 10, 100, 1.000, 10.000 | Radio de cantidades (§3.5) y comparativa (§3.6). |
| Cantidad de caras y cruces | `st.metric` (§3.5-3). |
| Frecuencia relativa de caras y cruces | Tabla comparativa, filas Cara y Cruz (§3.5-4). |
| Probabilidad teórica de cara y cruz | Columna "Prob. teórica" y pestaña Teoría. |
| Comparar con la teórica | Columna Diferencia, línea y embudo del gráfico. |
| ¿Es equilibrada? + justificación | `evaluate_fairness` y veredicto (§2.3, §3.5-2). |
| Req. común 1: ingresar/generar/modificar datos | Cantidad de lanzamientos y modo prueba con slider. |
| Req. común 2: resultados claros e interpretados | Veredicto interpretado, rótulo del experimento, frase de interpretación en comparativa. |
| Req. común 3: cálculos correctos | Funciones de `core/` + tests (§4). |
| Req. común 4: conceptos de probabilidad | Pestaña Teoría (§3.7). |
| Req. común 5: ejemplos de prueba | Modo prueba (§3.3) y pytest (§4). |
| Req. común 6: explicación para la exposición | Pestaña Teoría y guion de demo (§6). |

---

## 6. Guion sugerido para la exposición (3–5 min)

1. **Teoría (30 s):** pestaña Teoría: experimento aleatorio, probabilidad clásica (0,5) vs frecuencial.
2. **Moneda justa (1 min):** lanzar 10 → resultado irregular; lanzar 10.000 → la curva se pega a 0,5. Mostrar el embudo.
3. **Comparar cantidades (1 min):** pestaña Comparar: la diferencia se achica con n.
4. **Moneda trucada (1 min):** activar modo prueba con 0,60: con 10 lanzamientos probablemente no se detecta; con 1.000 sí. Explicar por qué.
5. **Código y tests (1 min):** mostrar `core/simulation.py` y correr `pytest`.

---

## 7. Orden de implementación y definición de "terminado"

1. `core/simulation.py` + `tests/` (pytest en verde antes de tocar la interfaz).
2. `app.py`: sidebar, pestaña Simulador (controles → veredicto → métricas → tabla → gráfico).
3. Pestaña Comparar cantidades.
4. Pestaña Teoría.
5. `requirements.txt`, `README.md`, revisión con el guion de §6.

Terminado cuando: `pytest` pasa completo; `streamlit run app.py` funciona sin errores con n = 10, 100, 1.000 y 10.000 en modo justo y trucado; y cada fila de §5 se puede mostrar en pantalla.
