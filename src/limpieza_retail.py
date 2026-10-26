"""Preparación Retail: sustitución expresamente autorizada por el usuario.

NO es la función original de series de tiempo, que no fue recuperada. Implementa
las reglas acordadas para Parte 5; no atribuye al original ningún filtro. Trabajo
asistido por Codex (OpenAI), responsabilidad de Jorge; revisión humana pendiente.

No elimina duplicados, devoluciones, cancelaciones, precios negativos ni líneas de
importe cero. Description/Country no determinan exclusiones. Se usa aritmética
entera a escala decimal derivada de Decimal(str(valor)): sin redondeo a centavos,
sin epsilon y sin residuo binario para decidir si una venta neta es positiva.
"""
from collections import Counter
from decimal import Decimal, InvalidOperation

import numpy as np
import pandas as pd

from datos import resumen_clientes

INICIO_RETAIL = pd.Timestamp("2010-12-01")
FIN_CALIB_RETAIL = pd.Timestamp("2011-06-30")
FIN_HOLDOUT_RETAIL = pd.Timestamp("2011-12-08")


def _decimales(serie, nombre):
    valores = []
    for v in serie:
        try:
            d = Decimal(str(v).strip())
        except InvalidOperation:
            raise ValueError(f"{nombre}: valor no numérico; no se descarta silenciosamente") from None
        if not d.is_finite():
            raise ValueError(f"{nombre}: valor ausente/no finito; revisar los datos")
        valores.append(d)
    return valores


def _entero_escalado(d, escala):
    signo, digitos, exponente = d.as_tuple()
    coeficiente = int("".join(map(str, digitos)))
    return (-1 if signo else 1) * coeficiente * 10 ** (exponente + escala)


def _texto_decimal(entero, escala):
    signo = "-" if entero < 0 else ""
    texto = str(abs(entero)).zfill(escala + 1)
    if escala:
        texto = (texto[:-escala] + "." + texto[-escala:]).rstrip("0").rstrip(".")
    return signo + texto


def limpiar(datos, *, devolver_auditoria=False):
    """Devuelve transacciones positivas cliente-día, sin modificar ``datos``.

    CustomerID se valida como identificador entero finito y se representa como
    texto decimal canónico (12345 y 12345.0 son la misma identidad). Las únicas
    filas excluidas son las que carecen de ID. Fechas malformadas, zonas horarias
    ambiguas o números no finitos generan error explícito, incluso antes de excluir
    IDs ausentes. La normalización es por día calendario, sin truncar importes.

    Con devolver_auditoria=True devuelve (transacciones, todos_los_dias, auditoria).
    ``todos_los_dias`` conserva también netos cero/negativos e importes exactos.
    Los conteos de líneas y de facturas únicas se registran separadamente.
    """
    requeridas = {"InvoiceNo", "CustomerID", "InvoiceDate", "Quantity", "UnitPrice"}
    faltantes = requeridas - set(datos.columns)
    if faltantes:
        raise ValueError(f"Columnas requeridas ausentes: {sorted(faltantes)}")
    if len(datos) == 0:
        raise ValueError("No hay líneas Retail")
    fechas = pd.to_datetime(datos["InvoiceDate"], errors="coerce", format="mixed")
    if fechas.isna().any():
        raise ValueError(f"InvoiceDate: {int(fechas.isna().sum())} fechas ausentes/malformadas")
    try:
        if fechas.dt.tz is not None:
            raise ValueError("Se requieren fechas locales sin zona horaria")
        fechas = fechas.dt.normalize()
    except AttributeError:
        raise ValueError("InvoiceDate: zonas horarias mixtas/no admitidas") from None
    cantidades = _decimales(datos["Quantity"], "Quantity")
    precios = _decimales(datos["UnitPrice"], "UnitPrice")
    escala_q = max(0, max(-v.as_tuple().exponent for v in cantidades))
    escala_p = max(0, max(-v.as_tuple().exponent for v in precios))
    escala = escala_q + escala_p
    importes = [_entero_escalado(q, escala_q) * _entero_escalado(p, escala_p)
                for q, p in zip(cantidades, precios)]
    ids_ausentes = datos["CustomerID"].isna() | datos["CustomerID"].astype(str).str.strip().eq("")
    ids = []
    for ausente, valor in zip(ids_ausentes, datos["CustomerID"]):
        if ausente:
            ids.append(None)
            continue
        d = _decimales([valor], "CustomerID")[0]
        if d != d.to_integral_value():
            raise ValueError("CustomerID debe ser un identificador entero")
        ids.append(str(int(d)))
    facturas = datos["InvoiceNo"].astype("string").str.strip()
    cancelacion = facturas.str.upper().str.startswith("C", na=False)
    lineas = pd.DataFrame({
        "cliente": ids, "fecha": fechas.to_numpy(), "factura": facturas.to_numpy(),
        "neto_unidades": pd.Series(importes, dtype=object),
        "cantidad_negativa": [q < 0 for q in cantidades],
        "importe_negativo": [v < 0 for v in importes],
        "cancelacion": cancelacion.to_numpy(),
    })
    conservadas = lineas[lineas["cliente"].notna()].copy()
    if conservadas.empty:
        raise ValueError("Ninguna línea tiene CustomerID")
    dias = conservadas.groupby(["cliente", "fecha"], as_index=False, sort=True).agg(
        neto_unidades=("neto_unidades", "sum"), lineas=("factura", "size"),
        facturas_distintas=("factura", "nunique"),
        lineas_cantidad_negativa=("cantidad_negativa", "sum"),
        lineas_importe_negativo=("importe_negativo", "sum"),
        lineas_cancelacion=("cancelacion", "sum"))
    dias["venta_neta_exacta"] = [_texto_decimal(int(v), escala) for v in dias.neto_unidades]
    dias["califica"] = dias.neto_unidades > 0
    trans = dias[dias.califica].copy().reset_index(drop=True)
    trans["semana"] = (trans.fecha - INICIO_RETAIL).dt.days / 7
    auditoria = {
        "limpiar": "sustitución autorizada; original no recuperada",
        "filas_originales": len(datos), "filas_sin_customerid": int(ids_ausentes.sum()),
        "filas_con_customerid": len(conservadas), "filas_invalidas": 0,
        "facturas_unicas_originales": int(facturas.nunique()),
        "facturas_unicas_con_customerid": int(conservadas.factura.nunique()),
        "filas_sin_factura": int(facturas.isna().sum()),
        "filas_duplicadas_exactas_originales": int(datos.duplicated().sum()),
        "politica_duplicados": "se conservan todas las líneas idénticas; no se prueba que sean errores",
        "filas_quantity_negativa_originales": sum(q < 0 for q in cantidades),
        "filas_quantity_negativa_conservadas": int(conservadas.cantidad_negativa.sum()),
        "filas_cancelacion_originales": int(cancelacion.sum()),
        "filas_cancelacion_conservadas": int(conservadas.cancelacion.sum()),
        "filas_importe_negativo_conservadas": int(conservadas.importe_negativo.sum()),
        "filas_unitprice_no_positivo_originales": sum(p <= 0 for p in precios),
        "clientes_identificados": int(conservadas.cliente.nunique()),
        "dias_cliente_totales": len(dias), "dias_neto_cero": int((dias.neto_unidades == 0).sum()),
        "dias_neto_negativo": int((dias.neto_unidades < 0).sum()),
        "transacciones_calificantes_todo_archivo": len(trans),
        "clientes_calificantes_todo_archivo": int(trans.cliente.nunique()),
        "dias_positivos_con_importes_negativos": int((dias.califica & (dias.lineas_importe_negativo > 0)).sum()),
        "precision": {"metodo": "Decimal(str(valor)) a enteros de escala común; sin redondear ni epsilon",
            "decimales_quantity": escala_q, "decimales_unitprice": escala_p,
            "escala_importe": escala,
            "distribucion_decimales_unitprice": dict(sorted(Counter(max(0, -p.as_tuple().exponent) for p in precios).items()))},
        "venta_neta_conservada_exacta": _texto_decimal(sum(int(v) for v in conservadas.neto_unidades), escala),
        "fecha_min": fechas.min().isoformat(), "fecha_max": fechas.max().isoformat(),
        "origen_semanas": INICIO_RETAIL.date().isoformat(),
        "filtros_no_aplicados": ["país", "frecuencia mínima", "outliers", "precio positivo", "deduplicación"],
    }
    return (trans, dias, auditoria) if devolver_auditoria else trans


def historias_retail(trans, fin_calib=FIN_CALIB_RETAIL, fin_holdout=FIN_HOLDOUT_RETAIL):
    """Adaptador de resumen_clientes; cohorte solo con adquisición calificante en calibración."""
    fin_calib, fin_holdout = pd.Timestamp(fin_calib), pd.Timestamp(fin_holdout)
    if fin_holdout <= fin_calib:
        raise ValueError("El holdout debe terminar después de calibración")
    if trans.duplicated(["cliente", "fecha"]).any():
        raise ValueError("Se requiere una fila por cliente-día calificante")
    if not trans.fecha.eq(trans.fecha.dt.normalize()).all():
        raise ValueError("Las fechas deben estar normalizadas a día")
    if not (trans.neto_unidades > 0).all():
        raise ValueError("Las historias requieren exclusivamente días netos positivos")
    disponibles = trans[trans.fecha <= fin_holdout].copy()
    disponibles["semana"] = (disponibles.fecha - INICIO_RETAIL).dt.days / 7
    res = resumen_clientes(disponibles, fin_calib, fin_holdout)
    calib = disponibles[disponibles.fecha <= fin_calib].groupby("cliente").fecha
    res["adquisicion"] = res.cliente.map(calib.min())
    res["ultima_calibracion"] = res.cliente.map(calib.max())
    return res
