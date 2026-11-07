"""Pruebas del contrato de columnas disponible."""

import unittest

from datosdemocl.generator import CAMPOS
from datosdemocl.schema import (
    CAMPOS_DISPONIBLES,
    CAMPOS_POR_DEFECTO,
    CAMPOS_TRANSACCION,
    ETIQUETAS,
    ETIQUETAS_PRESETS,
    PRESETS,
    campos_de_preset,
    normalizar_campos,
)


class EsquemaTests(unittest.TestCase):
    def test_columnas_por_defecto(self):
        self.assertEqual(
            CAMPOS_POR_DEFECTO,
            (
                "id_prueba",
                "nombre",
                "apellido",
                "rut",
                "correo",
                "region",
                "comuna",
                "fecha_registro",
                "monto_clp",
            ),
        )
        self.assertEqual(CAMPOS, CAMPOS_POR_DEFECTO)

    def test_columnas_disponibles_sin_duplicados(self):
        self.assertEqual(
            len(CAMPOS_DISPONIBLES), len(set(CAMPOS_DISPONIBLES))
        )
        self.assertEqual(len(CAMPOS_DISPONIBLES), 44)
        for campo in CAMPOS_POR_DEFECTO:
            self.assertIn(campo, CAMPOS_DISPONIBLES)

    def test_columnas_de_transaccion(self):
        self.assertEqual(len(CAMPOS_TRANSACCION), 12)
        self.assertEqual(CAMPOS_DISPONIBLES[15:27], CAMPOS_TRANSACCION)
        for campo in CAMPOS_TRANSACCION:
            self.assertIn(campo, CAMPOS_DISPONIBLES)

    def test_presets(self):
        self.assertEqual(
            set(PRESETS),
            {"base", "sabana_ventas", "transacciones", "clientes", "comercio_demo", "completo"},
        )
        self.assertEqual(PRESETS["base"], CAMPOS_POR_DEFECTO)
        self.assertEqual(PRESETS["transacciones"], CAMPOS_TRANSACCION)
        self.assertEqual(PRESETS["completo"], CAMPOS_DISPONIBLES)
        self.assertEqual(len(PRESETS["base"]), 9)
        self.assertEqual(len(PRESETS["transacciones"]), 12)
        self.assertEqual(len(PRESETS["sabana_ventas"]), 10)
        self.assertEqual(len(PRESETS["clientes"]), 11)
        self.assertEqual(len(PRESETS["comercio_demo"]), 29)
        self.assertEqual(len(PRESETS["completo"]), 44)
        self.assertEqual(set(ETIQUETAS_PRESETS), set(PRESETS))
        for nombre in PRESETS:
            self.assertEqual(campos_de_preset(nombre), PRESETS[nombre])
            self.assertTrue(ETIQUETAS_PRESETS[nombre].strip())
        with self.assertRaises(ValueError):
            campos_de_preset("no_existe")

    def test_todas_las_columnas_tienen_etiqueta(self):
        self.assertEqual(set(ETIQUETAS), set(CAMPOS_DISPONIBLES))
        for etiqueta in ETIQUETAS.values():
            self.assertTrue(etiqueta.strip())

    def test_normaliza_y_conserva_el_orden(self):
        self.assertEqual(
            normalizar_campos((" rut ", "nombre", "estado")),
            ("rut", "nombre", "estado"),
        )
        self.assertEqual(
            normalizar_campos(["monto_clp", "rut"]),
            ("monto_clp", "rut"),
        )

    def test_rechaza_selecciones_invalidas(self):
        for campos in ((), ["no_existe"], ["rut", "rut"], ["rut", ""], [1]):
            with self.subTest(campos=campos):
                with self.assertRaises(ValueError):
                    normalizar_campos(campos)


if __name__ == "__main__":
    unittest.main()
