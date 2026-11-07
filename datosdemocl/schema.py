"""Contrato de campos disponibles en los registros."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Campo:
    clave: str
    etiqueta: str
    descripcion: str
    por_defecto: bool = False


CAMPOS_INFO: tuple[Campo, ...] = (
    Campo(
        "id_prueba",
        "ID de registro",
        "Identificador secuencial del lote.",
        True,
    ),
    Campo("nombre", "Nombre", "Nombre ficticio de la lista local.", True),
    Campo("apellido", "Apellido", "Apellido ficticio de la lista local.", True),
    Campo(
        "nombre_completo",
        "Nombre completo",
        "Nombre y apellido en una sola columna.",
    ),
    Campo(
        "rut",
        "RUT",
        "RUT ficticio de la fila; único en el lote y con dígito verificador calculado.",
        True,
    ),
    Campo(
        "correo",
        "Correo",
        "Correo bajo un dominio reservado .test.",
        True,
    ),
    Campo("region", "Región", "Región del catálogo local.", True),
    Campo(
        "comuna",
        "Comuna",
        "Comuna coherente con la región.",
        True,
    ),
    Campo(
        "fecha_registro",
        "Fecha de registro",
        "Fecha ISO simulada, dentro del rango elegido.",
        True,
    ),
    Campo(
        "fecha_nacimiento",
        "Fecha de nacimiento",
        "Fecha ISO simulada de una persona adulta.",
    ),
    Campo(
        "edad",
        "Edad",
        "Edad calculada a la fecha de registro.",
    ),
    Campo(
        "monto_clp",
        "Monto CLP",
        "Monto entero simulado en pesos chilenos.",
        True,
    ),
    Campo(
        "estado",
        "Estado",
        "Estado ficticio para probar filtros y formularios.",
    ),
    Campo(
        "categoria",
        "Categoría",
        "Categoría ficticia de ejemplo.",
    ),
    Campo(
        "descuento_pct",
        "Descuento (%)",
        "Porcentaje entero de 0 a 50, múltiplo de 5.",
    ),
    # Sábana de transacciones y pagos. Estos campos se calculan con un flujo
    # aleatorio independiente para no alterar las 15 columnas anteriores.
    Campo(
        "fecha_hora_transaccion",
        "Fecha y hora transacción",
        "Fecha y hora simuladas de la transacción.",
    ),
    Campo(
        "cliente_interno",
        "Cliente interno",
        "Código interno del cliente; se reutiliza entre transacciones.",
    ),
    Campo(
        "idventa",
        "ID venta",
        "Identificador único de la venta.",
    ),
    Campo(
        "monto_total",
        "Monto total",
        "Total de la venta en CLP; coincide con monto_clp si ambos se incluyen.",
    ),
    Campo(
        "tipo_documento_pago",
        "Tipo documento de pago",
        "Tipo de documento asociado al pago.",
    ),
    Campo(
        "id_chipax",
        "ID Chipax",
        "Identificador único de la venta en Chipax.",
    ),
    Campo(
        "pasarela_pago",
        "Pasarela de pago",
        "Medio o pasarela usada para el pago.",
    ),
    Campo(
        "identificador_tributario",
        "Identificador tributario",
        "RUT ficticio estable del cliente; úsalo junto con cliente_interno para unir sus ventas.",
    ),
    Campo(
        "chipax_sale_note_folio",
        "Folio nota de venta Chipax",
        "Folio único extraído del origen dp.extra_json->>'$.chipaxSaleNoteFolio'.",
    ),
    Campo(
        "idpayment_sale",
        "ID payment sale",
        "Identificador único del pago en la pasarela.",
    ),
    Campo(
        "estado_transaccion",
        "Estado transacción",
        "Estado simulado de la transacción.",
    ),
    Campo(
        "canal_venta",
        "Canal de venta",
        "Canal por donde se originó la venta.",
    ),
    Campo("tipo_cliente", "Tipo de cliente", "Persona o empresa ficticia."),
    Campo(
        "empresa",
        "Empresa",
        "Nombre ficticio; sólo se llena para clientes Empresa. Filtra ese tipo para evitar vacíos.",
    ),
    Campo(
        "segmento_cliente",
        "Segmento de cliente",
        "Segmento local de ejemplo: retail, pyme o corporativo.",
    ),
    Campo(
        "estado_cliente",
        "Estado del cliente",
        "Estado simulado de la relación con el cliente.",
    ),
    Campo(
        "fecha_alta",
        "Fecha de alta",
        "Fecha de alta simulada, estable por cliente.",
    ),
    Campo("producto", "Producto o servicio", "Producto local de catálogo demo."),
    Campo("sku", "SKU", "Código de producto prefijado con SKU-DEMO."),
    Campo(
        "categoria_producto",
        "Categoría de producto",
        "Categoría del producto seleccionado del catálogo demo.",
    ),
    Campo("cantidad", "Cantidad", "Unidades de la línea de venta (1 a 5)."),
    Campo(
        "precio_unitario_clp",
        "Precio unitario neto",
        "Precio neto; cantidad por precio coincide con el subtotal neto.",
    ),
    Campo(
        "subtotal_neto_clp",
        "Subtotal neto",
        "Cantidad por precio unitario, antes del IVA simulado.",
    ),
    Campo(
        "tasa_iva_pct",
        "Tasa IVA aplicada (%)",
        "Tasa simulada aplicada; 0 para documento exento.",
    ),
    Campo(
        "iva_clp",
        "IVA simulado",
        "Impuesto calculado con la tasa elegida para el lote.",
    ),
    Campo(
        "estado_pago",
        "Estado de pago",
        "Estado derivado de la transacción simulada.",
    ),
    Campo(
        "estado_pedido",
        "Estado del pedido",
        "Estado logístico derivado de la transacción simulada.",
    ),
    Campo(
        "fecha_entrega_estimada",
        "Entrega estimada",
        "Fecha futura para pedidos aprobados; vacía si el pago está pendiente, rechazado o reembolsado.",
    ),
    Campo("moneda", "Moneda", "Moneda del lote; por defecto CLP."),
)

CAMPOS_DISPONIBLES: tuple[str, ...] = tuple(campo.clave for campo in CAMPOS_INFO)
CAMPOS_POR_DEFECTO: tuple[str, ...] = tuple(
    campo.clave for campo in CAMPOS_INFO if campo.por_defecto
)
CAMPOS_TRANSACCION: tuple[str, ...] = (
    "fecha_hora_transaccion",
    "cliente_interno",
    "idventa",
    "monto_total",
    "tipo_documento_pago",
    "id_chipax",
    "pasarela_pago",
    "identificador_tributario",
    "chipax_sale_note_folio",
    "idpayment_sale",
    "estado_transaccion",
    "canal_venta",
)
GRUPO_CLIENTES: tuple[str, ...] = (
    "tipo_cliente",
    "empresa",
    "segmento_cliente",
    "estado_cliente",
    "fecha_alta",
)
GRUPO_COMERCIO: tuple[str, ...] = (
    "producto",
    "sku",
    "categoria_producto",
    "cantidad",
    "precio_unitario_clp",
    "subtotal_neto_clp",
    "tasa_iva_pct",
    "iva_clp",
    "estado_pago",
    "estado_pedido",
    "fecha_entrega_estimada",
    "moneda",
)
PRESETS: dict[str, tuple[str, ...]] = {
    "base": CAMPOS_POR_DEFECTO,
    "sabana_ventas": (
        "fecha_hora_transaccion",
        "cliente_interno",
        "idventa",
        "monto_total",
        "tipo_documento_pago",
        "id_chipax",
        "pasarela_pago",
        "identificador_tributario",
        "chipax_sale_note_folio",
        "idpayment_sale",
    ),
    "transacciones": CAMPOS_TRANSACCION,
    "clientes": (
        "id_prueba",
        "nombre_completo",
        "rut",
        "correo",
        "region",
        "comuna",
        *GRUPO_CLIENTES,
    ),
    "comercio_demo": (*CAMPOS_TRANSACCION, *GRUPO_CLIENTES, *GRUPO_COMERCIO),
    "completo": CAMPOS_DISPONIBLES,
}
ETIQUETAS_PRESETS: dict[str, str] = {
    "base": "Base (9 columnas)",
    "sabana_ventas": "Sábana de ventas (10 campos)",
    "transacciones": "Transacciones (12 campos)",
    "clientes": "Clientes (11 campos)",
    "comercio_demo": "Comercio completo (29 campos)",
    "completo": f"Completo ({len(CAMPOS_DISPONIBLES)} campos)",
}
ETIQUETAS: dict[str, str] = {campo.clave: campo.etiqueta for campo in CAMPOS_INFO}
DESCRIPCIONES: dict[str, str] = {
    campo.clave: campo.descripcion for campo in CAMPOS_INFO
}


def campos_de_preset(nombre: str) -> tuple[str, ...]:
    """Devuelve las columnas de un preset y rechaza nombres desconocidos."""
    try:
        return PRESETS[nombre]
    except KeyError as exc:
        raise ValueError(
            f"Perfil desconocido: {nombre}. "
            f"Disponibles: {', '.join(PRESETS)}."
        ) from exc


def normalizar_campos(campos: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """Valida una selección de campos y conserva el orden solicitado."""
    if not campos:
        raise ValueError("Debe seleccionar al menos una columna.")

    normalizados: list[str] = []
    vistos: set[str] = set()
    for campo in campos:
        if not isinstance(campo, str):
            raise ValueError("Los nombres de columna deben ser texto.")
        clave = campo.strip()
        if not clave:
            raise ValueError("Hay un nombre de columna vacío.")
        if clave not in CAMPOS_DISPONIBLES:
            raise ValueError(
                f"Columna desconocida: {clave}. "
                f"Disponibles: {', '.join(CAMPOS_DISPONIBLES)}."
            )
        if clave in vistos:
            raise ValueError(f"La columna {clave} está repetida.")
        vistos.add(clave)
        normalizados.append(clave)
    return tuple(normalizados)
