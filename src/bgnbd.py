"""
Modelo BG/NBD.

Log-verosimilitud y ajuste por máxima verosimilitud — Herman Andrés Echeverría Rojas
Funciones de pronóstico E[X(t)] y E[Y(tau)] — Sofía Isabela Sandoval Vásquez
P(vivo) y P(Z = 1) — José Gregorio Coronel Colombo

Referencia: Fader, Hardie y Lee (2005), "Counting Your Customers the Easy Way",
Marketing Science 24(2), ecuaciones (6) y (7); y la nota de implementación en
http://brucehardie.com/notes/004/.

Declaración de uso de IA: se utilizó Claude (Anthropic) como herramienta de apoyo
para comprender lo que pedía cada inciso del enunciado y como asistencia al escribir
y depurar el código. El análisis, la verificación de resultados y su interpretación
fueron revisados por los autores.
"""
import warnings

import numpy as np
from scipy.optimize import minimize
from scipy.special import betaln, gammaln, hyp2f1

PARAMS_ARTICULO = {"r": 0.243, "alpha": 4.414, "a": 0.793, "b": 2.426}
NOMBRES = ("r", "alpha", "a", "b")
COTA_LOG = 10.0


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


def _inicios_por_defecto(semilla=0):
    rng = np.random.default_rng(semilla)
    return [
        np.zeros(4),                                             # r = alpha = a = b = 1
        np.log([PARAMS_ARTICULO[k] for k in NOMBRES]),           # valores del artículo
        rng.uniform(-2, 2, size=4),                              # arranque aleatorio
    ]


def ajustar_bgnbd(x, tx, T, inicios=None):
    """Estimador de máxima verosimilitud de (r, alpha, a, b).

    Minimiza -LL/n sobre los log-parámetros con Nelder–Mead y con L-BFGS-B
    (cotas [-10, 10]) desde cada arranque de `inicios` y se queda con la mejor
    solución. Dividir entre n no cambia el óptimo y deja la función en una escala
    cómoda para las tolerancias del optimizador. Si algún parámetro termina en la
    cota emite una advertencia, porque entonces el máximo no es interior.

    Devuelve {"r", "alpha", "a", "b", "ll"} con ll en la escala original (suma).
    """
    x, tx, T = (np.asarray(v, dtype=float) for v in (x, tx, T))
    n = x.size
    inicios = _inicios_por_defecto() if inicios is None else inicios
    cotas = [(-COTA_LOG, COTA_LOG)] * 4

    def objetivo(log_params):
        valor = -loglik_bgnbd(log_params, x, tx, T) / n
        return valor if np.isfinite(valor) else np.inf

    mejor = None
    for inicio in inicios:
        for metodo, opciones in (
            ("Nelder-Mead", {"maxiter": 20_000, "xatol": 1e-8, "fatol": 1e-10}),
            ("L-BFGS-B", {"maxiter": 20_000, "ftol": 1e-12, "gtol": 1e-8}),
        ):
            res = minimize(objetivo, np.asarray(inicio, dtype=float), method=metodo,
                           bounds=cotas, options=opciones)
            if mejor is None or res.fun < mejor.fun:
                mejor = res

    if np.any(np.abs(mejor.x) >= COTA_LOG - 1e-3):
        en_cota = [k for k, v in zip(NOMBRES, mejor.x) if abs(v) >= COTA_LOG - 1e-3]
        warnings.warn(f"Parámetros en la cota de búsqueda: {en_cota}", RuntimeWarning)

    estimados = dict(zip(NOMBRES, np.exp(mejor.x)))
    estimados["ll"] = -mejor.fun * n
    return estimados


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


def p_vivo(x, tx, T, params):
    """P(vivo | x, tx, T): probabilidad de que el cliente siga activo en T.

    Con x = 0 vale exactamente 1: en el BG/NBD solo se muere justo después de una
    compra repetida, y el cliente todavía no ha hecho ninguna.
    """
    r, alpha, a, b = params["r"], params["alpha"], params["a"], params["b"]
    x, tx, T = (np.asarray(v, dtype=float) for v in (x, tx, T))
    xs = np.maximum(x, 1)  # evita b + x - 1 <= 0 cuando x = 0; ese término se anula abajo
    cociente = np.where(x > 0, a / (b + xs - 1) * ((alpha + T) / (alpha + tx)) ** (r + x), 0.0)
    return 1 / (1 + cociente)


def p_compra(tau, x, tx, T, params):
    """P(Z = 1 | x, tx, T): probabilidad de al menos una compra en las siguientes tau semanas.

    Un cliente vivo que no compra sigue vivo, y dado que está vivo lambda | datos ~
    Gamma(r + x, alpha + T); por la mezcla gamma–Poisson, la probabilidad de cero
    compras en tau semanas es ((alpha + T) / (alpha + T + tau))^(r + x) (inciso 4.3).
    """
    return p_vivo(x, tx, T, params) * p_compra_si_vivo(tau, x, T, params)


def p_compra_si_vivo(tau, x, T, params):
    """1 - P(0 compras en tau | vivo); no depende de tx ni de (a, b), por eso lo reusa el MBG/NBD."""
    r, alpha = params["r"], params["alpha"]
    x, T = (np.asarray(v, dtype=float) for v in (x, T))
    return 1 - ((alpha + T) / (alpha + T + tau)) ** (r + x)
