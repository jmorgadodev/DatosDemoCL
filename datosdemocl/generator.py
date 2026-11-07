"""Generación determinista de registros sintéticos de prueba."""

from __future__ import annotations

import random
import re
import secrets
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta

from .catalog import APELLIDOS, EMPRESAS_DEMO, NOMBRES, PRODUCTOS_DEMO, REGIONES
from .rut import calcular_dv, formatear_cuerpo
from .schema import CAMPOS_POR_DEFECTO, normalizar_campos

MIN_REGISTROS = 1
MAX_REGISTROS = 10_000

# Rango documentado para las fechas simuladas.
FECHA_MINIMA = date(2023, 1, 1)
FECHA_MAXIMA = date(2025, 12, 31)

# Límites amplios para que una fecha elegida por el usuario sea interpretable
# y permita calcular una fecha de nacimiento sin desbordar el calendario.
FECHA_LIMITE_MINIMA = date(1900, 1, 1)
FECHA_LIMITE_MAXIMA = date(2100, 12, 31)

# Los campos opcionales de nacimiento/edad representan personas adultas.
EDAD_MINIMA = 18
EDAD_MAXIMA = 80

# Montos simulados en pesos chilenos, enteros.
MONTO_MINIMO = 1_000
MONTO_MAXIMO = 5_000_000
PASO_MONTO = 100

DOMINIO_CORREO = "ejemplo.test"

# No existe un rango oficial de RUT reservado para pruebas. Se usan cuerpos
# altos para reducir --sin eliminar-- la probabilidad de coincidir con un RUT
# ya emitido a una persona real.
CUERPO_MINIMO_GENERADO = 50_000_000
CUERPO_MAXIMO_GENERADO = 99_999_999
INTENTOS_POR_CUERPO = 10_000

FORMATO_RUT_CON_PUNTOS = "con_puntos"
FORMATO_RUT_SIN_PUNTOS = "sin_puntos"
FORMATO_RUT_SIN_SEPARADORES = "sin_separadores"
FORMATOS_RUT = (
    FORMATO_RUT_CON_PUNTOS,
    FORMATO_RUT_SIN_PUNTOS,
    FORMATO_RUT_SIN_SEPARADORES,
)

ESTADOS = ("Activo", "Inactivo", "Pendiente")
CATEGORIAS = ("Básica", "Estándar", "Premium")
DESCUENTO_MINIMO = 0
DESCUENTO_MAXIMO = 50
PASO_DESCUENTO = 5

DOMINIO_RE = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+test$"
)

REGIONES_MAPA = {nombre: comunas for nombre, comunas in REGIONES}

# Valores ficticios de la sábana de transacciones y pagos.
TIPOS_DOCUMENTO_PAGO = (
    "Boleta electrónica",
    "Factura electrónica",
    "Boleta exenta",
    "Nota de venta",
)
PESOS_TIPO_DOCUMENTO = (55, 30, 10, 5)
TIPOS_CLIENTE = ("Persona", "Empresa")
PESOS_TIPO_CLIENTE = (75, 25)
PASARELAS_PAGO = (
    "Webpay",
    "Mercado Pago",
    "Flow",
    "Khipu",
    "Transferencia",
    "Efectivo",
)
ESTADOS_TRANSACCION = ("Aprobada", "Pendiente", "Rechazada", "Reversada")
PESOS_ESTADO_TRANSACCION = (78, 10, 8, 4)
ESTADOS_PAGO = ("Aprobado", "Pendiente", "Rechazado", "Reembolsado")
ESTADO_PAGO_A_TRANSACCION = dict(zip(ESTADOS_PAGO, ESTADOS_TRANSACCION))
CANALES_VENTA = ("Web", "App", "Tienda", "Call center", "Marketplace")
PESOS_CANAL_VENTA = (40, 25, 20, 10, 5)

# Rango de folios de la nota de venta. El valor inicial se elige con la
# semilla de transacciones y cada fila recibe un folio consecutivo único.
FOLIO_BASE_MINIMO = 100_000
FOLIO_BASE_MAXIMO = 899_999

# Máximo de clientes distintos en un lote. Mantiene la reutilización de
# clientes incluso en lotes grandes y acota el trabajo de la GUI y la CLI.
MAX_CLIENTES = 50

# Alias de compatibilidad con la versión 0.1.x.
CAMPOS = CAMPOS_POR_DEFECTO


class GenerationError(ValueError):
    """Parámetros inválidos para generar un lote."""


@dataclass(frozen=True)
class OpcionesGeneracion:
    """Configuración completa de un lote sintético."""

    cantidad: int
    semilla: int | None = None
    campos: tuple[str, ...] = CAMPOS_POR_DEFECTO
    formato_rut: str = FORMATO_RUT_CON_PUNTOS
    region: str | None = None
    comuna: str | None = None
    fecha_desde: date = FECHA_MINIMA
    fecha_hasta: date = FECHA_MAXIMA
    monto_min: int = MONTO_MINIMO
    monto_max: int = MONTO_MAXIMO
    monto_paso: int = PASO_MONTO
    iva_pct: int = 19
    estados_pago: tuple[str, ...] = ESTADOS_PAGO
    tipos_cliente: tuple[str, ...] = TIPOS_CLIENTE
    tipos_documento_pago: tuple[str, ...] = TIPOS_DOCUMENTO_PAGO
    pasarelas_pago: tuple[str, ...] = PASARELAS_PAGO
    canales_venta: tuple[str, ...] = CANALES_VENTA
    dominio_correo: str = DOMINIO_CORREO

    def validar(self) -> tuple[str, ...]:
        """Valida la configuración y devuelve las columnas normalizadas."""
        _validar_cantidad(self.cantidad)
        _validar_semilla(self.semilla)

        try:
            campos = normalizar_campos(self.campos)
        except ValueError as exc:
            raise GenerationError(str(exc)) from exc

        if self.formato_rut not in FORMATOS_RUT:
            raise GenerationError(
                f"Formato de RUT inválido: {self.formato_rut}. "
                f"Opciones: {', '.join(FORMATOS_RUT)}."
            )

        if type(self.fecha_desde) is not date or type(self.fecha_hasta) is not date:
            raise GenerationError("Las fechas deben ser fechas sin hora.")
        if self.fecha_desde > self.fecha_hasta:
            raise GenerationError(
                "La fecha inicial no puede ser posterior a la fecha final."
            )
        if not (
            FECHA_LIMITE_MINIMA <= self.fecha_desde <= FECHA_LIMITE_MAXIMA
            and FECHA_LIMITE_MINIMA <= self.fecha_hasta <= FECHA_LIMITE_MAXIMA
        ):
            raise GenerationError(
                "Las fechas deben estar entre "
                f"{FECHA_LIMITE_MINIMA.isoformat()} y "
                f"{FECHA_LIMITE_MAXIMA.isoformat()}."
            )

        _validar_rango_montos(
            self.monto_min, self.monto_max, self.monto_paso
        )
        if (
            isinstance(self.iva_pct, bool)
            or not isinstance(self.iva_pct, int)
            or not 0 <= self.iva_pct <= 100
        ):
            raise GenerationError("La tasa de IVA debe ser un entero entre 0 y 100.")
        for nombre, seleccion, permitidos in (
            ("estados de pago", self.estados_pago, ESTADOS_PAGO),
            ("tipos de cliente", self.tipos_cliente, TIPOS_CLIENTE),
            (
                "tipos de documento",
                self.tipos_documento_pago,
                TIPOS_DOCUMENTO_PAGO,
            ),
            ("pasarelas de pago", self.pasarelas_pago, PASARELAS_PAGO),
            ("canales de venta", self.canales_venta, CANALES_VENTA),
        ):
            if (
                not isinstance(seleccion, tuple)
                or not seleccion
                or any(not isinstance(valor, str) for valor in seleccion)
            ):
                raise GenerationError(f"Seleccione al menos un valor para {nombre}.")
            if len(set(seleccion)) != len(seleccion) or any(
                valor not in permitidos for valor in seleccion
            ):
                raise GenerationError(f"La selección de {nombre} no es válida.")
        _validar_region_comuna(self.region, self.comuna)
        _validar_dominio(self.dominio_correo)
        return campos


def _sin_acentos(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFKD", texto)
    return descompuesto.encode("ascii", "ignore").decode("ascii").lower()


def _validar_cantidad(cantidad: int) -> None:
    if isinstance(cantidad, bool) or not isinstance(cantidad, int):
        raise GenerationError("La cantidad de registros debe ser un número entero.")
    if cantidad < MIN_REGISTROS:
        raise GenerationError(f"La cantidad debe ser al menos {MIN_REGISTROS}.")
    if cantidad > MAX_REGISTROS:
        raise GenerationError(
            f"La cantidad no puede superar el máximo de {MAX_REGISTROS} registros."
        )


def _validar_semilla(semilla: int | None) -> None:
    if semilla is None:
        return
    if isinstance(semilla, bool) or not isinstance(semilla, int):
        raise GenerationError("La semilla debe ser un número entero.")


def _validar_rango_montos(minimo: int, maximo: int, paso: int) -> None:
    for nombre, valor in (
        ("El monto mínimo", minimo),
        ("El monto máximo", maximo),
        ("El paso de monto", paso),
    ):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise GenerationError(f"{nombre} debe ser un número entero.")
    if minimo < 1:
        raise GenerationError("El monto mínimo debe ser mayor que cero.")
    if maximo < minimo:
        raise GenerationError(
            "El monto máximo no puede ser menor que el monto mínimo."
        )
    if paso < 1:
        raise GenerationError("El paso de monto debe ser mayor que cero.")
    if _limites_monto(minimo, maximo, paso) is None:
        raise GenerationError(
            "El rango de montos no contiene ningún valor múltiplo del paso."
        )


def _limites_monto(minimo: int, maximo: int, paso: int) -> tuple[int, int] | None:
    primero = ((minimo + paso - 1) // paso) * paso
    ultimo = (maximo // paso) * paso
    if primero > ultimo:
        return None
    return primero // paso, ultimo // paso


def _validar_region_comuna(
    region: str | None, comuna: str | None
) -> tuple[str | None, str | None]:
    if region is not None and not isinstance(region, str):
        raise GenerationError("La región debe ser texto.")
    if comuna is not None and not isinstance(comuna, str):
        raise GenerationError("La comuna debe ser texto.")

    region_limpia = (region or "").strip() or None
    comuna_limpia = (comuna or "").strip() or None

    if comuna_limpia is not None and region_limpia is None:
        raise GenerationError(
            "Para filtrar por comuna también debe indicar la región."
        )
    if region_limpia is not None and region_limpia not in REGIONES_MAPA:
        raise GenerationError(f"Región desconocida: {region_limpia}.")
    if (
        comuna_limpia is not None
        and region_limpia is not None
        and comuna_limpia not in REGIONES_MAPA[region_limpia]
    ):
        raise GenerationError(
            f"La comuna {comuna_limpia} no pertenece a la región "
            f"{region_limpia}."
        )
    return region_limpia, comuna_limpia


def _validar_dominio(dominio: str) -> str:
    if not isinstance(dominio, str):
        raise GenerationError("El dominio de correo debe ser texto.")
    limpio = dominio.strip().lower()
    if not DOMINIO_RE.fullmatch(limpio):
        raise GenerationError(
            "El dominio de correo debe terminar en .test y tener un formato "
            "válido (por ejemplo, ejemplo.test)."
        )
    return limpio


def _calcular_edad(nacimiento: date, referencia: date) -> int:
    edad = referencia.year - nacimiento.year
    if (referencia.month, referencia.day) < (nacimiento.month, nacimiento.day):
        edad -= 1
    return edad


def _restar_anios(fecha: date, anios: int) -> date:
    """Resta años ajustando el 29 de febrero a un día válido."""
    try:
        return fecha.replace(year=fecha.year - anios)
    except ValueError:
        return fecha.replace(year=fecha.year - anios, day=28)


def _formatear_rut(cuerpo: int, formato: str) -> str:
    dv = calcular_dv(cuerpo)
    if formato == FORMATO_RUT_CON_PUNTOS:
        return f"{formatear_cuerpo(cuerpo)}-{dv}"
    if formato == FORMATO_RUT_SIN_PUNTOS:
        return f"{cuerpo}-{dv}"
    return f"{cuerpo}{dv}"


def _elegir_ponderado(
    rng: random.Random,
    opciones: tuple[str, ...],
    pesos: tuple[int, ...],
) -> str:
    """Elige una opción con pesos enteros, de forma determinista."""
    total = sum(pesos)
    punto = rng.randrange(total)
    acumulado = 0
    for opcion, peso in zip(opciones, pesos):
        acumulado += peso
        if punto < acumulado:
            return opcion
    return opciones[-1]


def _elegir_pasarela(
    rng: random.Random,
    tipo_documento: str,
    seleccionadas: tuple[str, ...] = PASARELAS_PAGO,
) -> str:
    """Elige una pasarela coherente con el tipo de documento."""
    if tipo_documento == "Factura electrónica":
        preferencias, pesos = ("Transferencia", "Webpay", "Flow"), (60, 30, 10)
    elif tipo_documento == "Boleta exenta":
        preferencias, pesos = ("Efectivo", "Webpay", "Mercado Pago"), (50, 30, 20)
    else:
        preferencias, pesos = (
            ("Webpay", "Mercado Pago", "Flow", "Khipu", "Efectivo"),
            (30, 25, 20, 15, 10),
        )
    filtradas = tuple(
        (valor, peso)
        for valor, peso in zip(preferencias, pesos)
        if valor in seleccionadas
    )
    if not filtradas:
        return rng.choice(seleccionadas)
    return _elegir_ponderado(
        rng,
        tuple(valor for valor, _ in filtradas),
        tuple(peso for _, peso in filtradas),
    )


def _elegir_canal(
    rng: random.Random,
    pasarela: str,
    seleccionados: tuple[str, ...] = CANALES_VENTA,
) -> str:
    """Elige un canal de venta coherente con el medio de pago."""
    if pasarela == "Efectivo":
        preferencias, pesos = ("Tienda", "Marketplace"), (80, 20)
    elif pasarela == "Transferencia":
        preferencias, pesos = ("Web", "Call center", "App"), (50, 30, 20)
    else:
        preferencias, pesos = CANALES_VENTA, PESOS_CANAL_VENTA
    filtrados = tuple(
        (valor, peso)
        for valor, peso in zip(preferencias, pesos)
        if valor in seleccionados
    )
    if not filtrados:
        return rng.choice(seleccionados)
    return _elegir_ponderado(
        rng,
        tuple(valor for valor, _ in filtrados),
        tuple(peso for _, peso in filtrados),
    )


def _numero_clientes(cantidad: int) -> int:
    """Cantidad de clientes distintos para que exista reutilización."""
    return max(1, min(MAX_CLIENTES, (cantidad + 2) // 3))


def _generar_clientes(
    cantidad: int,
    formato_rut: str,
    rng: random.Random,
    cuerpos_reservados: set[int],
) -> list[tuple[str, str]]:
    """Crea clientes estables con un RUT tributario ficticio y único."""
    usados = set(cuerpos_reservados)
    clientes: list[tuple[str, str]] = []
    for posicion in range(1, cantidad + 1):
        intentos = 0
        while True:
            cuerpo = rng.randint(
                CUERPO_MINIMO_GENERADO, CUERPO_MAXIMO_GENERADO
            )
            if cuerpo not in usados:
                usados.add(cuerpo)
                break
            intentos += 1
            if intentos >= INTENTOS_POR_CUERPO:
                raise GenerationError(
                    "No fue posible generar un identificador tributario "
                    "único para el lote; intente con otra semilla."
                )
        clientes.append(
            (
                f"CLI-{posicion:06d}",
                _formatear_rut(cuerpo, formato_rut),
            )
        )
    return clientes


def _generar_completos(
    opciones: OpcionesGeneracion, semilla_usada: int
) -> list[dict[str, object]]:
    """Genera todos los campos, aunque luego se exporte un subconjunto."""
    campos = opciones.validar()
    region_fija, comuna_fija = _validar_region_comuna(
        opciones.region, opciones.comuna
    )
    dominio = _validar_dominio(opciones.dominio_correo)
    limites = _limites_monto(
        opciones.monto_min, opciones.monto_max, opciones.monto_paso
    )
    if limites is None:  # ya validado, se mantiene por seguridad
        raise GenerationError("El rango de montos no es válido.")
    monto_indice_min, monto_indice_max = limites

    # El flujo principal conserva el orden de la versión 0.1.x. Los campos
    # adicionales usan flujos independientes para no alterar los datos base.
    rng = random.Random(semilla_usada)
    rng_extra = random.Random(semilla_usada ^ 0x5DEECE66D)
    rng_trans = random.Random(semilla_usada ^ 0x9E3779B9)
    rng_demo = random.Random(semilla_usada ^ 0xDADA2026)

    numero_clientes = _numero_clientes(opciones.cantidad)
    limite_fecha_alta = min(opciones.fecha_desde, date(1990, 1, 1))
    perfiles_cliente: list[tuple[str, str, str, str, str]] = []
    for _ in range(numero_clientes):
        tipo_cliente = _elegir_ponderado(
            rng_demo,
            opciones.tipos_cliente,
            tuple(
                PESOS_TIPO_CLIENTE[TIPOS_CLIENTE.index(valor)]
                for valor in opciones.tipos_cliente
            ),
        )
        perfiles_cliente.append(
            (
                tipo_cliente,
                rng_demo.choice(EMPRESAS_DEMO) if tipo_cliente == "Empresa" else "",
                rng_demo.choice(("Retail", "Emprendimiento", "Pyme", "Corporativo")),
                rng_demo.choice(("Activo", "Nuevo", "Inactivo")),
                date.fromordinal(
                    rng_demo.randint(
                        FECHA_LIMITE_MINIMA.toordinal(),
                        limite_fecha_alta.toordinal(),
                    )
                ).isoformat(),
            )
        )
    folio_base = rng_trans.randrange(
        FOLIO_BASE_MINIMO, FOLIO_BASE_MAXIMO + 1
    )

    usados: set[int] = set()
    clientes_fila: list[int] = []
    registros: list[dict[str, object]] = []

    for indice in range(1, opciones.cantidad + 1):
        intentos = 0
        while True:
            cuerpo = rng.randint(CUERPO_MINIMO_GENERADO, CUERPO_MAXIMO_GENERADO)
            if cuerpo not in usados:
                usados.add(cuerpo)
                break
            intentos += 1
            if intentos >= INTENTOS_POR_CUERPO:
                raise GenerationError(
                    "No fue posible generar un RUT único para el lote; "
                    "intente con otra semilla o una cantidad menor."
                )

        nombre = rng.choice(NOMBRES)
        apellido = rng.choice(APELLIDOS)

        if comuna_fija is not None:
            region = region_fija
            comuna = comuna_fija
        elif region_fija is not None:
            region = region_fija
            comunas = REGIONES_MAPA[region]
            comuna = comunas[rng.randrange(len(comunas))]
        else:
            region, comunas = REGIONES[rng.randrange(len(REGIONES))]
            comuna = comunas[rng.randrange(len(comunas))]

        fecha = date.fromordinal(
            rng.randint(
                opciones.fecha_desde.toordinal(),
                opciones.fecha_hasta.toordinal(),
            )
        )
        monto = rng.randint(monto_indice_min, monto_indice_max) * opciones.monto_paso

        edad = rng_extra.randint(EDAD_MINIMA, EDAD_MAXIMA)
        nacimiento = _restar_anios(fecha, edad)

        cliente_idx = rng_trans.randrange(numero_clientes)
        clientes_fila.append(cliente_idx)
        hora = rng_trans.randrange(24)
        minuto = rng_trans.randrange(60)
        segundo = rng_trans.randrange(60)
        tipo_documento = _elegir_ponderado(
            rng_trans,
            opciones.tipos_documento_pago,
            tuple(
                PESOS_TIPO_DOCUMENTO[TIPOS_DOCUMENTO_PAGO.index(valor)]
                for valor in opciones.tipos_documento_pago
            ),
        )
        pasarela = _elegir_pasarela(
            rng_trans, tipo_documento, opciones.pasarelas_pago
        )
        canal = _elegir_canal(rng_trans, pasarela, opciones.canales_venta)
        estado_pago = _elegir_ponderado(
            rng_trans,
            opciones.estados_pago,
            tuple(
                PESOS_ESTADO_TRANSACCION[ESTADOS_PAGO.index(valor)]
                for valor in opciones.estados_pago
            ),
        )
        estado_transaccion = ESTADO_PAGO_A_TRANSACCION[estado_pago]
        sku, producto, categoria_producto = rng_demo.choice(PRODUCTOS_DEMO)
        tasa_iva = (
            0 if tipo_documento == "Boleta exenta" else opciones.iva_pct
        )
        divisor_iva = 100 + tasa_iva
        subtotal_neto = (monto * 100 + divisor_iva // 2) // divisor_iva
        iva = monto - subtotal_neto
        cantidades = [
            cantidad
            for cantidad in range(1, 6)
            if subtotal_neto % cantidad == 0
        ]
        cantidad = rng_demo.choice(cantidades)
        estado_pedido = {
            "Aprobada": rng_demo.choice(("En preparación", "Despachado", "Entregado")),
            "Pendiente": "En preparación",
            "Rechazada": "No procesado",
            "Reversada": "Devuelto",
        }[estado_transaccion]
        fecha_entrega = (
            (fecha + timedelta(days=rng_demo.randint(1, 6))).isoformat()
            if estado_transaccion == "Aprobada"
            else ""
        )

        local = f"{_sin_acentos(nombre)}.{_sin_acentos(apellido)}{indice:04d}"
        registros.append(
            {
                "id_prueba": f"DEMO-{indice:06d}",
                "nombre": nombre,
                "apellido": apellido,
                "nombre_completo": f"{nombre} {apellido}",
                "rut": _formatear_rut(cuerpo, opciones.formato_rut),
                "correo": f"{local}@{dominio}",
                "region": region,
                "comuna": comuna,
                "fecha_registro": fecha.isoformat(),
                "fecha_nacimiento": nacimiento.isoformat(),
                "edad": _calcular_edad(nacimiento, fecha),
                "monto_clp": monto,
                "estado": rng_extra.choice(ESTADOS),
                "categoria": rng_extra.choice(CATEGORIAS),
                "descuento_pct": rng_extra.randrange(
                    DESCUENTO_MINIMO,
                    DESCUENTO_MAXIMO + 1,
                    PASO_DESCUENTO,
                ),
                "fecha_hora_transaccion": (
                    f"{fecha.isoformat()} "
                    f"{hora:02d}:{minuto:02d}:{segundo:02d}"
                ),
                "cliente_interno": "",
                "idventa": f"VTA-{indice:06d}",
                "monto_total": monto,
                "tipo_documento_pago": tipo_documento,
                "id_chipax": f"CHX-{indice:06d}",
                "pasarela_pago": pasarela,
                "identificador_tributario": "",
                "chipax_sale_note_folio": folio_base + indice,
                "idpayment_sale": f"PAG-{indice:06d}",
                "estado_transaccion": estado_transaccion,
                "canal_venta": canal,
                "tipo_cliente": "",
                "empresa": "",
                "segmento_cliente": "",
                "estado_cliente": "",
                "fecha_alta": "",
                "producto": producto,
                "sku": sku,
                "categoria_producto": categoria_producto,
                "cantidad": cantidad,
                "precio_unitario_clp": subtotal_neto // cantidad,
                "subtotal_neto_clp": subtotal_neto,
                "tasa_iva_pct": tasa_iva,
                "iva_clp": iva,
                "estado_pago": estado_pago,
                "estado_pedido": estado_pedido,
                "fecha_entrega_estimada": fecha_entrega,
                "moneda": "CLP",
            }
        )

    clientes = _generar_clientes(
        numero_clientes, opciones.formato_rut, rng_trans, usados
    )
    for registro, cliente_idx in zip(registros, clientes_fila):
        cliente_interno, identificador = clientes[cliente_idx]
        tipo, empresa, segmento, estado_cliente, fecha_alta = perfiles_cliente[cliente_idx]
        registro["cliente_interno"] = cliente_interno
        registro["identificador_tributario"] = identificador
        registro["tipo_cliente"] = tipo
        registro["empresa"] = empresa
        registro["segmento_cliente"] = segmento
        registro["estado_cliente"] = estado_cliente
        registro["fecha_alta"] = fecha_alta

    # La validación de campos ya se hizo; se repite aquí para devolver la
    # selección en el orden solicitado.
    seleccionados = normalizar_campos(campos)
    return [
        {campo: registro[campo] for campo in seleccionados}
        for registro in registros
    ]


def generar_lote(
    opciones: OpcionesGeneracion,
) -> tuple[list[dict[str, object]], int]:
    """Genera un lote según una configuración completa.

    Devuelve ``(registros, semilla_usada)``. Los registros contienen sólo las
    columnas seleccionadas, en el orden solicitado.
    """
    if not isinstance(opciones, OpcionesGeneracion):
        raise GenerationError("Se esperaba una configuración OpcionesGeneracion.")
    campos = opciones.validar()
    semilla_usada = (
        opciones.semilla if opciones.semilla is not None else secrets.randbits(32)
    )
    registros = _generar_completos(opciones, semilla_usada)
    return registros, semilla_usada


def generar_registros(
    cantidad: int, semilla: int | None = None
) -> tuple[list[dict[str, object]], int]:
    """Genera un lote con la configuración por defecto (compatibilidad).

    Devuelve ``(registros, semilla_usada)``. Si no se entrega una semilla, se
    elige una automáticamente y se informa para poder reproducir el lote.
    """
    return generar_lote(
        OpcionesGeneracion(cantidad=cantidad, semilla=semilla)
    )
