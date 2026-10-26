"""Pruebas de riesgos del ajuste compartido; elaboradas con asistencia de Codex."""
import sys
import unittest
import warnings
from pathlib import Path
from unittest.mock import patch

import numpy as np
from scipy.optimize import OptimizeResult
from lifetimes import BetaGeoFitter, ModifiedBetaGeoFitter

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from bgnbd import ajustar_bgnbd, ErrorAjuste, loglik_bgnbd, NOMBRES
from datos import cargar_cdnow, resumen_clientes
from mbgnbd import ajustar_mbgnbd, esperado_Y_mbgnbd, loglik_mbgnbd


def cuadratica(lp, x, tx, T):
    return -len(x) * np.square(lp).sum()


def resultado(lp, exito=True):
    lp = np.asarray(lp, dtype=float)
    return OptimizeResult(x=lp, fun=np.square(lp).sum(), success=exito,
                          status=0 if exito else 2, message="prueba controlada",
                          nit=3, nfev=8)


class DiagnosticoTest(unittest.TestCase):
    def ajustar(self, **kwargs):
        return ajustar_bgnbd([0, 1], [0, 1], [2, 2], inicios=[np.zeros(4)],
                             loglik=cuadratica, devolver_diagnostico=True, **kwargs)

    def test_todos_fallan_conserva_intentos(self):
        with patch("bgnbd.minimize", return_value=resultado(np.zeros(4), False)):
            with self.assertRaises(ErrorAjuste) as cm:
                self.ajustar()
        d = cm.exception.diagnostico
        self.assertFalse(d["aceptado"])
        self.assertEqual(len(d["intentos"]), 2)
        self.assertTrue(all(not a["success"] for a in d["intentos"]))

    def test_no_finito_no_es_utilizable_aunque_success(self):
        falso = resultado(np.zeros(4))
        falso.fun = np.nan
        with patch("bgnbd.minimize", return_value=falso):
            with self.assertRaises(ErrorAjuste):
                self.ajustar()

    def test_seleccion_por_objetivo_y_diagnosticos(self):
        with patch("bgnbd.minimize", side_effect=[resultado(np.ones(4)), resultado(np.zeros(4))]):
            est, d = self.ajustar()
        self.assertEqual(d["seleccionado"], 1)
        self.assertEqual(est["ll"], 0)
        self.assertAlmostEqual(d["rango_ll_exitosos"], 8)
        self.assertFalse(d["acuerdo_ll_exitosos"])
        self.assertEqual(d["intentos"][1]["nfev"], 8)

    def test_rechazado_mejor_se_reintenta_en_el_mismo_punto(self):
        with patch("bgnbd.minimize", side_effect=[resultado(np.ones(4)),
                   resultado(np.zeros(4), False), resultado(np.zeros(4)),
                   resultado(np.zeros(4))]) as opt:
            est, d = self.ajustar()
        self.assertEqual(est["ll"], 0)
        self.assertEqual(d["reintentos_discrepancia"], 1)
        self.assertEqual(len(d["intentos"]), 4)
        self.assertFalse(d["intentos"][1]["utilizable"])
        np.testing.assert_array_equal(opt.call_args_list[2].args[1], np.zeros(4))

    def test_discrepancia_persistente_rechaza(self):
        with patch("bgnbd.minimize", side_effect=[resultado(np.ones(4)),
                   resultado(np.zeros(4), False), resultado(np.ones(4)), resultado(np.ones(4))]):
            with self.assertRaisesRegex(ErrorAjuste, "mejora material") as cm:
                self.ajustar()
        self.assertEqual(cm.exception.diagnostico["reintentos_discrepancia"], 1)

    def test_cota_y_convergencia_son_distintas(self):
        with patch("bgnbd.minimize", return_value=resultado([10, 0, 0, 0])):
            with self.assertWarns(RuntimeWarning):
                _, d = self.ajustar()
        self.assertTrue(d["aceptado"])
        self.assertEqual(d["en_cota"], ["r"])

    def test_invariantes(self):
        for args in [([], [], []), ([0], [1], [2]), ([1.5], [1], [2]),
                     ([1], [3], [2]), ([0], [0], [np.nan]), ([[1]], [[1]], [[2]])]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                ajustar_bgnbd(*args)
        for inicios in [np.zeros(4), [], [[0, 0, 0]], [[0, 0, np.inf, 0]], [[11, 0, 0, 0]]]:
            with self.subTest(inicios=inicios), self.assertRaises(ValueError):
                ajustar_bgnbd([0], [0], [1], inicios=inicios)

    def test_callback_personalizado_real(self):
        objetivo = np.log([0.5, 5, 0.8, 3])
        def otra_ll(lp, x, tx, T):
            return -len(x) * np.square(lp - objetivo).sum()
        est = ajustar_bgnbd([0, 1], [0, 1], [2, 2], loglik=otra_ll)
        np.testing.assert_allclose([est[k] for k in NOMBRES], np.exp(objetivo), rtol=1e-6)
        self.assertGreater(est["ll"], -1e-10)


class RegresionCDNOWTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        trans = cargar_cdnow(RAIZ / "data/CDNOW_sample.txt")
        cls.res = resumen_clientes(trans, "1997-09-30", "1998-06-30")
        cls.x, cls.tx, cls.T = (cls.res[k].to_numpy() for k in ("x", "tx", "T"))

    def test_bgnbd_ll_y_ajuste_vs_lifetimes(self):
        self.assertEqual(len(self.x), 2357)
        self.assertEqual((self.x == 0).sum(), 1411)
        self.assertAlmostEqual(loglik_bgnbd(np.zeros(4), self.x, self.tx, self.T), -13887.7, delta=.05)
        est, d = ajustar_bgnbd(self.x, self.tx, self.T, devolver_diagnostico=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            ref = BetaGeoFitter(penalizer_coef=0.0).fit(self.x, self.tx, self.T)
        self.assertAlmostEqual(est["ll"], -9582.4292, delta=5e-4)
        np.testing.assert_allclose([est[k] for k in NOMBRES], ref.params_[list(NOMBRES)], rtol=2e-4, atol=2e-5)
        self.assertAlmostEqual(est["ll"], loglik_bgnbd(np.log(ref.params_[list(NOMBRES)]), self.x, self.tx, self.T), delta=1e-5)
        self.assertFalse(d["en_cota"])
        self.assertTrue(d["acuerdo_ll_exitosos"])
        self.assertEqual(set(ajustar_bgnbd(self.x, self.tx, self.T)), {*NOMBRES, "ll"})

    def test_mbgnbd_callback_y_pronostico_vs_lifetimes(self):
        est = ajustar_mbgnbd(self.x, self.tx, self.T)
        self.assertAlmostEqual(est["ll"], -9582.1357, delta=5e-4)
        self.assertAlmostEqual(est["ll"], loglik_mbgnbd(np.log([est[k] for k in NOMBRES]), self.x, self.tx, self.T), places=8)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            ref = ModifiedBetaGeoFitter(penalizer_coef=0.0).fit(self.x, self.tx, self.T)
        np.testing.assert_allclose([est[k] for k in NOMBRES], ref.params_[list(NOMBRES)], rtol=3e-4, atol=3e-5)
        np.testing.assert_allclose(esperado_Y_mbgnbd(39, self.x, self.tx, self.T, est),
                                  ref.conditional_expected_number_of_purchases_up_to_time(39, self.x, self.tx, self.T),
                                  rtol=3e-4, atol=3e-5)


if __name__ == "__main__":
    unittest.main()
