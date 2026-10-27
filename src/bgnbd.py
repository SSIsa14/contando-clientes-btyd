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

Extensión de diagnóstico y validación (Parte 2, Jorge Ferguson): elaborada con
asistencia de Codex (OpenAI).
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


class ErrorAjuste(RuntimeError):
    """Ajuste rechazado; conserva todos los intentos en ``diagnostico``."""

    def __init__(self, mensaje, diagnostico):
        super().__init__(mensaje)
        self.diagnostico = diagnostico


def _validar_historias(x, tx, T):
    x, tx, T = (np.asarray(v, dtype=float) for v in (x, tx, T))
    if x.ndim != 1 or not (x.shape == tx.shape == T.shape) or x.size == 0:
        raise ValueError("x, tx y T deben ser vectores no vacíos de igual longitud")
    if not all(np.isfinite(v).all() for v in (x, tx, T)):
        raise ValueError("Las historias deben ser finitas")
    if np.any(x < 0) or np.any(x != np.floor(x)):
        raise ValueError("x debe contener enteros no negativos")
    if np.any(tx < 0) or np.any(tx > T) or np.any(T < 0):
        raise ValueError("Se requiere 0 <= tx <= T")
    if np.any((x == 0) & (tx != 0)):
        raise ValueError("Con x = 0 se requiere tx = 0")
    return x, tx, T


def ajustar_bgnbd(x, tx, T, inicios=None, loglik=None, *, devolver_diagnostico=False):
    """Estimador de máxima verosimilitud de (r, alpha, a, b).

    Minimiza -LL/n sobre los log-parámetros con Nelder–Mead y con L-BFGS-B
    (cotas [-10, 10]) desde cada arranque LOGARÍTMICO de `inicios` y elige la mejor
    solución exitosa y finita. Dividir entre n no cambia el óptimo y deja la función en una escala
    cómoda para las tolerancias del optimizador. Si algún parámetro termina en la
    cota emite una advertencia, porque entonces el máximo no es interior.

    Devuelve {"r", "alpha", "a", "b", "ll"} con ll en la escala original (suma).
    `loglik` permite ajustar otra verosimilitud con la misma firma (el MBG/NBD).

    Con ``devolver_diagnostico=True`` devuelve (estimados, diagnostico); el valor
    predeterminado conserva el diccionario numérico de los consumidores existentes.
    Convergencia y cota se registran por separado. Una cota no se oculta ni implica
    por sí sola fallo del optimizador. Si un intento rechazado mejora -LL/n en más
    de 1e-7, se prueban ambos métodos una vez desde ese punto. Si la discrepancia
    persiste, o ningún intento es utilizable, lanza ErrorAjuste con el diagnóstico.
    """
    x, tx, T = _validar_historias(x, tx, T)
    n = x.size
    inicios = np.asarray(_inicios_por_defecto() if inicios is None else inicios, dtype=float)
    if (inicios.ndim != 2 or inicios.shape[1] != 4 or len(inicios) == 0
            or not np.isfinite(inicios).all() or np.any(np.abs(inicios) > COTA_LOG)):
        raise ValueError("inicios debe tener forma (n_inicios, 4), finita y dentro de las cotas log")
    loglik = loglik_bgnbd if loglik is None else loglik
    cotas = [(-COTA_LOG, COTA_LOG)] * 4
    tolerancia = 1e-7  # diferencia material por cliente, no en parámetros
    metodos = (
        ("Nelder-Mead", {"maxiter": 20_000, "xatol": 1e-8, "fatol": 1e-10}),
        ("L-BFGS-B", {"maxiter": 20_000, "ftol": 1e-12, "gtol": 1e-8}),
    )
    diagnostico = {
        "aceptado": False, "intentos": [], "seleccionado": None,
        "n_clientes": int(n), "objetivo": "-LL/n", "cotas_log": [-COTA_LOG, COTA_LOG],
        "tolerancia_objetivo": tolerancia, "opciones": dict(metodos),
        "reintentos_discrepancia": 0,
    }
    candidatos = []

    def objetivo(log_params):
        valor = -loglik(log_params, x, tx, T) / n
        return valor if np.isfinite(valor) else np.inf

    def intentar(inicio, indice_inicio, fase):
        for metodo, opciones in metodos:
            intento = {
                "id": len(diagnostico["intentos"]), "indice_inicio": indice_inicio,
                "fase": fase, "inicio_log": np.asarray(inicio).tolist(), "metodo": metodo,
                "success": False, "status": None, "message": "", "objetivo": None,
                "objetivo_optimizador": None, "log_params": None, "nit": None,
                "nfev": None, "njev": None, "en_cota": [], "utilizable": False,
            }
            try:
                res = minimize(objetivo, inicio.copy(), method=metodo, bounds=cotas, options=opciones)
                lp = np.asarray(res.x, dtype=float)
                punto_valido = (lp.shape == (4,) and np.isfinite(lp).all()
                                and np.all(np.abs(lp) <= COTA_LOG + 1e-8))
                valor = objetivo(lp) if punto_valido else np.inf
                intento.update({
                    "success": bool(res.success), "status": int(res.status), "message": str(res.message),
                    "objetivo": float(valor) if np.isfinite(valor) else None,
                    "objetivo_optimizador": float(res.fun) if np.isfinite(res.fun) else None,
                    "log_params": lp.tolist() if punto_valido else None,
                    "en_cota": [k for k, v in zip(NOMBRES, lp) if abs(v) >= COTA_LOG - 1e-3]
                    if punto_valido else [],
                })
                for clave in ("nit", "nfev", "njev"):
                    if getattr(res, clave, None) is not None:
                        intento[clave] = int(getattr(res, clave))
                intento["utilizable"] = bool(res.success and punto_valido
                                             and np.isfinite(valor) and np.isfinite(res.fun))
                if punto_valido and np.isfinite(valor):
                    candidatos.append((intento, float(valor), lp.copy()))
            except (ValueError, RuntimeError, FloatingPointError) as exc:
                intento["message"] = f"{type(exc).__name__}: {exc}"
            diagnostico["intentos"].append(intento)

    for indice, inicio in enumerate(inicios):
        intentar(inicio, indice, "inicial")

    def seleccionar():
        validos = [c for c in candidatos if c[0]["utilizable"]]
        return min(validos, key=lambda c: c[1]) if validos else None

    mejor = seleccionar()
    rechazados = [c for c in candidatos if not c[0]["utilizable"]]
    rechazado = min(rechazados, key=lambda c: c[1]) if rechazados else None
    if mejor is not None and rechazado is not None and rechazado[1] < mejor[1] - tolerancia:
        diagnostico["reintentos_discrepancia"] = 1
        intentar(rechazado[2], rechazado[0]["indice_inicio"], "recuperacion_discrepancia")
        mejor = seleccionar()
    rechazados = [c for c in candidatos if not c[0]["utilizable"]]
    discrepancia = (mejor is not None and any(c[1] < mejor[1] - tolerancia for c in rechazados))
    if mejor is None or discrepancia:
        mensaje = ("Ningún intento convergió a un resultado finito" if mejor is None
                   else "Un intento rechazado conserva una mejora material del objetivo")
        diagnostico["motivo_rechazo"] = mensaje
        raise ErrorAjuste(mensaje, diagnostico)

    intento, valor, log_estimados = mejor
    objetivos = [c[1] for c in candidatos if c[0]["utilizable"]]
    rango = float((max(objetivos) - min(objetivos)) * n)
    diagnostico.update({
        "aceptado": True, "seleccionado": intento["id"], "en_cota": intento["en_cota"],
        "rango_ll_exitosos": rango, "acuerdo_ll_exitosos": rango <= tolerancia * n,
        "n_exitosos": len(objetivos),
    })
    if intento["en_cota"]:
        warnings.warn(f"Parámetros en la cota de búsqueda: {intento['en_cota']}", RuntimeWarning)
    estimados = {k: float(v) for k, v in zip(NOMBRES, np.exp(log_estimados))}
    estimados["ll"] = float(-valor * n)
    return (estimados, diagnostico) if devolver_diagnostico else estimados


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
