import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from datosdemocl.rut import validar
from datosdemocl.schema import (
    CAMPOS_DISPONIBLES,
    CAMPOS_POR_DEFECTO,
    CAMPOS_TRANSACCION,
)

RAIZ = Path(__file__).resolve().parents[1]


def ejecutar(*argumentos: str) -> subprocess.CompletedProcess:
    entorno = os.environ.copy()
    entorno["PYTHONIOENCODING"] = "utf-8"
    entorno["PYTHONPATH"] = str(RAIZ) + os.pathsep + entorno.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "datosdemocl", *argumentos],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=entorno,
        timeout=120,
    )


class AyudaTests(unittest.TestCase):
    def test_sin_argumentos_muestra_ayuda(self):
        resultado = ejecutar()
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("generar", resultado.stdout)
        self.assertIn("validar-rut", resultado.stdout)
        self.assertIn("gui", resultado.stdout)

    def test_ayuda(self):
        resultado = ejecutar("--help")
        self.assertEqual(resultado.returncode, 0)
        ayuda = ejecutar("generar", "--help").stdout
        self.assertIn("--cantidad", ayuda)
        self.assertIn("--semilla", ayuda)
        for opcion in (
            "--perfil",
            "--campos",
            "--formato-rut",
            "--region",
            "--comuna",
            "--fecha-desde",
            "--fecha-hasta",
            "--monto-min",
            "--monto-max",
            "--monto-paso",
            "--estados-pago",
            "--tipos-cliente",
            "--tipos-documento",
            "--pasarelas",
            "--canales-venta",
            "--dominio-correo",
            "--delimitador",
            "--sin-bom",
        ):
            with self.subTest(opcion=opcion):
                self.assertIn(opcion, ayuda)

    def test_ayuda_gui(self):
        resultado = ejecutar("gui", "--help")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("interfaz", resultado.stdout.lower())

    def test_version(self):
        resultado = ejecutar("--version")
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("datosdemocl 0.8.0", resultado.stdout)


class GenerarTests(unittest.TestCase):
    def setUp(self):
        self._temporal = tempfile.TemporaryDirectory()
        self.carpeta = Path(self._temporal.name)
        self.addCleanup(self._temporal.cleanup)

    def test_genera_csv_valido(self):
        destino = self.carpeta / "lote.csv"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "25",
            "--formato",
            "csv",
            "--salida",
            str(destino),
            "--semilla",
            "2026",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Registros: 25", resultado.stdout)
        self.assertIn("puede coincidir", resultado.stderr)

        with destino.open(encoding="utf-8-sig", newline="") as archivo:
            filas = list(csv.DictReader(archivo, delimiter=";"))
        self.assertEqual(len(filas), 25)
        self.assertEqual(filas[0]["id_prueba"], "DEMO-000001")
        self.assertEqual(len({fila["rut"] for fila in filas}), 25)
        for fila in filas:
            self.assertTrue(validar(fila["rut"]), fila["rut"])
            self.assertTrue(fila["correo"].endswith("@ejemplo.test"))

    def test_genera_json_valido(self):
        destino = self.carpeta / "lote.json"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "25",
            "--formato",
            "json",
            "--salida",
            str(destino),
            "--semilla",
            "2026",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        registros = json.loads(destino.read_text(encoding="utf-8"))
        self.assertEqual(len(registros), 25)
        self.assertIsInstance(registros[0]["monto_clp"], int)
        for registro in registros:
            self.assertTrue(validar(registro["rut"]))

    def test_filtro_de_cliente_empresa_completa_la_columna(self):
        destino = self.carpeta / "empresas.json"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "12",
            "--formato",
            "json",
            "--salida",
            str(destino),
            "--campos",
            "tipo_cliente,empresa",
            "--tipos-cliente",
            "Empresa",
            "--semilla",
            "42",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        registros = json.loads(destino.read_text(encoding="utf-8"))
        self.assertEqual(len(registros), 12)
        self.assertTrue(all(fila["tipo_cliente"] == "Empresa" for fila in registros))
        self.assertTrue(all(fila["empresa"].strip() for fila in registros))

    def test_filtro_estado_de_pago_se_aplica_a_la_salida(self):
        destino = self.carpeta / "rechazadas.json"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "12",
            "--formato",
            "json",
            "--salida",
            str(destino),
            "--campos",
            "estado_pago,estado_transaccion,estado_pedido",
            "--estados-pago",
            "Rechazado",
            "--semilla",
            "42",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        registros = json.loads(destino.read_text(encoding="utf-8"))
        self.assertTrue(registros)
        self.assertTrue(all(fila["estado_pago"] == "Rechazado" for fila in registros))
        self.assertTrue(all(fila["estado_transaccion"] == "Rechazada" for fila in registros))
        self.assertTrue(all(fila["estado_pedido"] == "No procesado" for fila in registros))

    def test_misma_semilla_mismos_archivos(self):
        primero = self.carpeta / "uno.csv"
        segundo = self.carpeta / "dos.csv"
        for destino in (primero, segundo):
            resultado = ejecutar(
                "generar",
                "--cantidad",
                "30",
                "--formato",
                "csv",
                "--salida",
                str(destino),
                "--semilla",
                "2026",
            )
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(primero.read_bytes(), segundo.read_bytes())

    def test_formato_no_altera_datos(self):
        csv_destino = self.carpeta / "lote.csv"
        json_destino = self.carpeta / "lote.json"
        for formato, destino in (("csv", csv_destino), ("json", json_destino)):
            resultado = ejecutar(
                "generar",
                "--cantidad",
                "15",
                "--formato",
                formato,
                "--salida",
                str(destino),
                "--semilla",
                "77",
            )
            self.assertEqual(resultado.returncode, 0, resultado.stderr)

        with csv_destino.open(encoding="utf-8-sig", newline="") as archivo:
            filas_csv = list(csv.DictReader(archivo, delimiter=";"))
        registros_json = json.loads(json_destino.read_text(encoding="utf-8"))
        self.assertEqual(
            [fila["rut"] for fila in filas_csv],
            [registro["rut"] for registro in registros_json],
        )
        self.assertEqual(
            [int(fila["monto_clp"]) for fila in filas_csv],
            [registro["monto_clp"] for registro in registros_json],
        )

    def test_semilla_automatica_se_informa_y_reproduce(self):
        primero = self.carpeta / "auto.json"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "5",
            "--formato",
            "json",
            "--salida",
            str(primero),
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        coincidencia = re.search(r"--semilla (\d+)", resultado.stdout)
        self.assertIsNotNone(coincidencia)
        semilla = coincidencia.group(1)

        segundo = self.carpeta / "manual.json"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "5",
            "--formato",
            "json",
            "--salida",
            str(segundo),
            "--semilla",
            semilla,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(primero.read_bytes(), segundo.read_bytes())

    def test_no_sobrescribe_por_defecto(self):
        destino = self.carpeta / "lote.csv"
        destino.write_text("original", encoding="utf-8")
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "5",
            "--formato",
            "csv",
            "--salida",
            str(destino),
            "--semilla",
            "1",
        )
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("ya existe", resultado.stderr)
        self.assertEqual(destino.read_text(encoding="utf-8"), "original")

        resultado = ejecutar(
            "generar",
            "--cantidad",
            "5",
            "--formato",
            "csv",
            "--salida",
            str(destino),
            "--semilla",
            "1",
            "--sobrescribir",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("DEMO-000001", destino.read_text(encoding="utf-8-sig"))

    def test_cantidad_fuera_de_rango(self):
        destino = self.carpeta / "lote.csv"
        for cantidad in ("0", "-3", "10001"):
            with self.subTest(cantidad=cantidad):
                resultado = ejecutar(
                    "generar",
                    "--cantidad",
                    cantidad,
                    "--formato",
                    "csv",
                    "--salida",
                    str(destino),
                )
                self.assertEqual(resultado.returncode, 2)
                self.assertIn("cantidad", resultado.stderr.lower())
                self.assertFalse(destino.exists())

    def test_cantidad_no_numerica(self):
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "muchos",
            "--formato",
            "csv",
            "--salida",
            str(self.carpeta / "lote.csv"),
        )
        self.assertEqual(resultado.returncode, 2)

    def test_formato_invalido(self):
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "5",
            "--formato",
            "xml",
            "--salida",
            str(self.carpeta / "lote.xml"),
        )
        self.assertEqual(resultado.returncode, 2)

    def test_carpeta_de_destino_inexistente(self):
        destino = self.carpeta / "sin_carpeta" / "lote.csv"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "5",
            "--formato",
            "csv",
            "--salida",
            str(destino),
        )
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("carpeta", resultado.stderr.lower())
        self.assertFalse(destino.exists())


class PersonalizacionCliTests(unittest.TestCase):
    def setUp(self):
        self._temporal = tempfile.TemporaryDirectory()
        self.carpeta = Path(self._temporal.name)
        self.addCleanup(self._temporal.cleanup)

    def test_csv_personalizado(self):
        destino = self.carpeta / "personalizado.csv"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "12",
            "--formato",
            "csv",
            "--salida",
            str(destino),
            "--semilla",
            "2026",
            "--campos",
            "rut,nombre,region,comuna,estado,monto_clp,fecha_registro,correo",
            "--formato-rut",
            "sin_puntos",
            "--region",
            "Biobío",
            "--comuna",
            "Concepción",
            "--dominio-correo",
            "qa.ejemplo.test",
            "--fecha-desde",
            "2024-01-01",
            "--fecha-hasta",
            "2024-12-31",
            "--monto-min",
            "10000",
            "--monto-max",
            "20000",
            "--monto-paso",
            "1000",
            "--delimitador",
            ",",
            "--sin-bom",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Campos: 8", resultado.stdout)

        datos = destino.read_bytes()
        self.assertFalse(datos.startswith(b"\xef\xbb\xbf"))
        with destino.open(encoding="utf-8", newline="") as archivo:
            filas = list(csv.DictReader(archivo, delimiter=","))

        self.assertEqual(len(filas), 12)
        self.assertEqual(
            list(filas[0]),
            [
                "rut",
                "nombre",
                "region",
                "comuna",
                "estado",
                "monto_clp",
                "fecha_registro",
                "correo",
            ],
        )
        for fila in filas:
            self.assertRegex(fila["rut"], r"^\d{8}-[\dK]$")
            self.assertTrue(validar(fila["rut"]))
            self.assertEqual(fila["region"], "Biobío")
            self.assertEqual(fila["comuna"], "Concepción")
            self.assertIn(fila["estado"], ("Activo", "Inactivo", "Pendiente"))
            self.assertTrue(fila["correo"].endswith("@qa.ejemplo.test"))
            self.assertGreaterEqual(int(fila["monto_clp"]), 10_000)
            self.assertLessEqual(int(fila["monto_clp"]), 20_000)
            self.assertEqual(int(fila["monto_clp"]) % 1_000, 0)
            self.assertTrue(fila["fecha_registro"].startswith("2024-"))

    def test_json_personalizado_y_orden_de_campos(self):
        destino = self.carpeta / "personalizado.json"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "8",
            "--formato",
            "json",
            "--salida",
            str(destino),
            "--semilla",
            "42",
            "--campos",
            "rut, correo, edad, nombre_completo",
            "--formato-rut",
            "sin_separadores",
            "--dominio-correo",
            "demo.test",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        registros = json.loads(destino.read_text(encoding="utf-8"))
        self.assertEqual(len(registros), 8)
        for registro in registros:
            self.assertEqual(
                list(registro),
                ["rut", "correo", "edad", "nombre_completo"],
            )
            self.assertRegex(registro["rut"], r"^\d{8}[\dK]$")
            self.assertTrue(validar(registro["rut"]))
            self.assertTrue(registro["correo"].endswith("@demo.test"))
            self.assertGreaterEqual(registro["edad"], 18)
            self.assertLessEqual(registro["edad"], 80)
            self.assertIn(" ", registro["nombre_completo"])

    def test_delimitador_tabulador(self):
        destino = self.carpeta / "tabulado.csv"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "5",
            "--formato",
            "csv",
            "--salida",
            str(destino),
            "--semilla",
            "1",
            "--campos",
            "rut,nombre",
            "--delimitador",
            "tab",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        with destino.open(encoding="utf-8-sig", newline="") as archivo:
            filas = list(csv.DictReader(archivo, delimiter="\t"))
        self.assertEqual(len(filas), 5)
        self.assertEqual(list(filas[0]), ["rut", "nombre"])

    def test_opciones_invalidas_no_crean_archivo(self):
        casos = (
            ("--region", "Región Inventada"),
            ("--comuna", "Concepción"),
            ("--region", "Biobío", "--comuna", "Santiago"),
            ("--fecha-desde", "2025-02-30"),
            ("--fecha-desde", "2025-01-02", "--fecha-hasta", "2025-01-01"),
            ("--monto-min", "0"),
            ("--monto-min", "5000", "--monto-max", "1000"),
            ("--monto-paso", "0"),
            ("--dominio-correo", "ejemplo.com"),
            ("--campos", "rut,no_existe"),
            ("--campos", "rut,rut"),
            ("--formato-rut", "con_guiones"),
            ("--delimitador", "|"),
        )
        for indice, extra in enumerate(casos, start=1):
            with self.subTest(extra=extra):
                destino = self.carpeta / f"invalido_{indice}.csv"
                resultado = ejecutar(
                    "generar",
                    "--cantidad",
                    "5",
                    "--formato",
                    "csv",
                    "--salida",
                    str(destino),
                    "--semilla",
                    "1",
                    *extra,
                )
                self.assertEqual(resultado.returncode, 2, resultado.stderr)
                self.assertTrue(resultado.stderr.strip())
                self.assertFalse(destino.exists())

    def test_rango_de_montos_y_fechas_en_salida(self):
        destino = self.carpeta / "rango.json"
        resultado = ejecutar(
            "generar",
            "--cantidad",
            "30",
            "--formato",
            "json",
            "--salida",
            str(destino),
            "--semilla",
            "9",
            "--campos",
            "fecha_registro,monto_clp",
            "--fecha-desde",
            "2024-06-01",
            "--fecha-hasta",
            "2024-06-30",
            "--monto-min",
            "5000",
            "--monto-max",
            "9000",
            "--monto-paso",
            "500",
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        registros = json.loads(destino.read_text(encoding="utf-8"))
        for registro in registros:
            self.assertTrue(registro["fecha_registro"].startswith("2024-06-"))
            self.assertGreaterEqual(registro["monto_clp"], 5_000)
            self.assertLessEqual(registro["monto_clp"], 9_000)
            self.assertEqual(registro["monto_clp"] % 500, 0)


class ValidarRutCliTests(unittest.TestCase):
    def test_rut_valido(self):
        resultado = ejecutar("validar-rut", "12.345.678-5")
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("RUT válido: 12.345.678-5", resultado.stdout)

    def test_k_minuscula(self):
        resultado = ejecutar("validar-rut", "6-k")
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("RUT válido: 6-K", resultado.stdout)

    def test_dv_incorrecto(self):
        resultado = ejecutar("validar-rut", "12.345.678-4")
        self.assertEqual(resultado.returncode, 2)
        self.assertIn("se esperaba 5", resultado.stderr)

    def test_formato_invalido(self):
        resultado = ejecutar("validar-rut", "no-es-un-rut")
        self.assertEqual(resultado.returncode, 2)
        self.assertIn("RUT inválido", resultado.stderr)


if __name__ == "__main__":
    unittest.main()
