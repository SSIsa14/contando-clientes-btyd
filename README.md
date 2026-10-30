# Contando clientes con modelos Buy 'Til You Die

Proyecto 2 de Análisis y Ciencia de Datos (Universidad del Istmo). Implementación desde cero del modelo **BG/NBD** (Fader, Hardie y Lee, 2005) sobre los datos de CDNOW: derivación y estimación por máxima verosimilitud, pronóstico de compras, probabilidad de que un cliente siga activo, comparación con el MBG/NBD y aplicación a Online Retail.

**Integrantes:** Sofía Isabela Sandoval Vásquez · Herman Andrés Echeverría Rojas · Jorge Armando Ferguson Yaeggy · José Gregorio Coronel Colombo

**Diapositivas:** [`slides/presentacion Final.pdf`](slides/presentacion%20Final.pdf)

## Quién hizo qué

| Integrante | Partes |
|---|---|
| Sofía Sandoval | Parte 0 (preparación de datos), Parte 3 (pronóstico bottom-up vs. top-down), integración del repositorio |
| Herman Echeverría | Parte 1 (derivación, verosimilitud, ajuste y simulación), Parte 6 (logística vs. BG/NBD) |
| Jorge Ferguson | Parte 2 (ajuste a CDNOW, interpretación y bootstrap), Parte 5 (Online Retail) |
| José Gregorio Coronel | Parte 4 (¿quién sigue vivo?, P(Z = 1) y MBG/NBD) |

## Estructura

```
data/
  CDNOW_sample.txt             datos de CDNOW (Bruce Hardie)
  Online Retail.xlsx           datos de Online Retail (UCI)
src/
  datos.py                     carga de CDNOW y resumen por cliente (x, tx, T, x*)
  bgnbd.py                     verosimilitud y ajuste, E[X(t)], E[Y(τ)], P(vivo) y P(Z = 1) del BG/NBD
  mbgnbd.py                    verosimilitud, ajuste y pronóstico del MBG/NBD
  simulacion.py                simulador de clientes BG/NBD
  bootstrap_cdnow.py           bootstrap sobre clientes
  limpieza_retail.py           limpiar (de la tarea de series de tiempo) y venta neta por cliente-día
  pronostico_retail.py         historias y pronóstico de Online Retail
notebooks/
  00_preparacion.ipynb         Parte 0: preparación de los datos
  01_modelo_y_simulacion.ipynb Parte 1: verosimilitud y simulación de recuperación
  02_ajuste_cdnow.ipynb        Parte 2: ajuste a CDNOW, interpretación y bootstrap
  03_pronostico.ipynb          Parte 3: pronóstico bottom-up vs. top-down
  04_quien_sigue_vivo.ipynb    Parte 4: P(vivo), P(Z = 1) y MBG/NBD
  05_online_retail.ipynb       Parte 5: Online Retail
  06_logistica.ipynb           Parte 6 (opcional): regresión logística vs. BG/NBD
resultados/                    parámetros estimados y tablas generadas
figs/                          figuras generadas por los notebooks
slides/                        diapositivas de la presentación (PDF)
docs/                          detalles de reproducción de las Partes 2 y 5
scripts/, tests/               descarga del Excel original, validaciones y pruebas automáticas
```

## Cómo correrlo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

Ejecutar los notebooks en orden, de `00` a `06`, desde la carpeta `notebooks/`. Todos parten de los archivos originales de `data/`. El notebook `02` estima los parámetros de CDNOW y los guarda en `resultados/params_cdnow.json`, archivo que leen los notebooks `01`, `03`, `04` y `06`; el repositorio ya lo incluye, por lo que el orden anterior funciona desde un clon nuevo. Los notebooks `01`, `02` y `05` tardan algunos minutos (simulación, bootstrap y carga del Excel).

Pruebas y validaciones, desde la raíz:

```bash
python -m unittest discover -s tests
python scripts/validar_parte2.py
python scripts/validar_retail.py
```

Las versiones exactas con las que se validaron las Partes 2 y 5 están en `requirements-parte2.lock`; los pasos de reproducción y validación de esas partes están en [docs/parte2.md](docs/parte2.md) y [docs/parte5.md](docs/parte5.md).

## Notas

- La verosimilitud se programa a mano con `scipy`; `lifetimes` se usa únicamente para verificar resultados.
- Se utilizaron herramientas de IA como apoyo; el detalle se declara al inicio de cada archivo.
