"""
Simulación de clientes bajo el BG/NBD (inciso 1.3).

Autor: Herman Andrés Echeverría Rojas

Declaración de uso de IA: se utilizó Claude (Anthropic) como herramienta de apoyo
para comprender lo que pedía cada inciso del enunciado y como asistencia al escribir
y depurar el código. El análisis, la verificación de resultados y su interpretación
fueron revisados por el autor.
"""
import numpy as np
import pandas as pd

from bgnbd import NOMBRES


def simular_clientes(n, params, rng, T_min=27, T_max=39, horizonte_extra=0):
    """Genera (x, tx, T, x_star) para n clientes siguiendo los supuestos del BG/NBD.

    Cada cliente recibe lambda ~ Gamma(r, tasa alpha) y p ~ Beta(a, b), y un periodo
    de calibración T ~ Uniforme(T_min, T_max). Desde t = 0 (su primera compra) se
    sortean esperas exponenciales con tasa lambda; cada compra repetida cuenta en x
    si cae en (0, T] o en x_star si cae en (T, T + horizonte_extra], y después de
    ella el cliente muere con probabilidad p.

    La simulación avanza compra por compra para todos los clientes a la vez, de
    modo que el ciclo depende del número máximo de compras y no de n.
    """
    r, alpha, a, b = (params[k] for k in NOMBRES)
    lam = rng.gamma(r, 1 / alpha, size=n)        # numpy usa escala = 1 / tasa
    p = rng.beta(a, b, size=n)
    T = rng.uniform(T_min, T_max, size=n)
    fin = T + horizonte_extra

    t = np.zeros(n)
    x = np.zeros(n, dtype=int)
    tx = np.zeros(n)
    x_star = np.zeros(n, dtype=int)
    activo = np.ones(n, dtype=bool)

    while activo.any():
        idx = np.flatnonzero(activo)
        with np.errstate(divide="ignore"):       # lambda = 0 da una espera infinita
            t[idx] += rng.standard_exponential(idx.size) / lam[idx]

        fuera = t[idx] > fin[idx]
        activo[idx[fuera]] = False
        idx = idx[~fuera]

        en_calib = t[idx] <= T[idx]
        x[idx[en_calib]] += 1
        tx[idx[en_calib]] = t[idx[en_calib]]
        x_star[idx[~en_calib]] += 1

        muere = rng.random(idx.size) < p[idx]
        activo[idx[muere]] = False

    return pd.DataFrame({"x": x, "tx": tx, "T": T, "x_star": x_star})

