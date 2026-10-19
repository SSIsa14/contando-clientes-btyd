# Proyecto 2 – Contando clientes con modelos BTYD · Propuesta (Grupo 1)

**Integrantes:** Sofía Isabela Sandoval Vásquez · Herman Andrés Echeverría Rojas · Jorge Armando Ferguson Yaeggy · José Gregorio Coronel Colombo

## Quién se encarga de qué

**Sofía Sandoval** — Preparación de datos y pronóstico (incisos 0.1–0.4 y 3.1–3.4)
- Limpieza de CDNOW y construcción de (x, tx, T) en calibración y x\* en holdout.
- Pronóstico bottom-up de la cohorte con E[X(t)] y comparación contra la curva real.
- Pronóstico top-down con al menos tres métodos de series de tiempo y dos ventanas, y tabla comparativa (total, error % y MAE).
- Pronóstico por cliente con E[Y(τ)], agrupando por frecuencia de compra.
- Integración del repositorio de GitHub y README.

**Herman Echeverría** — Modelo, verosimilitud y simulación (incisos 1.1–1.3 y 6.1–6.5)
- Derivación de la verosimilitud individual (1.1) y de la mezcla gamma–beta (1.2).
- Programación de la log-verosimilitud y del estimador de máxima verosimilitud.
- Simulación de recuperación de parámetros con múltiples semillas (1.3).
- Parte 6 opcional: regresión logística contra el BG/NBD y análisis de fuga de información.

**Jorge Ferguson** — Ajuste a CDNOW y Online Retail (incisos 2.1–2.3 y 5.1–5.2)
- Estimación de (r, α, a, b) en CDNOW y comparación con el artículo original y con `lifetimes`.
- Interpretación de los parámetros y gráficas de las densidades de λ y p.
- Errores estándar por bootstrap sobre clientes (bono).
- Limpieza de Online Retail, ajuste del BG/NBD y comparación del pronóstico del holdout.
- Armado final de las diapositivas.

**Gregorio Coronel** — ¿Quién sigue vivo? (incisos 4.1–4.6)
- P(vivo) como clasificador: matriz de confusión, curva ROC, AUC y explicación del caso x = 0.
- Derivación de P(Z = 1) y verificación por simulación por deciles.
- Evaluación con AUC, calibración y Brier contra recencia, frecuencia y la tasa base.
- Ajuste del MBG/NBD y comparación con el BG/NBD.

A pesar de la división del trabajo, cada integrante estudiará el proyecto completo, incluida la derivación, para poder explicar y responder preguntas sobre cualquier sección.

## Cómo haremos la simulación de 1.3

- **Parámetros:** escenario principal r = 0.25, α = 4, a = 0.8, b = 2.5 (cercano a CDNOW). Escenario de control con clientes más activos y más propensos a morir: r = 0.6, α = 8, a = 1.4, b = 3.0.
- **Clientes:** 2 357 por réplica, con T ~ Uniforme(27, 39) semanas. Para cada cliente se sortea λ ~ Gamma(r, tasa α) y p ~ Beta(a, b); se generan compras con tiempos exponenciales hasta T, y después de cada compra repetida el cliente muere con probabilidad p.
- **Semillas (40):** 77785, 14045, 114526, 85967, 85603, 2452, 175326, 32532, 155374, 101914, 37119, 190629, 22054, 21663, 77709, 21226, 49984, 119397, 169546, 6120, 89947, 142369, 67446, 169504, 146915, 116397, 188834, 56560, 83788, 146255, 92419, 61219, 124227, 78090, 72131, 143951, 70942, 191266, 8258, 106699.
- **Estimación:** sobre log-parámetros, con Nelder–Mead y L-BFGS-B (cotas ±10), desde 3 puntos iniciales; se reporta la media y la desviación estándar de cada estimado.
- **Cómo sabremos que funcionó:** (1) el optimizador converge y los arranques coinciden, sin parámetros pegados a las cotas; (2) el sesgo relativo medio de cada parámetro es menor al 10 % y el valor verdadero cae dentro de media ± 2 DE; (3) la log-verosimilitud en el óptimo es mayor o igual que la evaluada en los parámetros verdaderos; (4) para una semilla, los estimados coinciden con los de `lifetimes`. Si falla alguno, no se pasa a CDNOW.
