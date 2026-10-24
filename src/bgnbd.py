"""
Modelo BG/NBD.

Log-verosimilitud — Herman Andrés Echeverría Rojas
Funciones de pronóstico E[X(t)] y E[Y(tau)] — Sofía Isabela Sandoval Vásquez

Referencia: Fader, Hardie y Lee (2005), "Counting Your Customers the Easy Way",
Marketing Science 24(2), ecuaciones (6) y (7); y la nota de implementación en
http://brucehardie.com/notes/004/.

Declaración de uso de IA: se utilizó Claude (Anthropic) como herramienta de apoyo
para comprender lo que pedía cada inciso del enunciado y como asistencia al escribir
y depurar el código. El análisis, la verificación de resultados y su interpretación
fueron revisados por los autores.
"""
import numpy as np
from scipy.special import betaln, gammaln, hyp2f1

PARAMS_ARTICULO = {"r": 0.243, "alpha": 4.414, "a": 0.793, "b": 2.426}
NOMBRES = ("r", "alpha", "a", "b")


def loglik_individual(log_params, x, tx, T):
    """ln L(r, alpha, a, b | x, tx, T) de cada cliente (ecuación 6 del artículo).

    Los parámetros entran en logaritmo para que el optimizador trabaje sin
    restricciones de positividad. La suma de los dos términos de la ecuación se
    hace con logaddexp para no perder precisión cuando ambos son muy pequeños.
    """
    r, alpha, a, b = np.exp(log_params)
    x, tx, T = (np.asarray(v, dtype=float) for v in (x, tx, T))

    # Con x = 0 el segundo término no existe (delta_{x>0} = 0); xs evita evaluar
    # betaln(a + 1, b - 1), que no tiene sentido si b < 1, y luego se descarta.
    xs = np.maximum(x, 1)
    base = gammaln(r + x) - gammaln(r) + r * np.log(alpha)
    vivo = betaln(a, b + x) - betaln(a, b) - (r + x) * np.log(alpha + T)
    muerto = np.where(
        x > 0,
        betaln(a + 1, b + xs - 1) - betaln(a, b) - (r + x) * np.log(alpha + tx),
        -np.inf,
    )
    return base + np.logaddexp(vivo, muerto)


def loglik_bgnbd(log_params, x, tx, T):
    """Log-verosimilitud de la muestra (ecuación 7): suma de las individuales."""
    return float(np.sum(loglik_individual(log_params, x, tx, T)))

