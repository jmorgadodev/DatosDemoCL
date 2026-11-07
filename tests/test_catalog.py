import unittest

from datosdemocl.catalog import APELLIDOS, NOMBRES, REGIONES


class CatalogosTests(unittest.TestCase):
    def test_listas_no_vacias_y_sin_duplicados(self):
        for lista in (NOMBRES, APELLIDOS):
            with self.subTest(lista=lista):
                self.assertGreater(len(lista), 0)
                self.assertEqual(len(lista), len(set(lista)))
                self.assertTrue(all(isinstance(valor, str) and valor for valor in lista))

    def test_catalogos_incluyen_caracteres_unicode(self):
        self.assertTrue(any("ñ" in apellido for apellido in APELLIDOS))
        self.assertTrue(any("á" in nombre or "é" in nombre for nombre in NOMBRES))

    def test_regiones_y_comunas_coherentes(self):
        self.assertEqual(len(REGIONES), 16)
        nombres_region = [region for region, _ in REGIONES]
        self.assertEqual(len(nombres_region), len(set(nombres_region)))
        for region, comunas in REGIONES:
            with self.subTest(region=region):
                self.assertTrue(region)
                self.assertGreaterEqual(len(comunas), 1)
                self.assertEqual(len(comunas), len(set(comunas)))
                self.assertTrue(all(comuna for comuna in comunas))

    def test_incluye_region_metropolitana_y_biobio(self):
        nombres = {region for region, _ in REGIONES}
        self.assertIn("Metropolitana de Santiago", nombres)
        self.assertIn("Biobío", nombres)


if __name__ == "__main__":
    unittest.main()
