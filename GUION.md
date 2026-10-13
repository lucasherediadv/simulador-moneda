# 🎤 Guion Para la Exposición Oral (3 a 5 min)

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
