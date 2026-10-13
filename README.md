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
├── .devcontainer/
│   └── devcontainer.json      # Configuración para Codespaces y contenedores de VS Code
├── app.py                    # Capa de presentación (Streamlit + Plotly)
├── core/
│   ├── __init__.py           # Exportación del paquete matemático
│   ├── simulation.py         # Lógica pura de simulación y evaluación estadística
│   └── formatting.py         # Formateo de números para la interfaz
├── tests/
│   ├── __init__.py
│   ├── test_formatting.py    # Pruebas de formateo
│   └── test_simulation.py    # Suite de pruebas de simulación
├── pytest.ini                # Configuración de pytest (pythonpath y testpaths)
├── requirements.txt          # Dependencias del proyecto
├── CONSIGNA.md               # Requerimientos originales de la cátedra
├── GUION.md                  # Guion para la exposición oral
├── .streamlit/config.toml    # Tema y configuración visual de Streamlit
└── README.md                 # Documentación del proyecto
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

La barra lateral comienza colapsada y contiene la configuración de la moneda. Desde allí
se puede activar el modo de prueba y ajustar la probabilidad de obtener cara.

### Desarrollo con GitHub Codespaces

El repositorio incluye una configuración en `.devcontainer/devcontainer.json`.
Al abrirlo en GitHub Codespaces o VS Code Dev Containers, se instalan las dependencias
y la aplicación Streamlit se inicia automáticamente en el puerto `8501`.

---

## 🧪 Pruebas Unitarias

La suite de 21 pruebas valida la lógica matemática, el formateo de números, la consistencia
del historial acumulado, el margen dinámico y el manejo de excepciones:

```bash
pytest -v
```

Todas las pruebas deben estar en estado **PASSED**.

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

## 📋 Trazabilidad con la Consigna

| Requerimiento de la Consigna | Implementación en el Proyecto |
|---|---|
| Lanzamientos de 10, 100, 1.000 y 10.000 | Selector horizontal en pestaña *Simulador* y simulación simultánea en *Comparar cantidades*. |
| Cantidad de caras y cruces | Métricas destacadas (`st.metric`) en el resultado del experimento. |
| Frecuencia relativa de caras y cruces | Tabla comparativa formateada tiro a tiro y final. |
| Probabilidad teórica de cara y cruz | Columna dedicada en tabla comparativa ($0,5000$) y línea de referencia roja en gráficos. |
| Comparar con la probabilidad teórica | Columna *Diferencia* con signo, embudo en el gráfico y comparativa logarítmica. |
| ¿Es equilibrada? + justificación | Función `evaluate_fairness` con veredicto prioritario, explicación en lenguaje natural y margen $1/\sqrt{n}$. |
| Req. Común 1: Ingresar/modificar datos | Selector de tamaño de muestra y slider de sesgo en el sidebar. |
| Req. Común 2: Resultados claros e interpretados | Veredicto destacado al inicio, rótulo del experimento y advertencia ante bajo $n$. |
| Req. Común 3: Cálculos matemáticamente correctos | Módulo desacoplado `core/simulation.py` validado con 21 tests en `pytest`. |
| Req. Común 4: Conceptos de probabilidad integrados | Pestaña dedicada *Teoría* con definiciones, fórmulas LaTeX y límites del modelo. |
| Req. Común 5: Ejemplos de prueba | Modo interactivo de moneda trucada en el sidebar y suite de pruebas unitarias. |
| Req. Común 6: Preparación para exposición oral | Pestaña *Teoría* estructurada y guion guiado paso a paso en `GUION.md`. |
