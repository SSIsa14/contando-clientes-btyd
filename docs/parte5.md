# Parte 5: Online Retail

Autor: Jorge Armando Ferguson Yaeggy. Uso de IA: implementación y documentación
asistidas por Codex (OpenAI).

## Reproducción

Desde la raíz, con el entorno del README activado:

```bash
python -m unittest discover -s tests
cd notebooks
python -m jupyter nbconvert --to notebook --execute --inplace 05_online_retail.ipynb
cd ..
python scripts/validar_retail.py
```

El original es `data/Online Retail.xlsx` (UCI 352, 541 909 líneas); su huella
SHA-256 se verifica antes y después del análisis (`data/online_retail_origen.json`).
`scripts/validar_retail.py` recalcula desde el Excel, con openpyxl y `Decimal`, los
netos diarios, la cohorte, los totales y las tablas, sin usar el código de `src/`.

## Preparación

1. `limpiar` de la Tarea 3 (copiada en `src/limpieza_retail.py`) quita duplicados
   exactos (5 268), facturas A (3), cantidades negativas sin cancelación (1 336),
   códigos que no son mercancía (2 259) y precios ≤ 0 (1 166). Quedan 531 877 líneas.
2. Se quedan las 400 190 líneas con `CustomerID`.
3. Venta neta por cliente-día = Σ Quantity × UnitPrice (las devoluciones restan).
   De 19 223 cliente-días, 16 562 tienen venta neta positiva y son transacciones.

Calibración hasta el 30 de junio de 2011; holdout del 1 de julio al 8 de diciembre
(23 semanas; el 9 de diciembre queda fuera). Semanas contadas desde el 1 de
diciembre de 2010. La cohorte son los 2 958 clientes con alguna transacción en
calibración (48 % con x = 0); los 1 374 que aparecen por primera vez en el holdout
no se pronostican.

## Resultados

| | r | α | a | b | LL |
|---|---:|---:|---:|---:|---:|
| BG/NBD | 0.740 | 9.16 | 4.5e-5 (cota) | ≈ 21 900 | −15 117.2 |

a/(a+b) ≈ 2e-9: el modelo se vuelve un NBD. b va de 146 a ≈ 22 000 según el
arranque con la misma verosimilitud y el mismo total pronosticado.

Holdout: pronóstico 5 492.9 contra 6 319 compras reales (−13.1 %). Noviembre tiene
54.8 compras por día contra 34.1 pronosticadas, y por sí solo explica ≈ 75 % del
error. Las respuestas a 5.1 y 5.2 están en el notebook.
