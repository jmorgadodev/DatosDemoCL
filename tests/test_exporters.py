import csv
import json
import tempfile
import unittest
from pathlib import Path

from datosdemocl.exporters import (
    DELIMITADOR_CSV,
    ExportError,
    OutputExistsError,
    OutputPathError,
    exportar_csv,
    exportar_json,
    serializar_csv,
    serializar_json,
)
from datosdemocl.generator import CAMPOS

REGISTROS = [
    {
        "id_prueba": "DEMO-000001",
        "nombre": "José",
        "apellido": "Ñandú",
        "rut": "12.345.678-5",
        "correo": "jose.nandu0001@ejemplo.test",
        "region": "Biobío",
        "comuna": "Concepción",
        "fecha_registro": "2024-02-29",
        "monto_clp": 1500,
    },
    {
        "id_prueba": "DEMO-000002",
        "nombre": "Valentina",
        "apellido": "Muñoz",
        "rut": "6-K",
        "correo": "valentina.munoz0002@ejemplo.test",
        "region": "Ñuble",
        "comuna": "Chillán",
        "fecha_registro": "2025-12-31",
        "monto_clp": 5_000_000,
    },
]


class SerializacionTests(unittest.TestCase):
    def test_csv_encabezado_delimitador_y_crlf(self):
        texto = serializar_csv(REGISTROS)
        lineas = texto.split("\r\n")
        self.assertEqual(lineas[0], DELIMITADOR_CSV.join(CAMPOS))
        self.assertEqual(lineas[-1], "")
        self.assertEqual(len(lineas), len(REGISTROS) + 2)
        for linea in lineas[1:-1]:
            self.assertEqual(len(linea.split(DELIMITADOR_CSV)), len(CAMPOS))
        self.assertIn("José", lineas[1])
        self.assertIn("Ñandú", lineas[1])
        self.assertIn("Ñuble", lineas[2])

    def test_json_conserva_acentos_y_tipos(self):
        texto = serializar_json(REGISTROS)
        recuperados = json.loads(texto)
        self.assertEqual(recuperados, REGISTROS)
        self.assertIn("Ñandú", texto)
        self.assertIn("Biobío", texto)
        self.assertIsInstance(recuperados[0]["monto_clp"], int)

    def test_registro_incompleto(self):
        incompleto = [{"id_prueba": "DEMO-000001"}]
        for serializador in (serializar_csv, serializar_json):
            with self.subTest(serializador=serializador.__name__):
                with self.assertRaises(ExportError):
                    serializador(incompleto)

    def test_orden_de_campos_estable(self):
        texto = serializar_csv(REGISTROS)
        self.assertTrue(texto.startswith(DELIMITADOR_CSV.join(CAMPOS)))

    def test_columnas_personalizadas_en_orden(self):
        campos = ("rut", "nombre")
        texto = serializar_csv(REGISTROS, campos=campos)
        lineas = texto.split("\r\n")
        self.assertEqual(lineas[0], "rut;nombre")
        self.assertEqual(lineas[1].split(";"), ["12.345.678-5", "José"])

        datos = json.loads(serializar_json(REGISTROS, campos=campos))
        self.assertEqual([tuple(fila) for fila in datos], [campos, campos])
        self.assertEqual(datos[0]["rut"], "12.345.678-5")

    def test_columnas_personalizadas_incompletas(self):
        with self.assertRaises(ExportError):
            serializar_csv(REGISTROS, campos=("rut", "estado"))
        with self.assertRaises(ExportError):
            serializar_json(REGISTROS, campos=("estado",))
        with self.assertRaises(ExportError):
            serializar_csv(REGISTROS, campos=())

    def test_delimitadores_alternativos(self):
        for delimitador in (",", "\t", "|"):
            with self.subTest(delimitador=delimitador):
                texto = serializar_csv(REGISTROS, delimitador=delimitador)
                self.assertEqual(
                    texto.split("\r\n")[0], delimitador.join(CAMPOS)
                )

    def test_delimitador_invalido(self):
        for delimitador in ("", ";;", None, 1):
            with self.subTest(delimitador=delimitador):
                with self.assertRaises(ExportError):
                    serializar_csv(REGISTROS, delimitador=delimitador)


class EscrituraTests(unittest.TestCase):
    def setUp(self):
        self._temporal = tempfile.TemporaryDirectory()
        self.carpeta = Path(self._temporal.name)
        self.addCleanup(self._temporal.cleanup)

    def test_csv_utf8_con_bom(self):
        destino = self.carpeta / "lote.csv"
        exportar_csv(destino, REGISTROS)
        datos = destino.read_bytes()
        self.assertTrue(datos.startswith(b"\xef\xbb\xbf"))
        texto = datos.decode("utf-8-sig")
        self.assertIn("Ñandú", texto)
        self.assertIn(";", texto)

    def test_csv_sin_bom(self):
        destino = self.carpeta / "sin_bom.csv"
        exportar_csv(destino, REGISTROS, incluir_bom=False)
        datos = destino.read_bytes()
        self.assertFalse(datos.startswith(b"\xef\xbb\xbf"))
        self.assertIn("Ñandú", datos.decode("utf-8"))

    def test_bom_invalido(self):
        destino = self.carpeta / "lote.csv"
        for valor in ("si", 1, None):
            with self.subTest(valor=valor):
                with self.assertRaises(ExportError):
                    exportar_csv(destino, REGISTROS, incluir_bom=valor)
        self.assertFalse(destino.exists())

    def test_columnas_personalizadas_escritas(self):
        destino = self.carpeta / "columnas.csv"
        exportar_csv(destino, REGISTROS, campos=("rut", "nombre"))
        with destino.open(encoding="utf-8-sig", newline="") as archivo:
            filas = list(csv.DictReader(archivo, delimiter=";"))
        self.assertEqual(list(filas[0]), ["rut", "nombre"])
        self.assertEqual(len(filas), len(REGISTROS))

    def test_json_utf8_sin_bom(self):
        destino = self.carpeta / "lote.json"
        exportar_json(destino, REGISTROS)
        datos = destino.read_bytes()
        self.assertFalse(datos.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(json.loads(datos.decode("utf-8")), REGISTROS)
        self.assertIn("Ñandú", datos.decode("utf-8"))

    def test_no_sobrescribe_sin_permiso(self):
        destino = self.carpeta / "lote.csv"
        destino.write_text("original", encoding="utf-8")
        with self.assertRaises(OutputExistsError):
            exportar_csv(destino, REGISTROS)
        with self.assertRaises(OutputExistsError):
            exportar_json(destino, REGISTROS)
        self.assertEqual(destino.read_text(encoding="utf-8"), "original")

    def test_sobrescribe_con_permiso(self):
        destino = self.carpeta / "lote.csv"
        destino.write_text("original", encoding="utf-8")
        exportar_csv(destino, REGISTROS, sobrescribir=True)
        self.assertIn("Ñandú", destino.read_text(encoding="utf-8-sig"))

    def test_carpeta_inexistente(self):
        destino = self.carpeta / "no_existe" / "lote.csv"
        with self.assertRaises(OutputPathError):
            exportar_csv(destino, REGISTROS)
        self.assertFalse(destino.exists())

    def test_salida_es_carpeta(self):
        with self.assertRaises(OutputPathError):
            exportar_json(self.carpeta, REGISTROS, sobrescribir=True)

    def test_no_deja_temporales(self):
        destino = self.carpeta / "lote.csv"
        exportar_csv(destino, REGISTROS)
        self.assertEqual(
            sorted(ruta.name for ruta in self.carpeta.iterdir()), ["lote.csv"]
        )


if __name__ == "__main__":
    unittest.main()
