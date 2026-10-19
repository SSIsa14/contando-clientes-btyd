"""
Carga y preparación de datos (Parte 0).

Autora: Sofía Isabela Sandoval Vásquez

Declaración de uso de IA: se utilizó Claude (Anthropic) como herramienta de apoyo
para comprender lo que pedía cada inciso del enunciado y como asistencia al escribir
y depurar el código. El análisis, la verificación de resultados y su interpretación
fueron revisados por la autora.
"""
import numpy as np
import pandas as pd

INICIO_CDNOW = pd.Timestamp("1997-01-01")


def cargar_cdnow(ruta, inicio=INICIO_CDNOW):
    trans = pd.read_csv(
        ruta, sep=r"\s+", header=None,
        names=["id_master", "cliente", "fecha", "cds", "monto"],
        dtype={"id_master": str, "fecha": str},
    )
    trans["fecha"] = pd.to_datetime(trans["fecha"], format="%Y%m%d")

    # 0.1: varias compras el mismo día cuentan como una sola transacción
    trans = (trans.groupby(["cliente", "fecha"], as_index=False)
                  .agg(cds=("cds", "sum"), monto=("monto", "sum")))

    trans["semana"] = (trans["fecha"] - inicio).dt.days / 7
    return trans[["cliente", "fecha", "semana", "cds", "monto"]]


def resumen_clientes(trans, fin_calib, fin_holdout):
    """(x, tx, T) en calibración y x_star en holdout, en semanas.

    Calibración: hasta fin_calib inclusive. Holdout: del día siguiente a fin_holdout
    inclusive. Solo entran los clientes cuya primera compra cae en la calibración.
    """
    fin_calib, fin_holdout = pd.Timestamp(fin_calib), pd.Timestamp(fin_holdout)

    calib = trans[trans["fecha"] <= fin_calib]
    hold = trans[(trans["fecha"] > fin_calib) & (trans["fecha"] <= fin_holdout)]

    g = calib.groupby("cliente")
    res = pd.DataFrame({
        "primera": g["fecha"].min(),
        "ultima": g["fecha"].max(),
        "n_calib": g.size(),
        "semana_primera": g["semana"].min(),
    })
    res["x"] = res["n_calib"] - 1
    res["tx"] = (res["ultima"] - res["primera"]).dt.days / 7
    res["T"] = (fin_calib - res["primera"]).dt.days / 7
    res["x_star"] = hold.groupby("cliente").size().reindex(res.index, fill_value=0)

    return (res.reset_index()[["cliente", "x", "tx", "T", "x_star", "semana_primera"]]
               .astype({"x": int, "x_star": int}))


def serie_semanal_repetidas(trans, n_semanas):
    """Compras repetidas (sin la primera de cada cliente) por semana 1..n_semanas."""
    primera = trans.groupby("cliente")["fecha"].transform("min")
    rep = trans[trans["fecha"] > primera]
    semana = np.floor(rep["semana"]).astype(int) + 1
    conteo = semana.value_counts().reindex(range(1, n_semanas + 1), fill_value=0)
    return conteo.sort_index()
