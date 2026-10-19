# Contando clientes con modelos Buy 'Til You Die

Proyecto 2 de Análisis y Ciencia de Datos (Universidad del Istmo). Implementación desde cero del modelo **BG/NBD** (Fader, Hardie y Lee, 2005) sobre los datos de CDNOW.

**Integrantes:** Sofía Isabela Sandoval Vásquez · Herman Andrés Echeverría Rojas · Jorge Armando Ferguson Yaeggy · José Gregorio Coronel Colombo

## Estructura

```
data/
  CDNOW_sample.txt             datos originales (Bruce Hardie)
src/
  datos.py                     carga de CDNOW y resumen por cliente (x, tx, T, x*)
  bgnbd.py                     E[X(t)] y E[Y(τ)] del BG/NBD
notebooks/
  00_preparacion.ipynb         Parte 0: preparación de los datos
  03_pronostico.ipynb          Parte 3: pronóstico bottom-up vs. top-down
figs/                          figuras generadas por los notebooks
```

## Cómo correrlo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

Ejecutar `00_preparacion` y luego `03_pronostico`. El notebook `03` toma los parámetros de `resultados/params_cdnow.json`; si ese archivo todavía no existe, usa los reportados en el artículo original.

## Notas

- `lifetimes` se usa únicamente para verificar resultados.
- Se utilizó Claude (Anthropic) como herramienta de apoyo; el detalle se declara al inicio de cada archivo.
