"""Pruebas de la preparación de Online Retail (Parte 5). Autor: Jorge Ferguson; asistidas por Codex (OpenAI)."""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from limpieza_retail import limpiar, netear_por_dia, historias_retail, FIN_CALIB_RETAIL, FIN_HOLDOUT_RETAIL
from pronostico_retail import tablas_holdout


def lineas(filas):
    return pd.DataFrame(filas, columns=["CustomerID", "InvoiceDate", "Quantity", "UnitPrice", "InvoiceNo"])


class LimpiezaRetailTest(unittest.TestCase):
    def test_netea_antes_de_filtrar_y_no_deduplica(self):
        df = lineas([
            (1, "2011-06-01 12:00", 1, .1, "A"),
            (1, "2011-06-01 12:00", 1, .1, "A"),
            (1, "2011-06-01 14:00", -1, .2, "CA"),
            (2, "2011-06-01 12:00", 2, 1., "B"),
            (2, "2011-06-01 17:00", -1, 1., "CB"),
            (3, "2011-06-01 12:00", 1, 1., "D"),
            (3, "2011-06-01 17:00", -2, 1., "CD"),
        ])
        copia = df.copy(deep=True)
        trans, dias, audit = netear_por_dia(df, devolver_auditoria=True)
        self.assertEqual(trans.cliente.tolist(), ["2"])
        self.assertEqual(dias.set_index("cliente").venta_neta_exacta.to_dict(), {"1": "0", "2": "1", "3": "-1"})
        self.assertEqual(trans.iloc[0].lineas, 2)
        self.assertEqual(audit["dias_neto_cero"], 1)
        self.assertEqual(audit["dias_neto_negativo"], 1)
        self.assertEqual(audit["filas_duplicadas_exactas_originales"], 1)
        self.assertEqual(audit["filas_originales"], 7)
        self.assertEqual(audit["facturas_unicas_originales"], 6)
        self.assertEqual(audit["filas_cancelacion_conservadas"], 3)
        pd.testing.assert_frame_equal(df, copia)

    def test_decimal_exacto_sin_epsilon_ni_redondeo_centavos(self):
        df = lineas([(1, "2011-06-01", 1, .1, "A"),
                     (1, "2011-06-01", 1, .2, "B"),
                     (1, "2011-06-01", -1, .3, "C"),
                     (2, "2011-06-01", 1, 1e-12, "D")])
        trans, dias, _ = netear_por_dia(df, devolver_auditoria=True)
        self.assertEqual(trans.cliente.tolist(), ["2"])
        self.assertEqual(trans.venta_neta_exacta.iloc[0], "0.000000000001")
        self.assertEqual(dias.set_index("cliente").venta_neta_exacta["1"], "0")

    def test_importe_negativo_y_cancelacion_no_se_filtran(self):
        df = lineas([(1, "2011-06-01", 2, 3, "A"),
                     (1, "2011-06-01", 1, -2, "C1"),
                     (1, "2011-06-01", -1, 1, "C2")])
        trans = netear_por_dia(df)
        self.assertEqual(trans.venta_neta_exacta.iloc[0], "3")
        self.assertEqual(trans.lineas.iloc[0], 3)

    def test_id_ausente_y_campos_irrelevantes(self):
        df = lineas([(np.nan, "2011-06-01", 1, 1, "A"),
                     (1., "2011-06-01", 1, 1, "B"),
                     ("1.0", "2011-06-01", 1, 1, "D")])
        df["Description"] = None
        df["Country"] = "otro país"
        trans, _, audit = netear_por_dia(df, devolver_auditoria=True)
        self.assertEqual(trans.cliente.tolist(), ["1"])
        self.assertEqual(trans.venta_neta_exacta.iloc[0], "2")
        self.assertEqual(audit["filas_sin_customerid"], 1)

    def test_malformados_no_se_descartan_silenciosamente(self):
        base = lineas([(1, "2011-06-01", 1, 1, "A")])
        for columna, valor in [("InvoiceDate", "fecha incorrecta"), ("Quantity", np.nan),
                               ("UnitPrice", np.inf), ("CustomerID", 1.5)]:
            df = base.copy()
            df[columna] = valor
            with self.subTest(columna=columna), self.assertRaises(ValueError):
                netear_por_dia(df)
        with self.assertRaisesRegex(ValueError, "Columnas requeridas"):
            netear_por_dia(base.drop(columns="UnitPrice"))


class LimpiarTarea3Test(unittest.TestCase):
    def test_reglas_de_la_tarea(self):
        df = pd.DataFrame({
            "InvoiceNo": ["1", "1", "A2", "3", "C4", "5", "6"],
            "StockCode": ["X", "X", "X", "X", "X", "POST", "X"],
            "Quantity": [1, 1, 1, -1, -1, 1, 1],
            "UnitPrice": [1., 1., 1., 1., 1., 1., 0.],
        })
        # se van: duplicado, factura A, POST, precio 0 y negativa sin C; queda la cancelación
        self.assertEqual(limpiar(df).index.tolist(), [0, 4])


class HistoriasRetailTest(unittest.TestCase):
    def setUp(self):
        self.trans = netear_por_dia(lineas([
            (1, "2011-06-30 23:59:59", 1, 1, "A"),
            (1, "2011-07-01 22:00", 1, 1, "B"),
            (1, "2011-12-08 23:59:59", 1, 1, "C"),
            (1, "2011-12-09 12:00", 1, 1, "D"),
            (2, "2011-06-15", -1, 1, "CE"),
            (2, "2011-07-01", 1, 1, "F"),
            (3, "2010-12-01 23:00", 1, 1, "G"),
            (4, "2011-07-01", 1, 1, "H"),
            (5, "2011-06-30", 1, 1, "I"),
            (5, "2011-06-30", -1, 1, "CI"),
            (5, "2011-12-08", 1, 1, "J"),
            (6, "2011-01-01", -1, 1, "CK"),
            (6, "2011-06-01", 1, 1, "L"),
            (6, "2011-06-30", 1, 1, "M"),
            (6, "2011-12-08", 1, 1, "N"),
            (7, "2011-12-09", 1, 1, "O"),
        ]))
        self.res = historias_retail(self.trans).set_index("cliente")

    def test_cohorte_solo_calibracion_y_ceros_holdout(self):
        self.assertEqual(set(self.res.index), {"1", "3", "6"})
        self.assertEqual(self.res.x_star.to_dict(), {"1": 2, "3": 0, "6": 1})
        self.assertEqual(self.res.x.to_dict(), {"1": 0, "3": 0, "6": 1})
        self.assertEqual(self.res.loc["6", "adquisicion"], pd.Timestamp("2011-06-01"))

    def test_limites_unidades_y_adquisicion(self):
        self.assertEqual((FIN_HOLDOUT_RETAIL - FIN_CALIB_RETAIL).days / 7, 23)
        self.assertEqual(self.res.loc["1", "T"], 0)
        self.assertEqual(self.res.loc["1", "tx"], 0)
        self.assertAlmostEqual(self.res.loc["6", "T"], 29 / 7)
        self.assertAlmostEqual(self.res.loc["6", "tx"], 29 / 7)
        self.assertAlmostEqual(self.res.loc["3", "T"], 211 / 7)
        self.assertTrue(self.res.index.is_unique)
        self.assertTrue(np.isfinite(self.res[["x", "tx", "T", "x_star"]]).all().all())

    def test_no_admite_dias_repetidos_ni_horas(self):
        with self.assertRaisesRegex(ValueError, "una fila"):
            historias_retail(pd.concat([self.trans, self.trans.iloc[:1]]))
        mal = self.trans.copy()
        mal.loc[0, "fecha"] += pd.Timedelta(hours=1)
        with self.assertRaisesRegex(ValueError, "normalizadas"):
            historias_retail(mal)

    def test_tablas_pronostico_intervalos_y_totales(self):
        params = {"r": .74, "alpha": 9.14, "a": .0000454, "b": 22019.8}
        diario, semanal, mensual = tablas_holdout(self.trans, self.res.reset_index(), params)
        self.assertEqual(len(diario), 161)
        self.assertEqual(len(semanal), 23)
        self.assertTrue((semanal.dias == 7).all())
        self.assertEqual(semanal.fecha_inicio.iloc[0], pd.Timestamp("2011-07-01"))
        self.assertEqual(semanal.fecha_fin.iloc[-1], pd.Timestamp("2011-12-08"))
        self.assertEqual(diario.real.sum(), 3)
        self.assertEqual(diario[diario.fecha.eq("2011-12-08")].real.iloc[0], 2)
        self.assertEqual(mensual.dias.tolist(), [31, 31, 30, 31, 30, 8])
        self.assertAlmostEqual(diario.pronostico.sum(), semanal.pronostico.sum(), places=10)
        self.assertAlmostEqual(mensual.pronostico.sum(), diario.pronostico_acumulado.iloc[-1], places=10)
        self.assertTrue((diario.pronostico >= 0).all())


if __name__ == "__main__":
    unittest.main()
