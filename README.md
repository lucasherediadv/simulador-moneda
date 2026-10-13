# ¿La moneda está trucada? 🪙

> **Estadística y Probabilidad Aplicada** — Unidad 2, Ejercicio 2  
> **Stack:** Python 3 · Streamlit · Plotly · NumPy · Pandas · pytest

Simulador interactivo que analiza el comportamiento de la frecuencia relativa en lanzamientos de monedas y determina, mediante un criterio estadístico dinámico y justificable, si una moneda parece equilibrada o sesgada.

---

## 🎯 Características Principales

1. **Una pantalla, un recorrido claro:** *Elegir tamaño → Lanzar → Leer el veredicto justificado → Analizar la evidencia empírica*.
2. **Criterio de decisión dinámico ($1/\sqrt{n}$):** Reemplaza las tolerancias fijas arbitrarias (como $\pm 0,05$) por un margen que converge con el tamaño de muestra según la Ley de los Grandes Números (nivel de confianza $\approx 95\%$).
3. **Modo prueba (Moneda trucada):** Permite alterar deliberadamente la probabilidad de cara ($P(\text{cara}) \in [0, 1]$) para demostrar cómo muestras grandes desenmascaran sesgos sutiles que muestras pequeñas no logran detectar.
4. **Visualizaciones interactivas con Plotly:** Gráficos de alta velocidad (`Scattergl`) con franja de azar esperada en embudo ($\pm 1/\sqrt{x}$), línea de referencia teórica y escala logarítmica.
5. **Arquitectura limpia y desacoplada:** La lógica matemática (`core/`) no depende de la interfaz de usuario ni de librerías visuales, garantizando testeabilidad unitaria completa.

---

## 📂 Estructura del Proyecto

```
simulador-moneda/
├── app.py                    # Capa de presentación (Streamlit + Plotly)
├── core/
│   ├── __init__.py           # Exportación del paquete matemático
│   └── simulation.py         # Lógica pura de simulación y evaluación estadística
├── tests/
│   ├── __init__.py
│   └── test_simulation.py    # Suite completa de pruebas unitarias (22 tests)
├── pytest.ini                # Configuración de pytest (pythonpath y testpaths)
├── requirements.txt          # Dependencias del proyecto
├── CONSIGNA.md               # Requerimientos originales de la cátedra
├── PLAN.md                   # Plan de arquitectura y diseño detallado
└── README.md                 # Guía de instalación, uso y guion de exposición
```

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar o acceder al repositorio

```bash
cd simulador-moneda
```

### 2. Crear y activar un entorno virtual (recomendado)

```bash
python3 -m venv .venv
source .venv/bin/activate    # En Linux / macOS
# o en Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador web (por defecto en `http://localhost:8501`).

---

## 🧪 Pruebas Unitarias

La suite de pruebas valida exhaustivamente la lógica matemática, la consistencia del historial acumulado, el margen dinámico y el manejo de excepciones:

```bash
pytest -v
```

Todas las **22 pruebas** deben estar en estado **PASSED**.

---

## 📊 Criterio Estadístico de Equidad

A diferencia de un criterio de tolerancia fija (como $\pm 0,05$), que declararía sesgada al azar una moneda justa en $n = 10$ el $75\%$ de las veces o pasaría por alto una moneda trucada con $P = 0,54$ en $n = 10.000$, la aplicación emplea un margen que se ajusta a la dispersión esperada por el azar:

$$\text{Margen de azar} = \frac{1}{\sqrt{n}} \approx 1,96 \cdot \sqrt{\frac{0,5 \cdot 0,5}{n}} \quad (\approx 95\% \text{ de confianza})$$

* Si $|\text{Frecuencia observada} - 0,50| \le 1/\sqrt{n} \implies$ **Equilibrada** (no hay evidencia de sesgo).
* Si $|\text{Frecuencia observada} - 0,50| > 1/\sqrt{n} \implies$ **Sesgada** (la desviación supera lo atribuible al azar).

| $n$ | Margen esperado | Rango de caras compatibles con moneda justa |
|:---:|:---:|:---:|
| **10** | $\pm 0,316$ | 2 a 8 |
| **100** | $\pm 0,100$ | 40 a 60 |
| **1.000** | $\pm 0,032$ | 469 a 531 |
| **10.000** | $\pm 0,010$ | 4.900 a 5.100 |

> **Rigor pedagógico:** Cuando la moneda parece equilibrada, la app concluye *«no hay evidencia de que la moneda esté trucada»*, y **nunca** afirma *«queda demostrado que es justa»*.

---

## 🎤 Guion Sugerido para la Exposición Oral (3 a 5 min)

1. **Introducción teórica (30 s):**
   * Abrir la pestaña **📖 Teoría**.
   * Explicar el concepto de **experimento aleatorio** e **independencia** en el tiro de monedas.
   * Diferenciar **probabilidad clásica** ($P = 0,50$ *a priori*) de la **frecuencia relativa** ($f = \text{caras}/n$ *a posteriori*).
2. **Demostración con Moneda Justa (1 min):**
   * En la pestaña **🪙 Simulador**, lanzar $n = 10$: notar la alta dispersión y el margen amplio.
   * Lanzar $n = 10.000$: señalar cómo la curva se adhiere a la línea teórica de $0,50$ y queda contenida en el embudo sombreado de azar.
3. **Comparativa entre tamaños (1 min):**
   * Pasar a la pestaña **📊 Comparar cantidades** y presionar *"Ejecutar las 4 cantidades"*.
   * Mostrar en la tabla y en el gráfico cómo tanto el margen de azar como la diferencia observada decrecen monótonamente hacia cero (**Ley de los Grandes Números**).
4. **Demostración con Moneda Trucada (1 min):**
   * En el sidebar, activar el **Modo prueba** y fijar la probabilidad en $0,60$.
   * Volver a la pestaña **🪙 Simulador**:
     * Con $n = 10$, mostrar que la moneda suele ser declarada "Equilibrada" porque el margen por azar es muy ancho y la app advierte sobre la baja capacidad de detección.
     * Con $n = 1.000$ o $n = 10.000$, relanzar y mostrar cómo el veredicto pasa a "Sesgada" con certeza casi absoluta.
5. **Arquitectura y Calidad de Código (30 s):**
   * Mencionar la separación de responsabilidades: `core/simulation.py` sin dependencias gráficas.
   * Ejecutar `pytest -v` en terminal para exhibir la verificación automatizada en verde.

---

## 📋 Trazabilidad con la Consigna

| Requerimiento de la Consigna | Implementación en el Proyecto |
|---|---|
| Lanzamientos de 10, 100, 1.000 y 10.000 | Selector horizontal en pestaña *Simulador* y simulación simultánea en *Comparar cantidades*. |
| Cantidad de caras y cruces | Métricas destacadas (`st.metric`) en el resultado del experimento. |
| Frecuencia relativa de caras y cruces | Tabla comparativa formateada tiro a tiro y final. |
| Probabilidad teórica de cara y cruz | Columna dedicada en tabla comparativa ($0,5000$) y línea de referencia roja en gráficos. |
| Comparar con la probabilidad teórica | Columna *Diferencia* con signo, embudo en el gráfico y comparativa logarítmica. |
| ¿Es equilibrada? + justificación | Función `evaluate_fairness` con veredicto prioritario, explicación en lenguaje natural y margen $1/\sqrt{n}$. |
| Req. Común 1: Ingresar/modificar datos | Selector de tamaño (10, 100, 1.000, 10.000), opción *"Otra cantidad"* con campo numérico libre (1 a 100.000) y slider de sesgo en el sidebar. |
| Req. Común 2: Resultados claros e interpretados | Veredicto destacado al inicio, rótulo del experimento y advertencia ante bajo $n$. |
| Req. Común 3: Cálculos matemáticamente correctos | Módulo desacoplado `core/simulation.py` validado con **22 tests** en `pytest`. |
| Req. Común 4: Conceptos de probabilidad integrados | Pestaña dedicada *Teoría* con definiciones, fórmulas LaTeX y límites del modelo. |
| Req. Común 5: Ejemplos de prueba | Modo interactivo de moneda trucada en el sidebar y suite de pruebas unitarias. |
| Req. Común 6: Preparación para exposición oral | Pestaña *Teoría* estructurada y guion guiado paso a paso en este documento. |
