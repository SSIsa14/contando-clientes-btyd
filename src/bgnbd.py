"""
Modelo BG/NBD.

Funciones de pronóstico E[X(t)] y E[Y(tau)] — Sofía Isabela Sandoval Vásquez

Declaración de uso de IA: se utilizó Claude (Anthropic) como herramienta de apoyo
para comprender lo que pedía cada inciso del enunciado y como asistencia al escribir
y depurar el código. El análisis, la verificación de resultados y su interpretación
fueron revisados por la autora.
"""
import numpy as np
from scipy.special import hyp2f1


def esperado_X(t, params):
    """Compras repetidas esperadas en (0, t] para un cliente recién adquirido."""
    r, alpha, a, b = params["r"], params["alpha"], params["a"], params["b"]
    t = np.asarray(t, dtype=float)
    z = t / (alpha + t)
    return ((a + b - 1) / (a - 1)
            * (1 - (alpha / (alpha + t)) ** r * hyp2f1(r, b, a + b - 1, z)))


def esperado_Y(tau, x, tx, T, params):
    """Compras esperadas en las siguientes tau semanas dado el historial (x, tx, T)."""
    r, alpha, a, b = params["r"], params["alpha"], params["a"], params["b"]
    x, tx, T = (np.asarray(v, dtype=float) for v in (x, tx, T))

    A = (alpha + T) / (alpha + T + tau)
    xs = np.maximum(x, 1)  # evita b + x - 1 <= 0 cuando x = 0; ese término se anula abajo
    D = 1 + np.where(x > 0, a / (b + xs - 1) * ((alpha + T) / (alpha + tx)) ** (r + x), 0.0)
    num = 1 - A ** (r + x) * hyp2f1(r + x, b + x, a + b + x - 1, 1 - A)
    return (a + b + x - 1) / (a - 1) * num / D
