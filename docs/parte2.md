# Reproducción de la Parte 2 de Jorge

El notebook `notebooks/02_ajuste_cdnow.ipynb` reconstruye CDNOW desde el archivo
original, ajusta el modelo manual compartido, contrasta con `lifetimes` y ejecuta
las 200 réplicas del bootstrap. No requiere ejecutar otros notebooks primero.
La revisión humana de estas adiciones asistidas por Codex (OpenAI) está pendiente.

## Entorno y ejecución

Entorno validado: Python 3.12.14; versiones exactas en `requirements-parte2.lock`.
Se mantienen las dependencias generales en `requirements.txt`; `openpyxl` permite
inspeccionar el Excel recuperado para la siguiente etapa. No se reemplaza el ajuste
manual con una biblioteca.

Desde la raíz del repositorio, con Python 3.12 disponible:

```bash
python3.12 -m venv .venv/env
.venv/env/bin/python -m pip install -r requirements-parte2.lock
source .venv/env/bin/activate
python -m unittest discover -s tests -v
cd notebooks
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1200 02_ajuste_cdnow.ipynb
cd ..
python scripts/validar_parte2.py
```

Alternativamente, abrir Jupyter desde el entorno, seleccionar Python 3 y usar
**Restart & Run All** con el directorio de trabajo `notebooks/`. Cada ejecución
recalcula las 200 réplicas y actualiza sus salidas y artefactos.

En el contenedor sin Python se usó `uv` para instalar el intérprete dentro del
directorio ignorado `.venv/runtime` y crear `.venv/env`; `/tmp` no permite ejecutar
binarios en ese entorno. La variante equivalente es:

```bash
UV_PYTHON_INSTALL_DIR="$PWD/.venv/runtime" uv venv --python 3.12 --seed .venv/env
uv pip install --python .venv/env/bin/python -r requirements-parte2.lock
```

Si el directorio personal no permite cachés, definir antes de ejecutar Jupyter:

```bash
export MPLCONFIGDIR="${TMPDIR:-/tmp}/btyd-mpl"
export IPYTHONDIR="${TMPDIR:-/tmp}/btyd-ipython"
export JUPYTER_CONFIG_DIR="${TMPDIR:-/tmp}/btyd-jupyter"
```

## Artefactos y validación efectuada

| Productor | Artefacto | Evidencia |
|---|---|---|
| Notebook, celda `p2-publicacion` | `resultados/params_cdnow.json` | Exactamente `r,alpha,a,b`, números finitos positivos; valores sin redondear |
| Misma celda | `resultados/ajuste_cdnow_proveniencia.json` | LL sumada, SHA-256 original/código, cortes, conteos, versiones y todos los intentos |
| Celda `p2-interpretacion` | `resultados/interpretacion_cdnow.json` | Tasas, abandono, asimetría Gamma y heterogeneidad Beta |
| Celdas `p2-densidades`, `p2-bootstrap-figura` | `figs/parte2_densidad_lambda.png`, `parte2_densidad_p.png`, `parte2_bootstrap_parametros.png` | Salidas reales del notebook; tres PNG inspeccionados visualmente |
| Celda `p2-bootstrap-ejecucion` | `resultados/bootstrap_cdnow.csv`, `bootstrap_cdnow_diagnosticos.json` | 200 muestras/400 intentos, aceptación, multiplicidad, SHA de índices, cotas, reintentos |
| Celda `p2-bootstrap-comparacion` | `resultados/bootstrap_cdnow_resumen.json` | Contabilidad completa, SE con `ddof=1`, arranque y comparación con evidencia guardada de Herman |
| `scripts/validar_parte2.py` | `resultados/validacion_parte2.json` | Consistencia entre JSON, CSV, diagnósticos, código, muestras y salidas del notebook |

Se ejecutaron las diez celdas de código en un kernel nuevo, incluyendo `B=200`, sin
errores. Las 13 pruebas focalizadas pasaron: invariantes, selección/rechazo,
recuperación de discrepancias, multiplicidad, reintentos sin redibujo, regresión
CDNOW, callback personalizado y ajuste/pronóstico MBG/NBD contra `lifetimes`.
No se ejecutaron los notebooks de Sofía o Gregorio ni las 80 simulaciones de Herman.

## Política y resultados

`ajustar_bgnbd(..., devolver_diagnostico=True)` devuelve `(estimados, diagnostico)`.
El comportamiento predeterminado sigue devolviendo solamente `r,alpha,a,b,ll`.
`loglik=...` conserva el callback de MBG/NBD. Los intentos registran método, arranque
logarítmico, éxito/estado/mensaje, objetivo recalculado y del optimizador, conteos
disponibles, cotas y selección. Fallo total o una mejora material no resuelta de un
intento rechazado genera `ErrorAjuste`, con diagnóstico accesible.

Se acepta convergencia finita dentro de las cotas; estar cerca de una cota produce
una advertencia y una marca separada. La discrepancia material se mide en `−LL/n`
con umbral `1e-7`, y activa una recuperación acotada con ambos métodos. Se informa
el rango de LL de los resultados exitosos; no se exige identidad de parámetros.

El ajuste completo tuvo seis intentos exitosos, sin cotas; el rango de LL fue
`2.2123437304344407e-08`. LL sumada: `-9582.429206673929`. Máxima diferencia absoluta
de parámetros contra `lifetimes`: `6.132840590922228e-07`; diferencia de LL:
`5.4569682106375694e-12`, evaluando ambas soluciones con nuestra LL y penalización
cero. Los parámetros completos están en el JSON, sin alterar `PARAMS_ARTICULO`.

Tasa activa semanal: `0.0549652002868947`; anualizada con 52 semanas:
`2.858190414918525`. Abandono medio por compra repetida: `0.2463386868642038`.
La Gamma tiene forma menor que uno y asimetría `4.060593334870111`; la Beta tiene
`a<1,b>1`, densidad concentrada hacia cero y heterogeneidad importante. El notebook
cuantifica esa heterogeneidad y distingue intensidad activa de compras tras abandono.

Bootstrap: 200 intentadas, 200 aceptadas, cero no resueltas, cero cotas y cero
reintentos. Muestreo `default_rng(14045)`; reintentos independientes con
`SeedSequence([271828, réplica])`. Cada muestra conserva 2,357 apariciones.

| Parámetro | SE bootstrap | DE simulación principal, guardada y redondeada |
|---|---:|---:|
| r | 0.014747792057017397 | 0.010 |
| alpha | 0.46259735778094657 | 0.326 |
| a | 0.19389502665465363 | 0.168 |
| b | 0.8007348085447493 | 0.671 |

Las SE empíricas son mayores en este caso; los diseños difieren en población,
parámetros y distribución de edades. La comparación usa la celda `f91acd6a` del
notebook 01, cuya evidencia se verifica y cuya huella se guarda. No hay resultados
existentes por réplica con precisión completa; las DE de tres decimales se identifican
como tales. Cualquier fallo futuro queda guardado y evita el estado completo.

Consulte [entrega_jorge.md](entrega_jorge.md) para el traspaso vigente. El usuario
reasignó a Gregorio toda la presentación y conserva con él el refresco de Parte 4;
Sofía conserva Parte 3 e integración final. Esas tareas no son implementación
faltante de Jorge. Las 200 réplicas no deben repetirse por este cambio documental.
