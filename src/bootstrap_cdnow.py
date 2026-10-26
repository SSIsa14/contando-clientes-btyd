"""Bootstrap por filas de clientes (Parte 2.3), sin duplicar el optimizador.

Responsabilidad de la sección: Jorge Ferguson. Implementación asistida por Codex
(OpenAI); revisión humana pendiente. El muestreo y los reintentos usan RNG separados.
"""
import hashlib
import warnings

import numpy as np
import pandas as pd

from bgnbd import (NOMBRES, PARAMS_ARTICULO, COTA_LOG, ErrorAjuste,
                   _validar_historias, ajustar_bgnbd)


def bootstrap_clientes(x, tx, T, params, B=200, semilla=14045,
                       semilla_reintentos=271828, progreso=None):
    """Devuelve (tabla, diagnósticos) conservando fallos y multiplicidad.

    Por réplica se permite un máximo de tres llamadas al ajustador compartido:
    0: estimado completo; 1: estimado, unos y artículo; 2: estimado y dos
    perturbaciones logarítmicas (DE .35 y .8). Una llamada aceptada termina los
    reintentos. La recuperación interna de discrepancias del ajustador se registra
    aparte. Nunca se redibuja una muestra fallida. Las filas rechazadas conservan
    aceptada=False y parámetros ausentes, sin entrar silenciosamente en las DE.

    Los índices son posiciones en los vectores originales; su SHA-256 se calcula
    como enteros int64 little-endian. default_rng(semilla).integers(0,n,n) reproduce
    cada muestra, sin consumir ese generador en el ajuste ni en los reintentos.
    """
    x, tx, T = _validar_historias(x, tx, T)
    if not isinstance(B, (int, np.integer)) or B < 1:
        raise ValueError("B debe ser un entero positivo")
    base = np.array([params[k] for k in NOMBRES], dtype=float)
    if not np.isfinite(base).all() or np.any(base <= 0):
        raise ValueError("El arranque completo debe ser positivo y finito")
    base = np.log(base)
    if np.any(np.abs(base) > COTA_LOG):
        raise ValueError("El arranque completo debe estar dentro de las cotas")
    rng = np.random.default_rng(semilla)
    filas, registros = [], []
    for replica in range(1, B + 1):
        indices = rng.integers(0, x.size, size=x.size, dtype=np.int64)
        _, multiplicidad = np.unique(indices, return_counts=True)
        huella = hashlib.sha256(indices.astype("<i8").tobytes()).hexdigest()
        fila = {"replica": replica, "aceptada": False, "ll": np.nan,
                **{k: np.nan for k in NOMBRES}, "en_cota": False,
                "parametros_en_cota": "", "reintentos": 0, "n_intentos": 0,
                "reintentos_discrepancia": 0, "n_clientes": int(x.size),
                "n_clientes_distintos": int(multiplicidad.size),
                "multiplicidad_maxima": int(multiplicidad.max()),
                "indices_sha256": huella, "metodo_seleccionado": ""}
        registro = {"replica": replica, "indices_sha256": huella, "ajustes": []}
        rng_retry = np.random.default_rng(np.random.SeedSequence([semilla_reintentos, replica]))
        for vuelta in range(3):
            if vuelta == 0:
                inicios = [base.copy()]
            elif vuelta == 1:
                inicios = [base.copy(), np.zeros(4), np.log([PARAMS_ARTICULO[k] for k in NOMBRES])]
            else:
                inicios = [base.copy()] + [np.clip(base + rng_retry.normal(0, de, 4),
                                                  -COTA_LOG, COTA_LOG) for de in (.35, .8)]
            with warnings.catch_warnings(record=True) as avisos:
                warnings.simplefilter("always")
                try:
                    est, diag = ajustar_bgnbd(x[indices], tx[indices], T[indices],
                                             inicios=inicios, devolver_diagnostico=True)
                except ErrorAjuste as exc:
                    diag = exc.diagnostico
                    est = None
            registro["ajustes"].append({"numero": vuelta, "diagnostico": diag,
                                        "avisos": [str(a.message) for a in avisos]})
            fila["reintentos"] = vuelta
            fila["n_intentos"] += len(diag["intentos"])
            fila["reintentos_discrepancia"] += diag["reintentos_discrepancia"]
            if est is not None:
                fila.update(est)
                fila.update({"aceptada": True, "en_cota": bool(diag["en_cota"]),
                             "parametros_en_cota": ",".join(diag["en_cota"]),
                             "metodo_seleccionado": diag["intentos"][diag["seleccionado"]]["metodo"]})
                break
        registro["aceptada"] = fila["aceptada"]
        filas.append(fila)
        registros.append(registro)
        if progreso is not None:
            progreso(replica, B, fila)
    return pd.DataFrame(filas), registros
