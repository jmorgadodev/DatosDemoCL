import unittest
from datetime import date

from datosdemocl.catalog import APELLIDOS, NOMBRES, REGIONES
from datosdemocl.generator import (
    CAMPOS,
    CANALES_VENTA,
    DOMINIO_CORREO,
    EDAD_MAXIMA,
    EDAD_MINIMA,
    ESTADOS_TRANSACCION,
    FECHA_LIMITE_MAXIMA,
    FECHA_LIMITE_MINIMA,
    FECHA_MAXIMA,
    FECHA_MINIMA,
    FORMATO_RUT_CON_PUNTOS,
    FORMATO_RUT_SIN_PUNTOS,
    FORMATO_RUT_SIN_SEPARADORES,
    MAX_REGISTROS,
    MIN_REGISTROS,
    PASARELAS_PAGO,
    TIPOS_DOCUMENTO_PAGO,
    GenerationError,
    OpcionesGeneracion,
    generar_lote,
    generar_registros,
)
from datosdemocl.rut import validar
from datosdemocl.schema import CAMPOS_DISPONIBLES, CAMPOS_TRANSACCION


class GeneracionTests(unittest.TestCase):
    def test_misma_semilla_produce_mismos_registros(self):
        uno, semilla_uno = generar_registros(20, 2026)
        otro, semilla_otro = generar_registros(20, 2026)
        self.assertEqual(semilla_uno, 2026)
        self.assertEqual(semilla_otro, 2026)
        self.assertEqual(uno, otro)

    def test_semillas_distintas_producen_lotes_distintos(self):
        uno, _ = generar_registros(20, 1)
        otro, _ = generar_registros(20, 2)
        self.assertNotEqual(uno, otro)

    def test_sin_semilla_informa_una_semilla_reproducible(self):
        primero, semilla = generar_registros(5)
        self.assertIsInstance(semilla, int)
        segundo, _ = generar_registros(5, semilla)
        self.assertEqual(primero, segundo)

    def test_campos_y_tipos(self):
        registros, _ = generar_registros(30, 99)
        self.assertEqual(len(registros), 30)
        for posicion, registro in enumerate(registros, start=1):
            with self.subTest(posicion=posicion):
                self.assertEqual(tuple(registro), CAMPOS)
                self.assertEqual(registro["id_prueba"], f"DEMO-{posicion:06d}")
                self.assertIsInstance(registro["nombre"], str)
                self.assertIsInstance(registro["apellido"], str)
                self.assertIsInstance(registro["rut"], str)
                self.assertIsInstance(registro["correo"], str)
                self.assertIsInstance(registro["region"], str)
                self.assertIsInstance(registro["comuna"], str)
                self.assertIsInstance(registro["fecha_registro"], str)
                self.assertIsInstance(registro["monto_clp"], int)

    def test_ruts_unicos_y_validos_en_el_lote(self):
        registros, _ = generar_registros(500, 2026)
        ruts = [registro["rut"] for registro in registros]
        self.assertEqual(len(ruts), len(set(ruts)))
        for rut in ruts:
            self.assertTrue(validar(rut), rut)

    def test_cuerpos_en_rango_alto_documentado(self):
        registros, _ = generar_registros(100, 2026)
        for registro in registros:
            cuerpo = int(registro["rut"].split("-")[0].replace(".", ""))
            self.assertGreaterEqual(cuerpo, 50_000_000)
            self.assertLessEqual(cuerpo, 99_999_999)

    def test_correos_unicos_y_bajo_dominio_test(self):
        registros, _ = generar_registros(100, 7)
        correos = [registro["correo"] for registro in registros]
        self.assertEqual(len(correos), len(set(correos)))
        for correo in correos:
            with self.subTest(correo=correo):
                self.assertTrue(correo.endswith(f"@{DOMINIO_CORREO}"))
                local = correo.split("@", 1)[0]
                self.assertEqual(local, local.lower())
                self.assertTrue(local.isascii())
                self.assertNotIn(" ", local)

    def test_fechas_iso_dentro_del_rango(self):
        registros, _ = generar_registros(200, 11)
        for registro in registros:
            fecha = date.fromisoformat(registro["fecha_registro"])
            self.assertGreaterEqual(fecha, FECHA_MINIMA)
            self.assertLessEqual(fecha, FECHA_MAXIMA)
            self.assertEqual(len(registro["fecha_registro"]), 10)

    def test_montos_enteros_y_en_rango(self):
        registros, _ = generar_registros(200, 12)
        for registro in registros:
            monto = registro["monto_clp"]
            self.assertIsInstance(monto, int)
            self.assertGreaterEqual(monto, 1_000)
            self.assertLessEqual(monto, 5_000_000)
            self.assertEqual(monto % 100, 0)

    def test_region_y_comuna_pertenecen_al_catalogo(self):
        registros, _ = generar_registros(100, 13)
        mapa = {region: set(comunas) for region, comunas in REGIONES}
        for registro in registros:
            self.assertIn(registro["region"], mapa)
            self.assertIn(registro["comuna"], mapa[registro["region"]])

    def test_nombres_y_apellidos_salen_del_catalogo(self):
        registros, _ = generar_registros(100, 14)
        for registro in registros:
            self.assertIn(registro["nombre"], NOMBRES)
            self.assertIn(registro["apellido"], APELLIDOS)


class LimitesTests(unittest.TestCase):
    def test_cantidades_invalidas(self):
        for cantidad in (0, -1, MAX_REGISTROS + 1, 1.0, "5", True, None):
            with self.subTest(cantidad=cantidad):
                with self.assertRaises(GenerationError):
                    generar_registros(cantidad, 1)

    def test_limite_minimo_y_maximo_son_aceptados(self):
        registros, _ = generar_registros(MIN_REGISTROS, 1)
        self.assertEqual(len(registros), MIN_REGISTROS)
        registros, _ = generar_registros(MAX_REGISTROS, 1)
        self.assertEqual(len(registros), MAX_REGISTROS)
        self.assertEqual(
            len({registro["rut"] for registro in registros}), MAX_REGISTROS
        )

    def test_semillas_invalidas(self):
        for semilla in (1.5, "2026", True):
            with self.subTest(semilla=semilla):
                with self.assertRaises(GenerationError):
                    generar_registros(1, semilla)


class ApiPublicaTests(unittest.TestCase):
    def test_exports_principales(self):
        import datosdemocl

        self.assertEqual(datosdemocl.__version__, "0.8.0")
        registros, semilla = datosdemocl.generar_registros(3, 2026)
        self.assertEqual(semilla, 2026)
        self.assertEqual(len(registros), 3)
        self.assertTrue(datosdemocl.validar(registros[0]["rut"]))
        self.assertEqual(datosdemocl.normalizar("6-k"), "6-K")
        self.assertEqual(datosdemocl.calcular_dv(12345678), "5")


class OpcionesTests(unittest.TestCase):
    def generar(self, **cambios):
        base = {"cantidad": 20, "semilla": 2026}
        base.update(cambios)
        return generar_lote(OpcionesGeneracion(**base))

    def test_seleccion_y_orden_de_columnas(self):
        registros, _ = self.generar(campos=("rut", "nombre", "estado"))
        for registro in registros:
            self.assertEqual(tuple(registro), ("rut", "nombre", "estado"))

    def test_formato_rut_con_puntos_por_defecto(self):
        registros, _ = self.generar(campos=("rut",))
        for registro in registros:
            self.assertRegex(
                registro["rut"], r"^\d{1,3}(?:\.\d{3})*-[\dK]$"
            )
            self.assertTrue(validar(registro["rut"]))

    def test_formato_rut_sin_puntos(self):
        registros, _ = self.generar(
            campos=("rut",), formato_rut=FORMATO_RUT_SIN_PUNTOS
        )
        for registro in registros:
            self.assertRegex(registro["rut"], r"^\d{8}-[\dK]$")
            self.assertNotIn(".", registro["rut"])
            self.assertTrue(validar(registro["rut"]))

    def test_formato_rut_sin_separadores(self):
        registros, _ = self.generar(
            campos=("rut",), formato_rut=FORMATO_RUT_SIN_SEPARADORES
        )
        for registro in registros:
            self.assertRegex(registro["rut"], r"^\d{8}[\dK]$")
            self.assertNotIn(".", registro["rut"])
            self.assertNotIn("-", registro["rut"])
            self.assertTrue(validar(registro["rut"]))

    def test_formato_rut_invalido(self):
        with self.assertRaises(GenerationError):
            self.generar(formato_rut="con_guiones")

    def test_filtro_por_region(self):
        registros, _ = self.generar(campos=("region", "comuna"), region="Biobío")
        for registro in registros:
            self.assertEqual(registro["region"], "Biobío")
            self.assertIn(
                registro["comuna"],
                ("Concepción", "Talcahuano", "Los Ángeles"),
            )

    def test_filtro_por_region_y_comuna(self):
        registros, _ = self.generar(
            campos=("region", "comuna"),
            region="Biobío",
            comuna="Concepción",
        )
        for registro in registros:
            self.assertEqual(registro["region"], "Biobío")
            self.assertEqual(registro["comuna"], "Concepción")

    def test_comuna_requiere_region(self):
        with self.assertRaises(GenerationError):
            self.generar(region=None, comuna="Concepción")

    def test_comuna_de_otra_region(self):
        with self.assertRaises(GenerationError):
            self.generar(region="Biobío", comuna="Santiago")

    def test_region_desconocida(self):
        with self.assertRaises(GenerationError):
            self.generar(region="Región Inventada")

    def test_rango_de_fechas(self):
        desde = date(2024, 3, 1)
        hasta = date(2024, 3, 31)
        registros, _ = self.generar(
            campos=("fecha_registro",),
            fecha_desde=desde,
            fecha_hasta=hasta,
        )
        for registro in registros:
            fecha = date.fromisoformat(registro["fecha_registro"])
            self.assertGreaterEqual(fecha, desde)
            self.assertLessEqual(fecha, hasta)

    def test_fechas_invertidas(self):
        with self.assertRaises(GenerationError):
            self.generar(
                fecha_desde=date(2025, 1, 2),
                fecha_hasta=date(2025, 1, 1),
            )

    def test_fechas_fuera_de_limites(self):
        for desde, hasta in (
            (date(1899, 12, 31), FECHA_MAXIMA),
            (FECHA_MINIMA, date(2101, 1, 1)),
        ):
            with self.subTest(desde=desde, hasta=hasta):
                with self.assertRaises(GenerationError):
                    self.generar(fecha_desde=desde, fecha_hasta=hasta)

    def test_rango_de_montos(self):
        registros, _ = self.generar(
            campos=("monto_clp",),
            monto_min=10_000,
            monto_max=20_000,
            monto_paso=1_000,
        )
        for registro in registros:
            monto = registro["monto_clp"]
            self.assertGreaterEqual(monto, 10_000)
            self.assertLessEqual(monto, 20_000)
            self.assertEqual(monto % 1_000, 0)

    def test_rangos_de_monto_invalidos(self):
        casos = (
            {"monto_min": 0},
            {"monto_min": 5_000, "monto_max": 1_000},
            {"monto_paso": 0},
            {"monto_min": 1_001, "monto_max": 1_099, "monto_paso": 100},
            {"monto_min": 1.5},
        )
        for cambios in casos:
            with self.subTest(cambios=cambios):
                with self.assertRaises(GenerationError):
                    self.generar(**cambios)

    def test_dominio_de_correo_personalizado(self):
        registros, _ = self.generar(
            campos=("correo",), dominio_correo="QA.Ejemplo.TEST"
        )
        for registro in registros:
            self.assertTrue(
                registro["correo"].endswith("@qa.ejemplo.test")
            )

    def test_dominio_de_correo_invalido(self):
        for dominio in ("ejemplo.com", "test", "ejemplo.test.evil", ""):
            with self.subTest(dominio=dominio):
                with self.assertRaises(GenerationError):
                    self.generar(dominio_correo=dominio)

    def test_campos_invalidos(self):
        for campos in ((), ("no_existe",), ("rut", "rut"), ("rut", " ")):
            with self.subTest(campos=campos):
                with self.assertRaises(GenerationError):
                    self.generar(campos=campos)

    def test_valores_categoricos_se_filtran_y_conservan_relaciones(self):
        registros, _ = self.generar(
            cantidad=12,
            campos=(
                "estado_pago",
                "estado_transaccion",
                "estado_pedido",
                "tipo_documento_pago",
                "pasarela_pago",
                "canal_venta",
                "tipo_cliente",
                "empresa",
            ),
            estados_pago=("Rechazado",),
            tipos_cliente=("Empresa",),
            tipos_documento_pago=("Boleta exenta",),
            pasarelas_pago=("Efectivo",),
            canales_venta=("Tienda",),
        )
        self.assertTrue(registros)
        for registro in registros:
            self.assertEqual(registro["estado_pago"], "Rechazado")
            self.assertEqual(registro["estado_transaccion"], "Rechazada")
            self.assertEqual(registro["estado_pedido"], "No procesado")
            self.assertEqual(registro["tipo_documento_pago"], "Boleta exenta")
            self.assertEqual(registro["pasarela_pago"], "Efectivo")
            self.assertEqual(registro["canal_venta"], "Tienda")
            self.assertEqual(registro["tipo_cliente"], "Empresa")
            self.assertTrue(registro["empresa"])

    def test_rechaza_selecciones_categoricas_vacias_o_desconocidas(self):
        for campo, valor in (
            ("estados_pago", ()),
            ("tipos_cliente", ("Sociedad",)),
            ("tipos_documento_pago", ()),
            ("pasarelas_pago", ()),
            ("canales_venta", ()),
        ):
            with self.subTest(campo=campo):
                with self.assertRaises(GenerationError):
                    self.generar(**{campo: valor})

    def test_campos_opcionales_coherentes(self):
        registros, _ = self.generar(
            cantidad=100, campos=CAMPOS_DISPONIBLES
        )
        for registro in registros:
            self.assertEqual(tuple(registro), CAMPOS_DISPONIBLES)
            nacimiento = date.fromisoformat(registro["fecha_nacimiento"])
            referencia = date.fromisoformat(registro["fecha_registro"])
            self.assertLessEqual(nacimiento, referencia)
            edad = referencia.year - nacimiento.year
            if (referencia.month, referencia.day) < (
                nacimiento.month,
                nacimiento.day,
            ):
                edad -= 1
            self.assertEqual(registro["edad"], edad)
            self.assertGreaterEqual(registro["edad"], EDAD_MINIMA)
            self.assertLessEqual(registro["edad"], EDAD_MAXIMA)
            self.assertEqual(
                registro["nombre_completo"],
                f"{registro['nombre']} {registro['apellido']}",
            )
            self.assertIn(
                registro["estado"], ("Activo", "Inactivo", "Pendiente")
            )
            self.assertIn(
                registro["categoria"], ("Básica", "Estándar", "Premium")
            )
            self.assertIn(registro["descuento_pct"], (0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50))

    def test_campos_opcionales_no_alteran_los_base(self):
        base, _ = generar_registros(50, 2026)
        completo, _ = self.generar(
            cantidad=50, semilla=2026, campos=CAMPOS_DISPONIBLES
        )
        for registro_base, registro_completo in zip(base, completo):
            for campo in CAMPOS:
                self.assertEqual(
                    registro_base[campo], registro_completo[campo]
                )

    def test_transacciones_no_alteran_los_quince_campos(self):
        anteriores = CAMPOS_DISPONIBLES[:15]
        quince, _ = self.generar(
            cantidad=50, semilla=2026, campos=anteriores
        )
        completo, _ = self.generar(
            cantidad=50, semilla=2026, campos=CAMPOS_DISPONIBLES
        )
        for registro_quince, registro_completo in zip(quince, completo):
            for campo in anteriores:
                self.assertEqual(
                    registro_quince[campo], registro_completo[campo]
                )

    def test_transacciones_reproducibles(self):
        primero, _ = self.generar(
            cantidad=25, campos=CAMPOS_TRANSACCION
        )
        segundo, _ = self.generar(
            cantidad=25, campos=CAMPOS_TRANSACCION
        )
        self.assertEqual(primero, segundo)

    def test_transacciones_con_semillas_distintas(self):
        primero, _ = self.generar(
            cantidad=25, semilla=1, campos=CAMPOS_TRANSACCION
        )
        segundo, _ = self.generar(
            cantidad=25, semilla=2, campos=CAMPOS_TRANSACCION
        )
        self.assertNotEqual(primero, segundo)

    def test_campos_de_transaccion_coherentes(self):
        registros, _ = self.generar(
            cantidad=90, campos=CAMPOS_DISPONIBLES
        )
        ids_venta = [registro["idventa"] for registro in registros]
        ids_chipax = [registro["id_chipax"] for registro in registros]
        ids_pago = [registro["idpayment_sale"] for registro in registros]
        folios = [registro["chipax_sale_note_folio"] for registro in registros]
        self.assertEqual(len(ids_venta), len(set(ids_venta)))
        self.assertEqual(len(ids_chipax), len(set(ids_chipax)))
        self.assertEqual(len(ids_pago), len(set(ids_pago)))
        self.assertEqual(len(folios), len(set(folios)))

        clientes: dict[str, str] = {}
        for registro in registros:
            self.assertEqual(registro["monto_total"], registro["monto_clp"])
            self.assertTrue(
                registro["fecha_hora_transaccion"].startswith(
                    registro["fecha_registro"]
                )
            )
            self.assertRegex(
                registro["fecha_hora_transaccion"],
                r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
            )
            self.assertRegex(registro["idventa"], r"^VTA-\d{6}$")
            self.assertRegex(registro["id_chipax"], r"^CHX-\d{6}$")
            self.assertRegex(registro["idpayment_sale"], r"^PAG-\d{6}$")
            self.assertIsInstance(registro["chipax_sale_note_folio"], int)
            self.assertIn(
                registro["tipo_documento_pago"], TIPOS_DOCUMENTO_PAGO
            )
            self.assertIn(registro["pasarela_pago"], PASARELAS_PAGO)
            self.assertIn(
                registro["estado_transaccion"], ESTADOS_TRANSACCION
            )
            self.assertIn(registro["canal_venta"], CANALES_VENTA)
            self.assertTrue(validar(registro["identificador_tributario"]))

            cliente = registro["cliente_interno"]
            self.assertRegex(cliente, r"^CLI-\d{6}$")
            if cliente in clientes:
                self.assertEqual(
                    clientes[cliente],
                    registro["identificador_tributario"],
                )
            else:
                clientes[cliente] = registro["identificador_tributario"]

            if registro["tipo_documento_pago"] == "Factura electrónica":
                self.assertIn(
                    registro["pasarela_pago"],
                    ("Transferencia", "Webpay", "Flow"),
                )
            if registro["pasarela_pago"] == "Efectivo":
                self.assertIn(
                    registro["canal_venta"], ("Tienda", "Marketplace")
                )
            if registro["pasarela_pago"] == "Transferencia":
                self.assertIn(
                    registro["canal_venta"],
                    ("Web", "Call center", "App"),
                )

        self.assertLess(len(clientes), len(registros))
        self.assertEqual(
            len(
                {
                    registro["identificador_tributario"]
                    for registro in registros
                }
            ),
            len(clientes),
        )

    def test_formato_rut_en_identificador_tributario(self):
        sin_puntos, _ = self.generar(
            cantidad=10,
            campos=CAMPOS_TRANSACCION,
            formato_rut=FORMATO_RUT_SIN_PUNTOS,
        )
        for registro in sin_puntos:
            self.assertNotIn(".", registro["identificador_tributario"])
            self.assertIn("-", registro["identificador_tributario"])
            self.assertTrue(validar(registro["identificador_tributario"]))

        sin_separadores, _ = self.generar(
            cantidad=10,
            campos=CAMPOS_TRANSACCION,
            formato_rut=FORMATO_RUT_SIN_SEPARADORES,
        )
        for registro in sin_separadores:
            self.assertNotIn(".", registro["identificador_tributario"])
            self.assertNotIn("-", registro["identificador_tributario"])
            self.assertTrue(validar(registro["identificador_tributario"]))

    def test_semilla_automatica_en_opciones(self):
        primero, semilla = self.generar(
            cantidad=5, semilla=None, campos=("rut", "nombre")
        )
        self.assertIsInstance(semilla, int)
        segundo, _ = self.generar(
            cantidad=5, semilla=semilla, campos=("rut", "nombre")
        )
        self.assertEqual(primero, segundo)

    def test_limite_de_fechas_es_aceptado(self):
        registros, _ = self.generar(
            cantidad=3,
            campos=("fecha_registro", "fecha_nacimiento", "edad"),
            fecha_desde=FECHA_LIMITE_MINIMA,
            fecha_hasta=FECHA_LIMITE_MINIMA,
        )
        self.assertEqual(len(registros), 3)
        for registro in registros:
            self.assertEqual(
                registro["fecha_registro"], FECHA_LIMITE_MINIMA.isoformat()
            )
            self.assertGreaterEqual(registro["edad"], EDAD_MINIMA)


if __name__ == "__main__":
    unittest.main()
