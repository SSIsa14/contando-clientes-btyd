# Entrega de Jorge: implementación validada y traspaso

## Alcance vigente y cambio de asignación

**La implementación y el traspaso del alcance actual de Jorge están listos: Partes
2.1, 2.2, las 200 réplicas de 2.3 y Parte 5 completa, con artefactos y reproducción.**
La revisión científica humana sigue pendiente. Las comprobaciones automáticas y
la aprobación eventual de un título de commit no constituyen esa revisión.

La [propuesta original](../Propuesta_Grupo1.md) se conserva intacta como documento
histórico: asignaba a Jorge el montaje final de diapositivas. **El usuario reasignó
posteriormente a Gregorio toda la presentación:** creación, plantilla compartida,
Google Slides, ensamblaje grupal y PDF final. Esas tareas no son implementación
faltante de Jorge y no se han realizado ni aprobado por Gregorio en esta entrega.

Gregorio conserva el refresco/revisión de Parte 4. Sofía conserva el refresco de
Parte 3 y la integración final del grupo. La entrega individual de Jorge no declara
terminado el proyecto grupal. No se contactó a los compañeros, no se creó una
presentación ni se modificaron/ejecutaron sus notebooks o figuras.

Trabajo asistido por Codex (OpenAI); se preservan las atribuciones originales de
Sofía, Herman y Gregorio. Los notebooks ejecutados conservan sus textos históricos
de alcance; esta asignación vigente sustituye las menciones anteriores a diapositivas
de Jorge sin alterar sus celdas, salidas ni huellas de ejecución.

## Lista de requisito → artefacto → validación → responsable

| Requisito | Estado del alcance vigente | Evidencia o siguiente responsable |
|---|---|---|
| 2.1: historias y ajuste manual CDNOW | Completo, Jorge | [Notebook 02](../notebooks/02_ajuste_cdnow.ipynb), `p2-historias` y `p2-ajuste`; 2357 clientes, 1411 con x=0, 2457 repeticiones y 1882 compras de holdout |
| 2.1: tabla lifetimes, parámetros y LL sumada | Completo, Jorge | `p2-lifetimes`; comparación sin penalización y misma LL; [proveniencia](../resultados/ajuste_cdnow_proveniencia.json) |
| 2.1: cuatro parámetros oficiales | Completo, Jorge | [params_cdnow.json](../resultados/params_cdnow.json); exactamente r,alpha,a,b, sin redondear ni metadatos |
| 2.2: tasas, abandono y formas Gamma/Beta | Completo, Jorge | `p2-interpretacion`, [interpretación](../resultados/interpretacion_cdnow.json), dos densidades `parte2_*` |
| 2.3: 200 remuestras, semilla 14045 y multiplicidad | Completo, Jorge | [CSV](../resultados/bootstrap_cdnow.csv), [diagnósticos](../resultados/bootstrap_cdnow_diagnosticos.json), [resumen](../resultados/bootstrap_cdnow_resumen.json); 200 aceptadas/0 no resueltas |
| 2.3: SE y comparación con Herman | Completo, Jorge | DE con ddof=1; referencia guardada y redondeada de 40 simulaciones, celda `f91acd6a` de notebook 01 |
| Original Retail y proveniencia | Completo, Jorge | [Excel original](../data/Online%20Retail.xlsx), [registro de adquisición](../data/online_retail_origen.json), huella verificada |
| Limpiador por sustitución expresamente autorizada | Satisfecho, Jorge | [limpieza_retail.py](../src/limpieza_retail.py); no es original recuperado; autorización en [proveniencia Retail](../resultados/ajuste_retail_proveniencia.json) |
| Retail: netos, historias, cohorte y límites | Completo, Jorge | [Notebook 05](../notebooks/05_online_retail.ipynb); 19,296 netos diarios y 2,959 historias reconciliados independientemente |
| 5.1: ajuste, convergencia, cotas y sensibilidad | Completo, Jorge | `p5-ajuste`/`p5-sensibilidad`, [tabla de sensibilidad](../resultados/retail_sensibilidad.csv); débil identificación explícita |
| 5.2: esperado_Y, error y noviembre | Completo, Jorge | [retail_holdout.json](../resultados/retail_holdout.json), tablas diario/semanal/mensual y cuatro figuras |
| Reproducción y evidencia individual | Completo, Jorge | [Parte 2](parte2.md), [Parte 5](parte5.md), ambos notebooks ejecutados y [auditorías](#comprobaciones-de-entrega) |
| Presentación, plantilla, Google Slides y PDF | Reasignado a Gregorio; pendiente de él | Decisión explícita del usuario; no se afirma existencia, aprobación o entrega de diapositivas |
| Refresco y revisión de Parte 4 | Pendiente, Gregorio | Instrucciones y salidas concretas abajo; no es trabajo faltante de Jorge |
| Refresco de Parte 3 e integración final | Pendiente, Sofía | Instrucciones y comprobaciones abajo; no es trabajo faltante de Jorge |

## Resumen científico desde los artefactos guardados

### CDNOW y bootstrap

Los parámetros oficiales usan calibración hasta 30/09/1997 y holdout
01/10/1997–30/06/1998; unidades: semanas.

| Parámetro | Ajuste manual publicado | SE bootstrap | DE principal de Herman, redondeada |
|---|---:|---:|---:|
| r | 0.2425945256794309 | 0.014747792057017397 | 0.010 |
| alpha | 4.41360214123103 | 0.46259735778094657 | 0.326 |
| a | 0.7929219296911957 | 0.19389502665465363 | 0.168 |
| b | 2.4259063420057316 | 0.8007348085447493 | 0.671 |

LL sumada: **−9582.429206673929**. Seis intentos exitosos, sin cotas; rango de LL
2.2123437304344407e-8. `BetaGeoFitter(penalizer_coef=0.0)` se ajustó sobre los mismos
vectores exactos. Máxima diferencia de parámetros: 6.132840590922228e-7; diferencia
de LL evaluada con nuestra función para ambos vectores: 5.4569682106375694e-12.

Intensidad activa media: 0.054965200286894715 compras/semana y 2.858190414918525
por 52 semanas activas. Abandono medio por compra repetida: 0.2463386868642038.
La Gamma con r<1 concentra masa cerca de cero y tiene cola derecha
(asimetría 4.060593334870111). La Beta a<1,b>1 concentra propensiones bajas con
heterogeneidad: DE 0.2097773034383295; aproximadamente 31.77% tiene p<0.1 y 14.05%
p>0.5. Son características latentes del modelo, no etiquetas observadas.

Bootstrap: **B=200**, `default_rng(14045)`, 2357 apariciones por muestra,
arranque logarítmico del ajuste completo. Las 200 réplicas fueron aceptadas,
sin fallos, cotas o reintentos; sus 400 intentos de optimización fueron utilizables.
Se guardan hashes de índices y diagnósticos, y las SE usan `ddof=1`.

La comparación de Herman usa 40 muestras bajo r=.25, alpha=4, a=.8, b=2.5 y
T~Uniforme(27,39). Solo hay DE guardadas con tres decimales; no se inventa precisión
ni se repiten ambas simulaciones para reemplazarlas. El bootstrap empírico y la
simulación paramétrica describen variabilidad del mismo estimador bajo poblaciones
y diseños distintos, por lo que no se espera igualdad exacta.

### Retail

Una transacción es **un cliente-día con Quantity×UnitPrice neto estrictamente
positivo**, después de incluir devoluciones y cancelaciones. El reemplazo aprobado
valida entradas, conserva duplicados y usa escala decimal exacta sin epsilon ni
redondeo a centavos. La función original nunca fue recuperada; esa ausencia ya no
bloquea el requisito aprobado.

Se conservan 406,829 líneas identificadas de 541,909; 135,080 sin ID se excluyen.
Hay 19,296 días identificados: 65 netos cero, 2623 negativos y 16,608 positivos
en todo el archivo. Las 5268 líneas duplicadas exactas se conservan. El registro
distingue líneas de facturas únicas y documenta las reglas.

Calibración: desde el comienzo disponible hasta **30/06/2011 inclusive**. Holdout:
**01/07–08/12/2011 inclusive**; el 09/12 se conserva en el original y se excluye
del análisis. Origen Retail: 01/12/2010. Horizonte: **161/7=23 semanas**.
La adquisición operativa es el primer día calificante observado, sin afirmar que
sea la primera compra histórica real del cliente.

Cohorte: **2959 clientes**, 1417 con x=0, 4935 repeticiones de calibración;
974 clientes sin compras futuras se conservan. Los 1374 clientes solo calificantes
en holdout y sus 2339 compras se excluyen de ambos lados de la comparación.

| Parámetro | Ajuste Retail |
|---|---:|
| r | 0.7400738332312865 |
| alpha | 9.144550405767946 |
| a | 0.000045400369297551414 |
| b | 22019.841245856747 |

LL sumada: **−15144.80192003734**. Los seis intentos convergieron, pero a/b están
cerca de las cotas. El rango de LL es 0.00033760108431568625 y el acuerdo estricto
del ajustador es **False**. b cambia de 161.7421471305383 a 22019.841245856747
entre soluciones exitosas, mientras el total previsto varía solo de
5507.799801891573 a 5507.92930821692. Es identificación débil con pronóstico
estable en estos arranques, no evidencia de un máximo interior o abandono real nulo.

La intensidad activa media es 0.08093058711388186/semana; el abandono medio ajustado
es 2.0617936658597735e-9 por repetición. La corta exposición y la presencia descrita
de mayoristas son contexto plausible, sin clasificar individuos ni observar muertes.

`sum(esperado_Y(23,...))`: **5507.890886578898** frente a **6341** compras observadas
de la misma cohorte. Error definido como pronóstico menos observado:
**−833.1091134211019**, absoluto 833.1091134211019, porcentaje
**−13.138449982985364%**. No se ajustó un segundo modelo con lifetimes: se verificó
la predicción al mismo vector (diferencia máxima por cliente 2.304076929249277e-10).
También se comprobaron límites analíticos con tolerancia numérica documentada;
no se recortaron predicciones ni se cambió el pronóstico compartido.

Noviembre: 1645 compras en 30 días, 54.833333333333336/día, frente a
35.96774193548387/día en octubre: aumento de **52.4514%** al normalizar duración.
Diciembre solo cubre ocho días y tiene 57.875/día. El modelo estacionario prevé
aproximadamente 34.2105/día. Una sola ventana no demuestra causalidad estacional
ni explica por sí sola todo el error; no se invocan resultados de la tarea anterior.

### Distinciones que deben conservarse en métricas y presentación

- `P(vivo)` es supervivencia latente, no probabilidad de comprar durante un holdout.
  Un cliente activo puede no comprar; la supervivencia no se observa directamente.
- `P(compra en tau)` es una probabilidad de al menos una compra; `E[Y(tau)]` es un
  número esperado de compras y puede superar uno.
- `r/alpha` es intensidad mientras se está activo; anualizar con 52 semanas no
  elimina el efecto del abandono sobre compras realizadas.
- `a/(a+b)` es abandono medio por compra repetida, no churn anual.
- El bottom-up incondicional suma `E[X(t)]` según edad desde adquisición y puede
  formar incrementos entre extremos del holdout. `E[Y(tau)|x,tx,T]` condiciona en
  historias de calibración. Son cantidades con condicionamientos distintos:
  **no se fuerzan sus totales a coincidir ni se etiquetan indistintamente**.

## Para Gregorio: Parte 4 y presentación reasignada

### Parámetro oficial y comprobación

Consumir [resultados/params_cdnow.json](../resultados/params_cdnow.json), no una
copia de la semilla del artículo. Esquema exacto: `{"r": número, "alpha": número,
"a": número, "b": número}`, cuatro valores positivos finitos. LL y metadatos están
separados en [ajuste_cdnow_proveniencia.json](../resultados/ajuste_cdnow_proveniencia.json).

Evidencia: notebook 02, `p2-lifetimes`; [validacion_parte2.json](../resultados/validacion_parte2.json);
`tests/test_ajuste.py` para compatibilidad BG/MBG, incluido el callback del ajustador.
La interfaz predeterminada sigue devolviendo r,alpha,a,b,ll; el diagnóstico es optativo.

### Qué sigue reflejando parámetros anteriores

En [notebook 04](../notebooks/04_quien_sigue_vivo.ipynb), celda `7367f83f`, la salida
guardada carga r=.243, alpha=4.414, a=.793, b=2.426. Refrescar bajo su responsabilidad:

- P(vivo), P(compra), clasificación, ROC/AUC, Brier y calibración por deciles.
- Simulación de verificación con los parámetros cargados.
- Comparaciones BG/MBG, totales condicionales e incondicionales y texto numérico.
- `figs/parte4_roc_p_vivo.png`, `parte4_calibracion_simulada.png`,
  `parte4_roc_comparacion.png`, `parte4_calibracion_real.png`,
  `parte4_bgnbd_vs_mbgnbd.png`.

El ajuste MBG usa sus propias historias, no el JSON BG; la comparación con BG sí
depende del JSON. Refrescar/revisar no presupone que cada métrica cambie de redondeo.

Entorno: Python **3.12.14**, versiones en [requirements-parte2.lock](../requirements-parte2.lock);
configuración en [parte2.md](parte2.md). Comandos **para Gregorio después del traspaso**,
desde la raíz, con el entorno existente:

```bash
source .venv/env/bin/activate
python scripts/validar_parte2.py
cd notebooks
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1200 04_quien_sigue_vivo.ipynb
```

Antes de usar salidas finales: confirmar los cuatro parámetros en la primera celda,
revisar comparaciones internas, finitud, fechas, tablas, figuras, prosa y conclusiones.
La ejecución de 04 y esa revisión **no se realizaron en la finalización de Jorge**.

### Material terminado que puede incorporar a la presentación

- [Notebook 02](../notebooks/02_ajuste_cdnow.ipynb): fit, comparación, tasas,
  heterogeneidad y bootstrap; [resumen bootstrap](../resultados/bootstrap_cdnow_resumen.json).
- Figuras `parte2_densidad_lambda.png`, `parte2_densidad_p.png` y
  `parte2_bootstrap_parametros.png` en `figs/`.
- [Notebook 05](../notebooks/05_online_retail.ipynb): definición de transacción,
  cohorte, ajuste acotado, sensibilidad, pronóstico, noviembre y mensajes en español.
- Figuras `parte5_historias.png`, `parte5_holdout_acumulado.png`,
  `parte5_holdout_semanal.png`, `parte5_meses_por_dia.png` en `figs/`.
- [Resultados Retail](../resultados/retail_holdout.json), [proveniencia](../resultados/ajuste_retail_proveniencia.json)
  y [limitaciones/reproducción](parte5.md).

Gregorio recibe la responsabilidad de crear/recuperar plantilla, Google Slides,
ensamblar secciones y exportar el PDF. No se afirma que ya haya entregado o revisado
diapositivas. Referencia comunicada del grupo: 20–25 minutos más ocho de preguntas;
unos seis minutos para exponer los resultados CDNOW/Retail de Jorge. No se generan
aquí diapositivas, enlaces, archivos de presentación ni sistemas de exportación.

## Para Sofía: Parte 3 e integración del grupo

### Entrada y reproducción individual

Los artefactos oficiales están en `resultados/`, las figuras terminadas de Jorge
en `figs/parte2_*.png` y `figs/parte5_*.png`, los notebooks en `notebooks/02_ajuste_cdnow.ipynb`
y `notebooks/05_online_retail.ipynb`. Los originales están en `data/`; adquisición y
huellas Retail están documentadas en [online_retail_origen.json](../data/online_retail_origen.json).

Comprobaciones de artefactos, desde la raíz y sin volver a ajustar:

```bash
source .venv/env/bin/activate
python scripts/validar_parte2.py
python scripts/validar_retail.py
```

Reproducción completa individual: [parte2.md](parte2.md) y [parte5.md](parte5.md),
con directorio de trabajo `notebooks/`. Cada notebook es independiente y empieza
en los datos originales; ejecutar 02 recalcula las 200 réplicas. No hace falta
hacerlo por cambios de documentación. La ejecución individual no sustituye la
integración y revisión grupal.

### Parte 3 pendiente y controles de integración

En [notebook 03](../notebooks/03_pronostico.ipynb), celda `2d31be77`, la salida guardada
aún muestra el fallback del artículo. El lector carga el JSON oficial cuando existe;
ese mensaje histórico no demuestra un refresco. Bajo responsabilidad de Sofía:

- Refrescar curva bottom-up, tabla de métodos/error/MAE, pronóstico condicional
  por frecuencia y sus cuatro figuras `parte3_*`, con revisión de prosa numérica.
- Las series/pronósticos top-down independientes no cambian matemáticamente por
  el JSON, pero comparten tablas/figuras con BG/NBD y deben revisarse en conjunto.
- Confirmar que 03 y 04 realmente leen el archivo oficial, sin fallback ni semilla
  rotulada como estimación. Conservar las unidades y límites de sus análisis.
- Mantener la distinción E[X]/E[Y]; verificar cada total contra su definición y
  cohorte, sin imponer igualdad entre pronósticos con diferente condicionamiento.
- Integrar las entradas de Jorge con los cambios de Herman/Gregorio, comprobar
  imports y versiones, revisión humana de conclusiones y README final del grupo.
- Coordinar la incorporación de la presentación que ahora corresponde a Gregorio.

Comando **para Sofía después del traspaso**, desde la raíz con el entorno activado:

```bash
cd notebooks
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1200 03_pronostico.ipynb
```

La celda `4dc9faa4` de notebook 01 imprime también el JSON; sus verificaciones y
simulaciones usan entradas propias. No es necesario repetir sus 80 ajustes solo
porque se sustituyó la semilla. Las figuras de compañeros no se modificaron.

## Comprobaciones de entrega

Validadores: [Parte 2](../scripts/validar_parte2.py), [Retail](../scripts/validar_retail.py).
Informes: [validacion_parte2.json](../resultados/validacion_parte2.json),
[validacion_retail.json](../resultados/validacion_retail.json). Ambos notebooks de
Jorge conservan diez celdas de código ejecutadas y ninguna salida de error; se
contrasta su contenido con tablas, parámetros y huellas guardadas, no solo contadores.

Las 22 pruebas focalizadas ya pasaron en la etapa de implementación. En esta
finalización documental se repiten los dos validadores de artefactos y se comprueban
huellas, rutas y enlaces; no se repiten bootstrap ni simulaciones. Los informes se
regeneran mediante sus scripts, sin alterar estimados ni fabricar nueva ejecución.

Huellas de originales:

- CDNOW: `6fae10155c0b0ba363c2c386e30f77990d22328220efd862a5edd1443420d94a`.
- Retail: `43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d`.

Las siete figuras de Jorge se inspeccionaron visualmente durante la implementación;
la finalización verifica su presencia e integridad. La función original de limpieza,
el enunciado completo y la guía no se recuperaron; se conserva esa limitación de
proveniencia y se aplicaron las reglas explícitas/autorizaciones del usuario.
No queda un bloqueo de implementación de Jorge por esos archivos.

## Secuencia de commits y autorización individual

Al preparar este checkpoint, el historial observado estaba en
`5b2b3524f8a2cdf1ed4f589408058df33f935eff`: **0 commits de esta
contribución creados**, índice vacío. El [plan de diez ámbitos](secuencia_commits_jorge.md)
cubre todos los cambios de Jorge una sola vez y no contiene títulos propuestos.
Ese estado corresponde al checkpoint documental previo a la secuencia.

Posteriormente se recibió la instrucción explícita **“Begin the 10-commit approval sequence.”**
y se inició la aprobación individual de títulos. Aprobar un título autoriza
únicamente su commit y no equivale a revisión científica. Los diez ámbitos se
conservan; el historial Git registra sus commits y asuntos aprobados. Se conserva
la identidad Git existente; no se reescribe historial ni se hace push.
