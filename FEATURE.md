Agregá la posibilidad de ingresar una cantidad personalizada de lanzamientos.

1. En @core/simulation.py: definí MAX_FLIPS = 100_000 y hacé que run_simulation lance ValueError si n_flips está fuera de [1, MAX_FLIPS].
2. En @app.py: agregá la opción "Otra cantidad" al radio de cantidades; al elegirla, mostrá st.number_input (min 1, max MAX_FLIPS, valor inicial 500, paso 1, formato entero). Mantené que el experimento solo se ejecute al presionar "Lanzar moneda". Mostrá la cantidad con separador de miles en el rótulo del resultado.
3. En el gráfico: usá lines+markers cuando n ≤ 50.
4. Agregá los tests: n impar (777), n = 1, n = MAX_FLIPS + 1 (debe fallar con ValueError) y n = MAX_FLIPS.

No cambies el criterio de equidad ni el resto de la estructura. Al terminar, corré pytest y mostrame el resultado.
