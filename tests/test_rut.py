import unittest

from datosdemocl.rut import (
    CUERPO_MAXIMO,
    RutChecksumError,
    RutFormatError,
    calcular_dv,
    formatear_cuerpo,
    normalizar,
    validar,
    validar_o_error,
)


class CalcularDvTests(unittest.TestCase):
    def test_casos_conocidos(self):
        self.assertEqual(calcular_dv(1), "9")
        self.assertEqual(calcular_dv(6), "K")
        self.assertEqual(calcular_dv(14), "0")
        self.assertEqual(calcular_dv(12345678), "5")

    def test_acepta_cuerpo_como_texto(self):
        self.assertEqual(calcular_dv("12345678"), "5")
        self.assertEqual(calcular_dv("0000012345678"), "5")

    def test_rechaza_cuerpos_invalidos(self):
        for valor in (0, -1, 100_000_000, "abc", "12a", 1.5, True):
            with self.subTest(valor=valor):
                with self.assertRaises(RutFormatError):
                    calcular_dv(valor)

    def test_limite_superior(self):
        self.assertIn(calcular_dv(CUERPO_MAXIMO), "0123456789K")


class NormalizarTests(unittest.TestCase):
    def test_formatos_equivalentes(self):
        esperado = "12.345.678-5"
        for entrada in (
            "12.345.678-5",
            "12345678-5",
            "123456785",
            " 12.345.678-5 ",
            "12.345.678 - 5",
            "012345678-5",
        ):
            with self.subTest(entrada=entrada):
                self.assertEqual(normalizar(entrada), esperado)

    def test_k_minuscula(self):
        self.assertEqual(normalizar("6-k"), "6-K")
        self.assertEqual(normalizar("6K"), "6-K")

    def test_cuerpo_corto(self):
        self.assertEqual(normalizar("1-9"), "1-9")

    def test_no_valida_checksum(self):
        # Normalizar sólo ordena el formato; la validez se comprueba aparte.
        self.assertEqual(normalizar("12.345.678-4"), "12.345.678-4")

    def test_errores_de_formato(self):
        for entrada in (
            "",
            "   ",
            "5",
            "abc-5",
            "12.345.678-X",
            "12.345.678-55",
            "0-0",
            "000-0",
            "100.000.000-1",
        ):
            with self.subTest(entrada=entrada):
                with self.assertRaises(RutFormatError):
                    normalizar(entrada)

    def test_rechaza_no_texto(self):
        for valor in (None, 12345678, 12.5, True):
            with self.subTest(valor=valor):
                with self.assertRaises(RutFormatError):
                    normalizar(valor)


class ValidarTests(unittest.TestCase):
    def test_ruts_validos(self):
        for entrada in ("1-9", "6-K", "6-k", "14-0", "12.345.678-5", "123456785"):
            with self.subTest(entrada=entrada):
                self.assertTrue(validar(entrada))
                self.assertTrue(validar_o_error(entrada))

    def test_checksum_incorrecto(self):
        with self.assertRaises(RutChecksumError) as contexto:
            validar_o_error("12.345.678-4")
        self.assertIn("se esperaba 5", str(contexto.exception))
        self.assertFalse(validar("12.345.678-4"))

    def test_dv_k_incorrecto(self):
        self.assertFalse(validar("6-9"))
        with self.assertRaises(RutChecksumError):
            validar_o_error("6-9")

    def test_entradas_invalidas_no_lanzan_en_validar(self):
        for entrada in ("", "abc", None, "12.345.678-55", 123):
            with self.subTest(entrada=entrada):
                self.assertFalse(validar(entrada))

    def test_devuelve_forma_canonica(self):
        self.assertEqual(validar_o_error("123456785"), "12.345.678-5")
        self.assertEqual(validar_o_error(" 6 k "), "6-K")


class FormatearCuerpoTests(unittest.TestCase):
    def test_puntos_de_miles(self):
        self.assertEqual(formatear_cuerpo(1), "1")
        self.assertEqual(formatear_cuerpo(12345678), "12.345.678")

    def test_limites(self):
        with self.assertRaises(RutFormatError):
            formatear_cuerpo(0)
        with self.assertRaises(RutFormatError):
            formatear_cuerpo(100_000_000)


if __name__ == "__main__":
    unittest.main()
