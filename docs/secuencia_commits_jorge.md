# Secuencia propuesta de diez ámbitos de commit de Jorge

Este documento contiene ámbitos y archivos, **no títulos de commit**. No autoriza
staging ni commits. La contribución completa comprende exactamente diez commits
nuevos: al preparar este checkpoint el historial local estaba en `5b2b3524f8a2cdf1ed4f589408058df33f935eff`,
sin commits posteriores de implementación de Jorge. Los commits previos del grupo
no se atribuyen a Jorge por autoría o por mencionar una futura tarea suya.

La propuesta original y los análisis/figuras de los compañeros permanecen intactos.
Las agrupaciones se basan en capacidades y productos reales, sin padding. Todas
son no vacías y cada archivo cambiado aparece una sola vez.

| Orden | Ámbito | Dependencias | Archivos |
|---|---|---|---|
| 1 | Entorno reproducible y soporte de lectura Excel | — | [requirements.txt](../requirements.txt); [requirements-parte2.lock](../requirements-parte2.lock) |
| 2 | Diagnóstico y aceptación del ajuste compartido, con regresiones BG/MBG | 1 | [src/bgnbd.py](../src/bgnbd.py); [tests/test_ajuste.py](../tests/test_ajuste.py) |
| 3 | Bootstrap por clientes y garantías de muestreo/reintentos | 2 | [src/bootstrap_cdnow.py](../src/bootstrap_cdnow.py); [tests/test_bootstrap.py](../tests/test_bootstrap.py) |
| 4 | Recuperación verificable del original Retail | 1 | [data/Online Retail.xlsx](../data/Online%20Retail.xlsx); [data/online_retail_origen.json](../data/online_retail_origen.json); [scripts/obtener_retail.py](../scripts/obtener_retail.py) |
| 5 | Sustitución autorizada Retail, historias y contratos de calendario | 2, 4 | [src/limpieza_retail.py](../src/limpieza_retail.py); [src/pronostico_retail.py](../src/pronostico_retail.py); [tests/test_retail.py](../tests/test_retail.py) |
| 6 | Análisis CDNOW ejecutado y publicación oficial de Partes 2.1–2.3 | 2, 3 | [notebooks/02_ajuste_cdnow.ipynb](../notebooks/02_ajuste_cdnow.ipynb); [resultados/params_cdnow.json](../resultados/params_cdnow.json); [resultados/ajuste_cdnow_proveniencia.json](../resultados/ajuste_cdnow_proveniencia.json); [resultados/interpretacion_cdnow.json](../resultados/interpretacion_cdnow.json); [resultados/bootstrap_cdnow.csv](../resultados/bootstrap_cdnow.csv); [resultados/bootstrap_cdnow_diagnosticos.json](../resultados/bootstrap_cdnow_diagnosticos.json); [resultados/bootstrap_cdnow_resumen.json](../resultados/bootstrap_cdnow_resumen.json); [figs/parte2_densidad_lambda.png](../figs/parte2_densidad_lambda.png); [figs/parte2_densidad_p.png](../figs/parte2_densidad_p.png); [figs/parte2_bootstrap_parametros.png](../figs/parte2_bootstrap_parametros.png) |
| 7 | Análisis Retail ejecutado y entrega de ajuste, sensibilidad y pronóstico | 5, 6 | [notebooks/05_online_retail.ipynb](../notebooks/05_online_retail.ipynb); [resultados/params_retail.json](../resultados/params_retail.json); [resultados/ajuste_retail_proveniencia.json](../resultados/ajuste_retail_proveniencia.json); [resultados/retail_holdout.json](../resultados/retail_holdout.json); [resultados/retail_limpieza_auditoria.json](../resultados/retail_limpieza_auditoria.json); [resultados/retail_dias.csv](../resultados/retail_dias.csv); [resultados/retail_clientes.csv](../resultados/retail_clientes.csv); [resultados/retail_frecuencias.csv](../resultados/retail_frecuencias.csv); [resultados/retail_sensibilidad.csv](../resultados/retail_sensibilidad.csv); [resultados/retail_diario.csv](../resultados/retail_diario.csv); [resultados/retail_semanal.csv](../resultados/retail_semanal.csv); [resultados/retail_mensual.csv](../resultados/retail_mensual.csv); [figs/parte5_historias.png](../figs/parte5_historias.png); [figs/parte5_holdout_acumulado.png](../figs/parte5_holdout_acumulado.png); [figs/parte5_holdout_semanal.png](../figs/parte5_holdout_semanal.png); [figs/parte5_meses_por_dia.png](../figs/parte5_meses_por_dia.png) |
| 8 | Auditoría de consistencia y reproducción de Parte 2 | 6 | [scripts/validar_parte2.py](../scripts/validar_parte2.py); [resultados/validacion_parte2.json](../resultados/validacion_parte2.json); [docs/parte2.md](../docs/parte2.md) |
| 9 | Oráculo independiente y reproducción de Retail | 7 | [scripts/validar_retail.py](../scripts/validar_retail.py); [resultados/validacion_retail.json](../resultados/validacion_retail.json); [docs/parte5.md](../docs/parte5.md) |
| 10 | Traspaso por destinatario, alcance vigente y cierre documental | 8, 9 | [README.md](../README.md); [docs/entrega_jorge.md](../docs/entrega_jorge.md); [docs/secuencia_commits_jorge.md](../docs/secuencia_commits_jorge.md) |

## Coherencia de los snapshots

- El entorno antecede a imports nuevos; diagnóstico y pruebas BG/MBG se incorporan
  juntos. El bootstrap y sus pruebas solo dependen del ajustador ya incorporado.
- Las pruebas Retail importan tanto limpieza como pronóstico calendario: ambos
  módulos se incorporan juntos, después de las dependencias y entrada original.
- Los notebooks llegan con sus parámetros, resultados y figuras completos, cuando
  ya existen sus imports. El paso 7 también conserva el hash del parámetro CDNOW
  publicado en el paso 6.
- Las auditorías de los pasos 8 y 9 llegan después de los productos que verifican,
  junto con sus informes y guías de reproducción. Los enlaces documentales futuros
  de los notebooks quedan resueltos al incorporar esas guías; no son dependencias
  ejecutables ocultas. El traspaso documental completo se cierra en el paso 10.
- No se necesitan versiones parciales artificiales de notebooks ni regenerar
  resultados para repartirlos. No se toma trabajo de Parte 3/4 ni se crea presentación.
- Los 47 archivos previstos corresponden a cuatro archivos rastreados modificados
  y 43 archivos nuevos. El entorno ignorado, cachés y temporales no forman parte de
  los commits. Si cambia el árbol antes de comenzar, volver a inspeccionar y
  preservar trabajo ajeno sin añadir commits para superar diez.

## Protocolo de aprobación individual

La secuencia comenzó después de recibirse la instrucción explícita
**“Begin the 10-commit approval sequence.”**. El protocolo exige proponer solo un
título para el ámbito actual y esperar aprobación.
Una sustitución inequívoca del título autoriza ese reemplazo para ese commit.

Tras aprobarse: incorporar solo archivos/hunks del ámbito, inspeccionar el diff
staged, crear únicamente ese commit, comprobar que su mensaje almacenado coincide
exactamente con el título aprobado y comunicar hash corto. Luego proponer el
siguiente título y esperar. No se presupone aprobación de títulos posteriores.

Todos los mensajes serán solo asunto, en inglés claro e imperativo: sin cuerpo,
prefijos convencionales, emojis, números de secuencia, etiquetas, puntuación
decorativa, coautorías, sign-offs o atribución automática. La posición de la secuencia
se comunica fuera del mensaje. No se modifica identidad Git ni historial, y no se
hace push al terminar. Una aprobación de título no demuestra revisión científica.

El checkpoint original fue solo informe: en ese momento no se había hecho staging,
creado commits ni propuesto títulos. La autorización y ejecución posteriores se
registran en la conversación y el historial Git, sin cambiar los ámbitos revisados.
