# Parte 5 de Jorge: Online Retail ejecutado y reproducible

## Alcance y sustitución autorizada

El usuario autorizó expresamente sustituir el `limpiar` original no disponible por
una implementación de las reglas acordadas. `src/limpieza_retail.py` satisface esa
decisión: **no es una función recuperada de la tarea de series de tiempo**. La
proveniencia del ajuste registra la autorización y la ausencia del original. La
búsqueda histórica de Parte 2 no se repitió ni bloquea esta entrega.

Trabajo asistido por Codex (OpenAI), bajo la responsabilidad asignada a Jorge;
revisión humana pendiente. Se importan el resumen y pronóstico de Sofía y el
ajustador manual de Herman, sin cambiar sus interfaces o implementaciones.

## Reproducción

Se usa el entorno ya validado de Parte 2, sin dependencias nuevas. Desde la raíz:

```bash
source .venv/env/bin/activate
python -m unittest discover -s tests -v
cd notebooks
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1200 05_online_retail.ipynb
cd ..
python scripts/validar_retail.py
python scripts/validar_parte2.py
```

También puede abrirse el notebook desde `notebooks/`, seleccionar el entorno y
usar **Restart & Run All**. No requiere ejecutar otros notebooks ni cargar una
caché. La configuración de cachés y creación del entorno está en `docs/parte2.md`.
La auditoría de Parte 2 no vuelve a ajustar sus 200 réplicas.

Original: `data/Online Retail.xlsx`, UCI 352, adquirido mediante
`scripts/obtener_retail.py`; detalle en `data/online_retail_origen.json`.
Se verifica antes y después del análisis:

```text
43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d
```

El original de 541,909 líneas conserva sus ocho columnas y no se modifica.

## Reglas exactas y auditoría

- Se validan InvoiceNo, CustomerID, InvoiceDate, Quantity y UnitPrice. Las fechas
  inválidas y los números requeridos ausentes/no finitos generan error explícito.
- CustomerID entero se representa como texto decimal canónico. Solo las líneas
  sin CustomerID se excluyen; Description/Country no determinan exclusiones.
- Se normalizan fechas locales al día antes de cortes y agrupación.
- Se conserva Quantity×UnitPrice con signo: ninguna devolución, cancelación,
  cantidad negativa o precio no positivo se filtra antes de sumar.
- No se filtra por país, frecuencia o outliers ni se deduplican líneas idénticas.
- Se obtiene exactamente un día por cliente y se conserva como transacción solo
  si su venta neta es estrictamente positiva.

UnitPrice tiene uno, dos y tres decimales (31,273; 510,632; 4 líneas, respectivamente).
Quantity es entera en el archivo. Se convierte `Decimal(str(valor))` a enteros de
escala 1,000; el producto y la suma son enteros exactos. No se redondea a centavos ni
se usa epsilon. La prueba 0.1+0.2−0.3 verifica cero exacto y otra preserva una venta
positiva de 1e-12. El validador independiente usa sumas Decimal desde openpyxl.

| Propiedad (todo el archivo, antes de cortes) | Conteo |
|---|---:|
| Líneas originales / con ID / sin ID | 541,909 / 406,829 / 135,080 |
| Facturas únicas originales / con ID | 25,900 / 22,190 |
| Líneas duplicadas exactas, conservadas | 5,268 |
| Líneas Quantity negativa originales / conservadas con ID | 10,624 / 8,905 |
| Líneas de cancelación originales / conservadas con ID | 9,288 / 8,905 |
| Cliente-días identificados | 19,296 |
| Días netos cero / negativos, excluidos después de sumar | 65 / 2,623 |
| Días positivos / clientes con algún día positivo | 16,608 / 4,334 |
| Días positivos que incluyen importes negativos | 803 |

Los conteos de cancelaciones/devoluciones son **líneas**, no facturas únicas.
No hubo fechas o números requeridos inválidos. La normalización de horas conserva
transacciones tardías del 30 junio y 8 diciembre. El 9 diciembre contiene 1,632
líneas originales y 34 días positivos: se auditan, pero no entran en el análisis.

## Cohorte y resumen compartido

`historias_retail` adapta `resumen_clientes`, sin reimplementarlo. Origen:
01/12/2010; calibración hasta 30/06/2011 inclusive; holdout 01/07–08/12/2011;
horizonte `(08/12−30/06).days/7 = 23` semanas. La adquisición es el primer día
positivo observado. Tener devoluciones en calibración no basta para integrar la
cohorte. Los clientes nuevos del holdout se excluyen de predicciones y observaciones.

| Propiedad | Resultado |
|---|---:|
| Clientes de calibración | 2,959 |
| x=0 | 1,417 (47.8878%) |
| Días positivos de calibración / repeticiones | 7,894 / 4,935 |
| x mínimo / máximo | 0 / 58 |
| tx y T, rango en semanas | 0–30.142857142857142 |
| Clientes de calibración sin compras futuras, conservados | 974 |
| Compras observadas del holdout de la cohorte | 6,341 |
| Clientes nuevos del holdout / compras excluidas | 1,374 / 2,339 |

La adquisición cubre 01/12/2010–30/06/2011. `retail_frecuencias.csv` guarda la
distribución completa de x; `retail_clientes.csv` contiene historias y pronóstico
condicional por cliente. Fechas, enteros, finitud, cohortes y ceros se verificaron.

## Ajuste e identificación

Tres arranques naturales: (1,10,.1,1), (.5,5,.01,1) y (1,1,1,1), pasados a logaritmos.
Ambos métodos y las cotas ±10 son los del ajustador compartido. Los seis intentos
convergieron; se seleccionó el intento 4 (Nelder–Mead, tercer arranque).

```text
r     = 0.7400738332312865
alpha = 9.144550405767946
a     = 0.000045400369297551414
b     = 22019.841245856747
LL    = -15144.80192003734 (sumada)
```

a y b están cerca de sus cotas inferior y superior. No se presenta este resultado
como un máximo interior ni como identificación fuerte. El rango de LL exitosas es
0.00033760108431568625: el criterio estricto de acuerdo del ajustador es **False**,
aunque la variación práctica es pequeña. `retail_sensibilidad.csv` conserva todos
los candidatos: b varía aproximadamente 161.74–22,019.84 y el pronóstico solo
5,507.7998–5,507.9293. No se alteraron cotas, cohortes o parámetros para obtener NBD.

La media activa es aproximadamente 0.08093 compras/semana y el abandono medio es
aproximadamente 2.06e-9 por repetición. Es un ajuste próximo al límite sin abandono,
no prueba de abandono realmente nulo. La ventana corta, exposición desigual y
muchas historias sin repetición limitan su identificación. La fuente UCI describe
presencia de mayoristas, contexto plausible; no se identifican clientes individuales
como mayoristas ni se infieren muertes observadas a partir de a/b.

## Pronóstico, verificación y noviembre

`esperado_Y(23,...)` se aplica a exactamente la cohorte anterior. Todos los valores
son finitos/no negativos; se comprobaron cero y monotonía por cliente en los 162
extremos diarios. Los intervalos semanales son 01–07 julio hasta 02–08 diciembre,
23 bloques de siete días; sus incrementos provienen de diferencias acumuladas.

| Métrica | Resultado |
|---|---:|
| Pronóstico total | 5507.890886578898 |
| Observado | 6341 |
| Error firmado = pronóstico − observado | −833.1091134211019 |
| Error absoluto | 833.1091134211019 |
| Error porcentual = 100×error/observado | −13.138449982985364% |

`lifetimes` verifica al **mismo vector**, sin ajuste independiente y con
`penalizer_coef=0.0`; la diferencia máxima por cliente a 23 semanas es
2.304076929249277e-10. Se comprobaron además límites analíticos mediante los
momentos posteriores Gamma/Beta, con tolerancia 1e-7 por cliente (relativa cuando
la cota supera uno). El mayor exceso numérico sobre la cota superior exacta es
2.798455134289668e-8 compras/cliente, dentro de la tolerancia documentada; no se
recortó ningún valor. No se necesitó modificar la fórmula compartida.

| Mes observado | Días | Compras reales | Reales por día |
|---|---:|---:|---:|
| Julio | 31 | 989 | 31.9032 |
| Agosto | 31 | 966 | 31.1613 |
| Septiembre | 30 | 1163 | 38.7667 |
| Octubre | 31 | 1115 | 35.9677 |
| Noviembre | 30 | 1645 | 54.8333 |
| Diciembre parcial | 8 | 463 | 57.8750 |

El modelo predice aproximadamente 34.2105 compras/día. Noviembre aumenta 52.4514%
frente a octubre tras ajustar por días. Su total es el mayor, pero diciembre parcial
tiene mayor tasa diaria. Es compatible con demanda de fin de año; una sola ventana
no establece causalidad ni atribuye todo el error a estacionalidad. El modelo
estacionario no incorpora un calendario estacional/promocional. No se invocan
hallazgos de la tarea previa no recuperada.

## Artefactos y checks ejecutados

- Notebook 05: diez celdas de código ejecutadas desde kernel nuevo, sin errores
  finales. Se corrigió una referencia ambigua a la columna T y se repitió completo.
- 22 pruebas aprobadas: 13 previas y 9 nuevas; incluye netos, precisión, duplicados,
  IDs ausentes, cortes con hora, cohortes, ceros y tablas calendario.
- `scripts/validar_retail.py` reconcilió independientemente los 19,296 netos diarios,
  las 2,959 historias, los conteos y errores, y todas las sumas de las tablas.
- Original verificado de nuevo; Parte 2 auditada sin repetir bootstrap. Fuente
  compartida, notebook 02, resultados/figuras de Parte 2 y datasets preservados.
- Cuatro figuras `figs/parte5_*.png` inspeccionadas visualmente.

| Artefacto | Contenido |
|---|---|
| `params_retail.json` | Solo r,alpha,a,b; no modifica params_cdnow.json |
| `retail_limpieza_auditoria.json` | Reglas, precisión, líneas/facturas, netos y ventanas |
| `ajuste_retail_proveniencia.json` | Datos, autorización, código/versiones, intentos y huellas de resultados |
| `retail_holdout.json` | Cohorte, horizonte, totales, errores, noviembre y verificación |
| `retail_dias.csv` | Todos los días neteados, incluso cero/negativos y 9 diciembre |
| `retail_clientes.csv`, `retail_frecuencias.csv` | Historias/predicción y distribución x |
| `retail_sensibilidad.csv` | Parámetros, LL, abandono y pronóstico por intento exitoso |
| `retail_diario.csv`, `retail_semanal.csv`, `retail_mensual.csv` | Comparaciones reconciliadas y tasas por duración |
| `validacion_retail.json` | Resultado del oráculo independiente y huella del notebook ejecutado |

El usuario reasignó presentación, plantilla, Google Slides, montaje grupal y PDF
a Gregorio; también conserva con él el refresco de 04. Sofía conserva 03 e
integración final. La Parte 5 de Jorge está terminada computacionalmente y su
traspaso está en [entrega_jorge.md](entrega_jorge.md); la revisión humana queda pendiente.
