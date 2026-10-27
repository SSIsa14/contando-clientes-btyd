# Parte 2: ajuste a CDNOW, interpretación y bootstrap

Autor: Jorge Armando Ferguson Yaeggy. Uso de IA: notebook, extensión de diagnóstico
del ajuste y pruebas elaborados con apoyo de Codex (OpenAI).

`notebooks/02_ajuste_cdnow.ipynb` reconstruye CDNOW desde el archivo original, ajusta
el BG/NBD con `ajustar_bgnbd` (verosimilitud programada a mano), lo verifica contra
`lifetimes` y ejecuta las 200 réplicas del bootstrap. No necesita otros notebooks.

## Reproducción

Desde la raíz, con el entorno del README activado:

```bash
python -m unittest discover -s tests
cd notebooks
python -m jupyter nbconvert --to notebook --execute --inplace 02_ajuste_cdnow.ipynb
cd ..
python scripts/validar_parte2.py
```

`requirements-parte2.lock` guarda las versiones exactas con las que se validó
(Python 3.12). `scripts/validar_parte2.py` revisa que parámetros, diagnósticos,
bootstrap, figuras y salidas del notebook sean consistentes entre sí.

## Diagnóstico del optimizador

`ajustar_bgnbd(..., devolver_diagnostico=True)` devuelve `(estimados, diagnostico)`;
sin esa opción devuelve solo `r, alpha, a, b, ll`. Se aceptan intentos con
convergencia, objetivo finito y parámetros dentro de las cotas `[-10, 10]` en
logaritmos; estar en una cota se reporta aparte. Si un intento rechazado mejora el
objetivo en más de `1e-7` (en `−LL/n`), se reintenta desde ese punto con ambos métodos.

## Resultados

| | r | α | a | b | LL |
|---|---:|---:|---:|---:|---:|
| Ajuste propio | 0.2426 | 4.4136 | 0.7929 | 2.4259 | −9582.43 |
| Artículo | 0.243 | 4.414 | 0.793 | 2.426 | −9582.4 |

`lifetimes.BetaGeoFitter(penalizer_coef=0.0)` da los mismos parámetros (diferencias
del orden de 1e-6). Tasa de compra de un activo r/α ≈ 0.055 por semana (≈ 2.9 al año);
probabilidad media de morir tras una compra a/(a+b) ≈ 0.25.

Bootstrap: B = 200, `default_rng(14045)`, 2 357 clientes por muestra, 200 réplicas
aceptadas y ninguna en las cotas.

| Parámetro | SE bootstrap | DE simulación 1.3 (escenario principal) |
|---|---:|---:|
| r | 0.015 | 0.010 |
| α | 0.463 | 0.326 |
| a | 0.194 | 0.168 |
| b | 0.801 | 0.671 |

Los resultados completos están en `resultados/params_cdnow.json`,
`ajuste_cdnow_proveniencia.json`, `interpretacion_cdnow.json` y `bootstrap_cdnow*`.
