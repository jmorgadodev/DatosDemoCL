"""Pruebas de humo de la interfaz gráfica Tkinter.

Se omiten automáticamente si el entorno no puede abrir una ventana.
"""

import csv
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from datosdemocl.generator import (
    FORMATO_RUT_CON_PUNTOS,
    FORMATO_RUT_SIN_PUNTOS,
    GenerationError,
)
from datosdemocl.schema import CAMPOS_POR_DEFECTO, PRESETS
from datosdemocl.schema import ETIQUETAS

try:
    import tkinter as tk

    from datosdemocl.gui import (
        ETIQUETAS_FORMATO_RUT,
        TODAS_COMUNAS,
        TODAS_REGIONES,
        Aplicacion,
    )

    TKINTER_DISPONIBLE = True
except ImportError:
    TKINTER_DISPONIBLE = False


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not TKINTER_DISPONIBLE:
            raise unittest.SkipTest("Tkinter no está instalado.")
        try:
            cls.app = Aplicacion()
        except tk.TclError as exc:
            raise unittest.SkipTest(
                f"Tkinter no puede abrir una ventana: {exc}"
            ) from exc
        cls.app.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.app.destroy()

    def setUp(self):
        self.app._restablecer()
        self.app.update_idletasks()

    def test_aviso_extenso_no_ocupa_la_ventana(self):
        self.assertFalse(hasattr(self.app, "lbl_aviso"))

    def test_id_prueba_tiene_etiqueta_limpia_sin_subrayado(self):
        self.assertEqual(ETIQUETAS["id_prueba"], "ID de registro")
        self.assertEqual(self.app.chk_campos["id_prueba"].cget("underline"), -1)

    def test_configuracion_por_defecto(self):
        opciones = self.app._leer_opciones()
        self.assertEqual(opciones.cantidad, 25)
        self.assertIsNone(opciones.semilla)
        self.assertEqual(self.app.var_semilla.get(), "")
        self.assertEqual(opciones.campos, PRESETS["sabana_ventas"])
        self.assertEqual(opciones.formato_rut, FORMATO_RUT_CON_PUNTOS)
        self.assertEqual(opciones.region, None)
        self.assertEqual(opciones.comuna, None)
        self.assertEqual(opciones.fecha_desde, date(2023, 1, 1))
        self.assertEqual(opciones.fecha_hasta, date(2025, 12, 31))

    def test_formato_rut_desde_la_interfaz(self):
        self.app.var_formato_rut.set(
            ETIQUETAS_FORMATO_RUT[FORMATO_RUT_SIN_PUNTOS]
        )
        self.assertEqual(
            self.app._leer_opciones().formato_rut, FORMATO_RUT_SIN_PUNTOS
        )

    def test_region_actualiza_comunas(self):
        self.app.var_region.set("Biobío")
        self.app._actualizar_comunas()
        valores = self.app.cmb_comuna.cget("values")
        self.assertIn("Concepción", valores)
        self.assertEqual(self.app.var_comuna.get(), TODAS_COMUNAS)

        self.app.var_comuna.set("Concepción")
        opciones = self.app._leer_opciones()
        self.assertEqual(opciones.region, "Biobío")
        self.assertEqual(opciones.comuna, "Concepción")

    def test_volver_a_todas_las_regiones(self):
        self.app.var_region.set("Biobío")
        self.app._actualizar_comunas()
        self.app.var_region.set(TODAS_REGIONES)
        self.app._actualizar_comunas()
        self.assertEqual(self.app.var_comuna.get(), TODAS_COMUNAS)
        self.assertEqual(
            str(self.app.cmb_comuna.cget("state")), "disabled"
        )

    def test_vista_previa_genera_y_muestra_filas(self):
        self.app._vista_previa()
        self.assertEqual(len(self.app.tree.get_children()), 5)
        columnas = self.app.tree.cget("columns")
        self.assertEqual(tuple(columnas), PRESETS["sabana_ventas"])
        self.assertIn("Muestra lista", self.app.var_estado.get())

    def test_limpiar_categoria_pausa_y_al_reseleccionar_recupera_la_muestra(self):
        self.app._vista_previa()
        self.assertEqual(len(self.app.tree.get_children()), 5)
        botones = tuple(self.app.btn_opciones["tipos_documento_pago"].values())

        self.app._seleccionar_opciones_grupo("tipos_documento_pago", False)
        self.assertEqual(self.app.tree.get_children(), ())
        self.assertEqual(tuple(self.app.tree.cget("columns")), ())
        self.assertIn("tipo de documento", self.app.lbl_preview.cget("text").lower())
        self.assertEqual(
            tuple(self.app.btn_opciones["tipos_documento_pago"].values()), botones
        )

        self.app._alternar_opcion(
            "tipos_documento_pago", "Factura electrónica"
        )
        self.assertEqual(len(self.app.tree.get_children()), 5)
        self.assertIn("muestra", self.app.lbl_preview.cget("text").lower())

    def test_cambio_de_estado_de_pago_actualiza_la_muestra(self):
        self.app.var_campos["estado_pago"].set(True)
        for estado, variable in self.app.var_opciones["estados_pago"].items():
            variable.set(estado == "Rechazado")
        self.app._refrescar_vista_previa()

        self.assertEqual(len(self.app.tree.get_children()), 5)
        campos = tuple(self.app.tree.cget("columns"))
        self.assertIn("estado_pago", campos)
        posicion = campos.index("estado_pago")
        for fila in self.app.tree.get_children():
            valores = self.app.tree.item(fila, "values")
            self.assertEqual(valores[posicion], "Rechazado")

    def test_estado_pago_marcado_identifica_otra_categoria_vacia(self):
        self.app.var_campos["estado_pago"].set(True)
        for estado, variable in self.app.var_opciones["estados_pago"].items():
            variable.set(estado == "Aprobado")

        self.app._seleccionar_opciones_grupo("tipos_documento_pago", False)
        self.assertEqual(self.app.tree.get_children(), ())
        self.assertIn("Tipo de documento", self.app.lbl_preview.cget("text"))
        self.assertNotIn("Estado de pago", self.app.lbl_preview.cget("text"))

        documento = next(iter(self.app.var_opciones["tipos_documento_pago"]))
        self.app._alternar_opcion("tipos_documento_pago", documento)
        self.assertEqual(len(self.app.tree.get_children()), 5)
        self.assertIn("estado_pago", self.app.tree.cget("columns"))
        posicion = tuple(self.app.tree.cget("columns")).index("estado_pago")
        for fila in self.app.tree.get_children():
            self.assertEqual(
                self.app.tree.item(fila, "values")[posicion], "Aprobado"
            )

    def test_semilla_automatica_conserva_muestra_y_archivo(self):
        self.app._vista_previa()
        self.assertEqual(self.app.var_semilla.get(), "")
        semilla = self.app._semilla_lote_actual
        self.assertIsInstance(semilla, int)
        previa = [self.app.tree.item(fila, "values") for fila in self.app.tree.get_children()]

        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "muestra.csv"
            self.app.var_salida.set(str(destino))
            with patch(
                "datosdemocl.gui.messagebox.askyesno", return_value=False
            ), patch("datosdemocl.gui.messagebox.showerror") as mostrar_error:
                self.app._generar_archivo()
            mostrar_error.assert_not_called()
            with destino.open(encoding="utf-8-sig", newline="") as archivo:
                filas = list(csv.reader(archivo, delimiter=";"))

        self.assertEqual(tuple(filas[0]), PRESETS["sabana_ventas"])
        self.assertEqual(filas[1:6], [list(fila) for fila in previa])
        self.assertEqual(self.app._semilla_lote_actual, semilla)
        self.assertEqual(self.app.var_semilla.get(), "")

    def test_seleccion_de_columnas(self):
        self.app._seleccionar_todas()
        self.assertEqual(
            len(self.app._leer_opciones().campos), 44
        )
        self.app._seleccionar_ninguna()
        with self.assertRaises(GenerationError):
            self.app._leer_opciones()

    def test_generar_archivo_ajusta_la_extension(self):
        with tempfile.TemporaryDirectory() as carpeta:
            self.app.var_formato.set("CSV")
            self.app.var_cantidad.set("3")
            self.app.var_salida.set(str(Path(carpeta) / "lote.json"))

            with patch(
                "datosdemocl.gui.messagebox.askyesno", return_value=False
            ), patch(
                "datosdemocl.gui.messagebox.showerror"
            ) as mostrar_error:
                self.app._generar_archivo()

            mostrar_error.assert_not_called()
            self.assertTrue((Path(carpeta) / "lote.csv").exists())
            self.assertFalse((Path(carpeta) / "lote.json").exists())
            self.assertEqual(
                Path(self.app.var_salida.get()).suffix.lower(), ".csv"
            )

    def test_generar_archivo_json(self):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "lote.json"
            self.app.var_formato.set("JSON")
            self.app.var_cantidad.set("3")
            self.app.var_salida.set(str(destino))

            with patch(
                "datosdemocl.gui.messagebox.askyesno", return_value=False
            ), patch("datosdemocl.gui.messagebox.showerror") as mostrar_error:
                self.app._generar_archivo()

            mostrar_error.assert_not_called()
            datos = json.loads(destino.read_text(encoding="utf-8"))
            self.assertEqual(len(datos), 3)
            self.assertEqual(tuple(datos[0]), PRESETS["sabana_ventas"])

    def test_no_exporta_si_una_categoria_esta_vacia(self):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "incompleto.csv"
            self.app.var_salida.set(str(destino))
            self.app._seleccionar_opciones_grupo("estados_pago", False)

            with patch(
                "datosdemocl.gui.messagebox.showerror"
            ) as mostrar_error:
                self.app._generar_archivo()

            mostrar_error.assert_called_once()
            self.assertIn(
                "estados de pago", mostrar_error.call_args.args[1].lower()
            )
            self.assertFalse(destino.exists())

    def test_generar_no_sobrescribe_si_se_cancela(self):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = Path(carpeta) / "lote.csv"
            destino.write_text("original", encoding="utf-8")
            self.app.var_cantidad.set("3")
            self.app.var_salida.set(str(destino))

            with patch(
                "datosdemocl.gui.messagebox.askyesno", return_value=False
            ), patch(
                "datosdemocl.gui.messagebox.showerror"
            ) as mostrar_error:
                self.app._generar_archivo()

            mostrar_error.assert_not_called()
            self.assertEqual(
                destino.read_text(encoding="utf-8"), "original"
            )


if __name__ == "__main__":
    unittest.main()
