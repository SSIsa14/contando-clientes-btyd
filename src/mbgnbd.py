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
from scipy.special import betaln, gammaln

from bgnbd import ajustar_bgnbd


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
