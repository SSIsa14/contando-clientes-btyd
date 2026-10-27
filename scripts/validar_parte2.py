"""Auditoría de artefactos de Parte 2 sin volver a ejecutar los 200 ajustes.

Autor: Jorge Armando Ferguson Yaeggy. Uso de IA: asistencia de Codex (OpenAI). Desde la raíz: python scripts/validar_parte2.py
"""
import hashlib
import json
from pathlib import Path
import sys

import nbformat
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from bgnbd import NOMBRES
from datos import cargar_cdnow, resumen_clientes


def sha(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def leer(nombre):
    def rechazar(valor):
        raise ValueError(f"Constante JSON no finita: {valor}")
    return json.loads((RAIZ / nombre).read_text(encoding="utf-8"), parse_constant=rechazar)


def validar():
    p = leer("resultados/params_cdnow.json")
    pro = leer("resultados/ajuste_cdnow_proveniencia.json")
    b = leer("resultados/bootstrap_cdnow_resumen.json")
    ds = leer("resultados/bootstrap_cdnow_diagnosticos.json")
    assert set(p) == set(NOMBRES)
    assert all(type(v) is float and np.isfinite(v) and v > 0 for v in p.values())
    assert p == pro["parametros"] == b["arranque_parametros"]
    np.testing.assert_array_equal(np.log([p[k] for k in NOMBRES]), b["arranque_log"])
    assert pro["datos"]["sha256"] == b["datos_sha256"] == sha(RAIZ / "data/CDNOW_sample.txt")
    for ruta, valor in pro["codigo_sha256"].items():
        assert sha(RAIZ / ruta) == valor, f"Código cambió después de ejecución: {ruta}"
    assert pro["diagnostico"]["aceptado"] and not pro["diagnostico"]["en_cota"]
    assert abs(pro["verificacion_lifetimes"]["diferencia_ll"]) < 1e-5

    res = resumen_clientes(cargar_cdnow(RAIZ / "data/CDNOW_sample.txt"), "1997-09-30", "1998-06-30")
    historias = res[["x", "tx", "T"]].to_numpy(dtype="<f8")
    assert sha(RAIZ / "resultados/bootstrap_cdnow.csv") == b["replicas_csv_sha256"]
    assert hashlib.sha256(historias.tobytes()).hexdigest() == b["historias_sha256"]
    boot = pd.read_csv(RAIZ / "resultados/bootstrap_cdnow.csv",
                       converters={k: float for k in [*NOMBRES, "ll"]})
    assert len(boot) == b["B"] == b["intentadas"] == b["aceptadas"] == 200
    assert b["no_resueltas"] == 0 and boot.aceptada.all()
    assert len(ds) == 200 and boot.replica.tolist() == list(range(1, 201))
    assert np.isfinite(boot[[*NOMBRES, "ll"]]).all().all()
    assert (boot[list(NOMBRES)] > 0).all().all()
    np.testing.assert_allclose(boot[list(NOMBRES)].std(ddof=1),
                               [b["errores_estandar"][k] for k in NOMBRES], rtol=1e-12)
    rng = np.random.default_rng(b["semilla_muestreo"])
    for fila, diag in zip(boot.itertuples(), ds):
        idx = rng.integers(0, len(res), size=len(res), dtype=np.int64)
        _, mult = np.unique(idx, return_counts=True)
        huella = hashlib.sha256(idx.astype("<i8").tobytes()).hexdigest()
        assert huella == fila.indices_sha256 == diag["indices_sha256"]
        assert fila.replica == diag["replica"] and diag["aceptada"]
        assert fila.n_clientes == mult.sum() == 2357
        assert fila.n_clientes_distintos == len(mult) and fila.multiplicidad_maxima == mult.max()
        assert len(diag["ajustes"]) == fila.reintentos + 1
        primero = diag["ajustes"][0]["diagnostico"]
        np.testing.assert_array_equal(primero["intentos"][0]["inicio_log"], b["arranque_log"])
        elegido = diag["ajustes"][-1]["diagnostico"]
        intento = elegido["intentos"][elegido["seleccionado"]]
        assert elegido["aceptado"] and intento["success"] and intento["utilizable"]
        assert bool(elegido["en_cota"]) == fila.en_cota
        np.testing.assert_allclose([getattr(fila, k) for k in NOMBRES], np.exp(intento["log_params"]), rtol=1e-14)
        np.testing.assert_allclose(fila.ll, -intento["objetivo"] * len(res), rtol=1e-14)
    assert int(boot.en_cota.sum()) == b["en_cota"]
    assert int(boot.reintentos.sum()) == b["reintentos_externos_total"]
    assert int(boot.reintentos_discrepancia.sum()) == b["reintentos_discrepancia_total"]

    ruta_nb = RAIZ / "notebooks/02_ajuste_cdnow.ipynb"
    nb = nbformat.read(ruta_nb, as_version=4)
    nbformat.validate(nb)
    codigo = [c for c in nb.cells if c.cell_type == "code"]
    assert [c.execution_count for c in codigo] == list(range(1, len(codigo) + 1))
    assert not any(o.output_type == "error" for c in codigo for o in c.outputs)
    ajuste = next(c for c in codigo if c.id == "p2-ajuste")
    texto = "".join(o.get("text", "") for o in ajuste.outputs)
    linea = next(l for l in texto.splitlines() if l.startswith("Parámetros completos: "))
    assert json.loads(linea.split(": ", 1)[1]) == p
    assert f"LL sumada: {pro['ll_sumada']!r}" in texto
    for nombre in ["parte2_densidad_lambda.png", "parte2_densidad_p.png", "parte2_bootstrap_parametros.png"]:
        assert (RAIZ / "figs" / nombre).stat().st_size > 10000
    assert sha(RAIZ / b["simulacion_comparacion"]["fuente"]) == b["simulacion_comparacion"]["fuente_sha256"]
    informe = {
        "estado": "completo: auditoría de artefactos aprobada",
        "alcance": "Parte 2",
        "notebook_sha256": sha(ruta_nb), "celdas_codigo_ejecutadas": len(codigo),
        "parametros": p, "ll_sumada": pro["ll_sumada"], "bootstrap_aceptadas": 200,
        "bootstrap_no_resueltas": 0, "bootstrap_en_cota": b["en_cota"],
        "intentos_optimizacion_bootstrap": sum(len(a["diagnostico"]["intentos"]) for d in ds for a in d["ajustes"]),
        "intentos_fallidos_bootstrap": sum(not i["utilizable"] for d in ds for a in d["ajustes"] for i in a["diagnostico"]["intentos"]),
        "verificaciones": ["esquema JSON y finitud", "fuente y código por SHA-256",
            "consistencia parámetros/proveniencia/arranque/salida notebook",
            "200 muestras reproducidas y multiplicidad preservada", "DE ddof=1 desde CSV",
            "selección y contabilidad por réplica", "notebook ejecutado sin errores guardados",
            "figuras presentes; legibilidad inspeccionada por separado"],
    }
    (RAIZ / "resultados/validacion_parte2.json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(informe, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    validar()
