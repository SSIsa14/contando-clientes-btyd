"""Pruebas del bootstrap 2.3: muestreo, multiplicidad y fallos. Autor: Jorge Ferguson; asistidas por Codex (OpenAI)."""
import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bgnbd import ErrorAjuste
from bootstrap_cdnow import bootstrap_clientes


class BootstrapTest(unittest.TestCase):
    params = {"r": .25, "alpha": 4., "a": .8, "b": 2.5}
    x = np.array([0, 1, 2, 3])
    tx = np.array([0., 1., 2., 3.])
    T = np.array([4., 5., 6., 7.])

    def exito(self):
        return ({**self.params, "ll": -4.}, {"aceptado": True, "en_cota": [],
                 "intentos": [{"metodo": "prueba"}], "seleccionado": 0,
                 "reintentos_discrepancia": 0})

    def fallo(self):
        return ErrorAjuste("fallo controlado", {"aceptado": False, "intentos": [],
                                                "reintentos_discrepancia": 0})

    def test_multiplicidad_arranque_y_reproduccion(self):
        with patch("bootstrap_cdnow.ajustar_bgnbd", return_value=self.exito()) as fit:
            tabla, _ = bootstrap_clientes(self.x, self.tx, self.T, self.params, B=2)
        rng = np.random.default_rng(14045)
        for i, call in enumerate(fit.call_args_list):
            idx = rng.integers(0, 4, size=4, dtype=np.int64)
            np.testing.assert_array_equal(call.args[0], self.x[idx])
            self.assertEqual(len(call.args[0]), 4)
            self.assertEqual(tabla.iloc[i]["n_clientes_distintos"], len(np.unique(idx)))
            self.assertEqual(tabla.iloc[i]["indices_sha256"], hashlib.sha256(idx.astype("<i8").tobytes()).hexdigest())
            np.testing.assert_allclose(call.kwargs["inicios"][0], np.log(list(self.params.values())))
        self.assertTrue((tabla.multiplicidad_maxima > 1).any())

    def test_reintento_no_redibuja_ni_cambia_siguiente_muestra(self):
        with patch("bootstrap_cdnow.ajustar_bgnbd", side_effect=[self.fallo(), self.exito(), self.exito()]) as fit:
            tabla, diags = bootstrap_clientes(self.x, self.tx, self.T, self.params, B=2)
        for a, b in zip(fit.call_args_list[0].args, fit.call_args_list[1].args):
            np.testing.assert_array_equal(a, b)
        rng = np.random.default_rng(14045)
        rng.integers(0, 4, size=4, dtype=np.int64)
        idx2 = rng.integers(0, 4, size=4, dtype=np.int64)
        np.testing.assert_array_equal(fit.call_args_list[2].args[0], self.x[idx2])
        self.assertEqual(tabla.reintentos.tolist(), [1, 0])
        self.assertFalse(diags[0]["ajustes"][0]["diagnostico"]["aceptado"])

    def test_fallos_sin_ocultar_y_reintentos_acotados(self):
        with patch("bootstrap_cdnow.ajustar_bgnbd", side_effect=self.fallo()) as fit:
            tabla, diags = bootstrap_clientes(self.x, self.tx, self.T, self.params, B=2)
        self.assertEqual(fit.call_count, 6)
        self.assertEqual(len(tabla), 2)
        self.assertFalse(tabla.aceptada.any())
        self.assertTrue(tabla[["r", "alpha", "a", "b"]].isna().all().all())
        self.assertTrue(all(len(d["ajustes"]) == 3 for d in diags))


if __name__ == "__main__":
    unittest.main()
