"""Tablas calendario del holdout Retail usando esperado_Y compartido.

Responsabilidad de Jorge; asistencia de Codex (OpenAI), revisión humana pendiente.
No modifica parámetros ni reemplaza resultados numéricos inválidos.
"""
import numpy as np
import pandas as pd

from bgnbd import esperado_Y
from limpieza_retail import FIN_CALIB_RETAIL, FIN_HOLDOUT_RETAIL


def tablas_holdout(trans, res, params, fin_calib=FIN_CALIB_RETAIL, fin_holdout=FIN_HOLDOUT_RETAIL):
    """Devuelve diario, semanal y mensual, con la misma cohorte y extremos inclusivos.

    Semana 1: 1–7 julio; semana 23: 2–8 diciembre. Las compras previstas por
    intervalo son diferencias de expectativas condicionales acumuladas. El cero
    corresponde al corte del 30 junio; las fechas se interpretan por día calendario.
    """
    fin_calib, fin_holdout = pd.Timestamp(fin_calib), pd.Timestamp(fin_holdout)
    fechas = pd.date_range(fin_calib + pd.Timedelta(days=1), fin_holdout, freq="D")
    if len(fechas) == 0 or not res.cliente.is_unique:
        raise ValueError("Se requiere holdout positivo y una fila por cliente")
    cortes = np.arange(len(fechas) + 1, dtype=float) / 7
    x, tx, T = (res[k].to_numpy(dtype=float)[None, :] for k in ("x", "tx", "T"))
    acumulado = esperado_Y(cortes[:, None], x, tx, T, params)
    if not np.isfinite(acumulado).all() or np.any(acumulado < 0):
        raise ValueError("esperado_Y produjo valores no finitos o negativos")
    if not np.allclose(acumulado[0], 0, atol=1e-12, rtol=0):
        raise ValueError("La expectativa a horizonte cero no es cero")
    if np.any(np.diff(acumulado, axis=0) < 0):
        raise ValueError("La expectativa acumulada no es monótona por cliente")
    total_acum = acumulado.sum(axis=1)
    hold = trans[(trans.fecha > fin_calib) & (trans.fecha <= fin_holdout)
                 & trans.cliente.isin(res.cliente)]
    real = hold.groupby("fecha").size().reindex(fechas, fill_value=0).to_numpy()
    if int(real.sum()) != int(res.x_star.sum()):
        raise ValueError("Los historiales y el conteo de holdout no coinciden")
    diario = pd.DataFrame({"fecha": fechas, "dia": np.arange(1, len(fechas) + 1),
        "tau_semanas": cortes[1:], "real": real, "pronostico": np.diff(total_acum),
        "real_acumulado": np.cumsum(real), "pronostico_acumulado": total_acum[1:]})
    diario["semana_holdout"] = np.arange(len(fechas)) // 7 + 1
    diario["mes"] = diario.fecha.dt.strftime("%Y-%m")

    def agrupar(columna):
        tabla = diario.groupby(columna, as_index=False).agg(
            fecha_inicio=("fecha", "min"), fecha_fin=("fecha", "max"),
            dias=("fecha", "size"), real=("real", "sum"), pronostico=("pronostico", "sum"))
        tabla["real_por_dia"] = tabla.real / tabla.dias
        tabla["pronostico_por_dia"] = tabla.pronostico / tabla.dias
        tabla["error_firmado"] = tabla.pronostico - tabla.real
        return tabla

    semanal, mensual = agrupar("semana_holdout"), agrupar("mes")
    for tabla in (semanal, mensual):
        np.testing.assert_allclose(tabla.pronostico.sum(), total_acum[-1], rtol=1e-12, atol=1e-9)
        assert int(tabla.real.sum()) == int(res.x_star.sum())
    return diario, semanal, mensual
