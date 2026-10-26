"""
Modelo MBG/NBD (inciso 4.6).

Autor: José Gregorio Coronel Colombo

Cambia una sola pieza del BG/NBD: el cliente también puede morir justo después de
su primera compra, así que desaparece delta_{x>0} y P(vivo) < 1 incluso con x = 0.

Referencia: Batislam, Denizel y Filiztekin (2007), "Empirical Validation and
Comparison of Models for Customer Base Analysis", International Journal of
Research in Marketing 24(3); fórmulas tal como aparecen en el enunciado.

Declaración de uso de IA: se utilizó inteligencia artificial como herramienta de apoyo
para comprender lo que pedía cada inciso del enunciado y como asistencia al escribir
y depurar el código. El análisis, la verificación de resultados y su interpretación
fueron revisados por el autor.
"""
import numpy as np
from scipy.special import betaln, gammaln, hyp2f1

from bgnbd import ajustar_bgnbd, p_compra_si_vivo


def loglik_individual_mbgnbd(log_params, x, tx, T):
    """ln L(r, alpha, a, b | x, tx, T) de cada cliente en el MBG/NBD.

    Igual que en el BG/NBD, pero el término de "murió después de la última compra"
    existe también con x = 0 (en ese caso tx = 0) y los argumentos de betaln se
    corren en uno: B(a, b + x + 1) y B(a + 1, b + x).
    """
    r, alpha, a, b = np.exp(log_params)
    x, tx, T = (np.asarray(v, dtype=float) for v in (x, tx, T))

    base = gammaln(r + x) - gammaln(r) + r * np.log(alpha)
    vivo = betaln(a, b + x + 1) - betaln(a, b) - (r + x) * np.log(alpha + T)
    muerto = betaln(a + 1, b + x) - betaln(a, b) - (r + x) * np.log(alpha + tx)
    return base + np.logaddexp(vivo, muerto)


def loglik_mbgnbd(log_params, x, tx, T):
    """Log-verosimilitud de la muestra: suma de las individuales."""
    return float(np.sum(loglik_individual_mbgnbd(log_params, x, tx, T)))


def ajustar_mbgnbd(x, tx, T, inicios=None):
    """Máxima verosimilitud con el mismo optimizador y arranques que ajustar_bgnbd."""
    return ajustar_bgnbd(x, tx, T, inicios=inicios, loglik=loglik_mbgnbd)


def p_vivo_mbgnbd(x, tx, T, params):
    """P(vivo | x, tx, T) en el MBG/NBD; ya no hay delta_{x>0}, así que con x = 0 es < 1."""
    r, alpha, a, b = params["r"], params["alpha"], params["a"], params["b"]
    x, tx, T = (np.asarray(v, dtype=float) for v in (x, tx, T))
    return 1 / (1 + a / (b + x) * ((alpha + T) / (alpha + tx)) ** (r + x))


def p_compra_mbgnbd(tau, x, tx, T, params):
    """P(Z = 1 | x, tx, T): la fórmula de 4.3 sigue valiendo con el P(vivo) del MBG/NBD.

    Un cliente vivo que no compra sigue vivo y el posterior de lambda dado vivo es el
    mismo Gamma(r + x, alpha + T); solo cambia la probabilidad de estar vivo.
    """
    return p_vivo_mbgnbd(x, tx, T, params) * p_compra_si_vivo(tau, x, T, params)


def esperado_X_mbgnbd(t, params):
    """Compras repetidas esperadas en (0, t] para un cliente recién adquirido."""
    r, alpha, a, b = params["r"], params["alpha"], params["a"], params["b"]
    t = np.asarray(t, dtype=float)
    return b / (a - 1) * (1 - (alpha / (alpha + t)) ** r * hyp2f1(r, b + 1, a + b, t / (alpha + t)))


def esperado_Y_mbgnbd(tau, x, tx, T, params):
    """Compras esperadas en las siguientes tau semanas dado el historial (x, tx, T)."""
    r, alpha, a, b = params["r"], params["alpha"], params["a"], params["b"]
    x, tx, T = (np.asarray(v, dtype=float) for v in (x, tx, T))

    A = (alpha + T) / (alpha + T + tau)
    D = 1 + a / (b + x) * ((alpha + T) / (alpha + tx)) ** (r + x)
    num = 1 - A ** (r + x) * hyp2f1(r + x, b + x + 1, a + b + x, 1 - A)
    return (a + b + x) / (a - 1) * num / D
