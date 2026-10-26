# Contando clientes con modelos Buy 'Til You Die

Proyecto 2 de Análisis y Ciencia de Datos (Universidad del Istmo). Implementación desde cero del modelo **BG/NBD** (Fader, Hardie y Lee, 2005) sobre los datos de CDNOW.

**Integrantes:** Sofía Isabela Sandoval Vásquez · Herman Andrés Echeverría Rojas · Jorge Armando Ferguson Yaeggy · José Gregorio Coronel Colombo

## Estructura

```
data/
  CDNOW_sample.txt             datos originales (Bruce Hardie)
src/
  datos.py                     carga de CDNOW y resumen por cliente (x, tx, T, x*)
  bgnbd.py                     verosimilitud y ajuste, E[X(t)], E[Y(τ)], P(vivo) y P(Z = 1) del BG/NBD
  mbgnbd.py                    verosimilitud, ajuste, P(vivo), P(Z = 1), E[X(t)] y E[Y(τ)] del MBG/NBD
  simulacion.py                simulador de clientes BG/NBD
notebooks/
  00_preparacion.ipynb         Parte 0: preparación de los datos
  03_pronostico.ipynb          Parte 3: pronóstico bottom-up vs. top-down
  04_quien_sigue_vivo.ipynb    Parte 4: P(vivo), P(Z = 1) y MBG/NBD
figs/                          figuras generadas por los notebooks
```

## Cómo correrlo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

Ejecutar `00_preparacion`, `03_pronostico` y `04_quien_sigue_vivo`. Los notebooks `03` y `04` toman los parámetros de `resultados/params_cdnow.json`; si ese archivo todavía no existe, usa los reportados en el artículo original.

La Parte 2 de Jorge está en `notebooks/02_ajuste_cdnow.ipynb`: ajuste manual,
interpretación y bootstrap de 200 remuestras de clientes. Entorno y reproducción:
[docs/parte2.md](docs/parte2.md). Este notebook publica los parámetros ajustados;
el refresco de las Partes 3/4 queda pendiente de integración. Alcance restante y
entradas recuperadas: [docs/entrega_jorge.md](docs/entrega_jorge.md).

La Parte 5 está ejecutada en `notebooks/05_online_retail.ipynb`; reproducción:
[docs/parte5.md](docs/parte5.md). Las Partes 2 y 5 son independientes y usan el
entorno validado Python 3.12.14 de `requirements-parte2.lock`. Por reasignación
explícita del usuario, Gregorio se encarga de toda la presentación y del refresco
de Parte 4; Sofía conserva Parte 3 e integración final. La propuesta original se
mantiene como registro histórico. La entrega de Jorge no declara completo al grupo.

## Notas

- `lifetimes` se usa únicamente para verificar resultados.
- Se utilizó Claude (Anthropic) como herramienta de apoyo; el detalle se declara al inicio de cada archivo.
