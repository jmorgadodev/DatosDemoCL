"""Interfaz de línea de comandos de DatosDemoCL."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from typing import Sequence

from . import __version__
from .exporters import ExportError, exportar_csv, exportar_json
from .generator import (
    DOMINIO_CORREO,
    FECHA_MAXIMA,
    FECHA_MINIMA,
    FORMATOS_RUT,
    MAX_REGISTROS,
    MIN_REGISTROS,
    MONTO_MAXIMO,
    MONTO_MINIMO,
    PASO_MONTO,
    CANALES_VENTA,
    ESTADOS_PAGO,
    PASARELAS_PAGO,
    TIPOS_CLIENTE,
    TIPOS_DOCUMENTO_PAGO,
    GenerationError,
    OpcionesGeneracion,
    generar_lote,
)
from .rut import RutError, validar_o_error
from .schema import (
    CAMPOS_DISPONIBLES,
    CAMPOS_POR_DEFECTO,
    PRESETS,
    campos_de_preset,
    normalizar_campos,
)

ADVERTENCIA = (
    "un RUT matemáticamente válido no garantiza una identidad ficticia: "
    "puede coincidir con el RUT de una persona real. Use estos datos sólo "
    "para pruebas y no los presente como información anonimizada."
)

EJEMPLOS = """\
ejemplos:
  python -m datosdemocl gui
  python -m datosdemocl generar --cantidad 25 --formato csv --salida .\\ejemplos\\mi_lote.csv --semilla 2026
  python -m datosdemocl generar --cantidad 100 --formato csv --salida .\\ejemplos\\sabana.csv --semilla 2026 --perfil sabana_ventas
  python -m datosdemocl generar --cantidad 25 --formato csv --salida .\\ejemplos\\transacciones.csv --semilla 2026 --perfil transacciones
  python -m datosdemocl generar --cantidad 500 --formato csv --salida .\\ejemplos\\mi_lote.csv --semilla 42 --campos rut,nombre,correo,region,estado,monto_clp --formato-rut sin_puntos --region "Biobío"
  python -m datosdemocl generar --cantidad 25 --formato json --salida .\\ejemplos\\mi_lote.json --semilla 2026
  python -m datosdemocl validar-rut 12.345.678-5
"""


class _ErrorDeUso(Exception):
    """Error de argumentos que debe terminar con código 2."""


def _parse_fecha(texto: str) -> date:
    try:
        return date.fromisoformat(texto)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Fecha inválida: {texto}. Use el formato AAAA-MM-DD."
        ) from exc


def _parse_campos(texto: str) -> tuple[str, ...]:
    partes = tuple(parte.strip() for parte in texto.split(",") if parte.strip())
    try:
        return normalizar_campos(partes)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _parse_valores(texto: str, permitidos: tuple[str, ...], nombre: str) -> tuple[str, ...]:
    valores = tuple(valor.strip() for valor in texto.split(",") if valor.strip())
    desconocidos = tuple(valor for valor in valores if valor not in permitidos)
    if not valores or desconocidos or len(set(valores)) != len(valores):
        raise argparse.ArgumentTypeError(
            f"Valores inválidos para {nombre}. Disponibles: {', '.join(permitidos)}."
        )
    return valores


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m datosdemocl",
        description=(
            "Generador local de datos sintéticos de prueba con convenciones "
            "chilenas (RUT, región/comuna, fechas y montos)."
        ),
        epilog=EJEMPLOS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"datosdemocl {__version__}",
    )

    subcomandos = parser.add_subparsers(dest="comando", metavar="comando")

    generar = subcomandos.add_parser(
        "generar",
        help="genera un lote sintético y lo guarda en CSV o JSON",
        description=(
            "Genera registros ficticios reproducibles. Nunca sobrescribe un "
            "archivo existente salvo que se indique --sobrescribir."
        ),
        epilog=EJEMPLOS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    generar.add_argument(
        "--cantidad",
        type=int,
        required=True,
        metavar="N",
        help=f"número de registros ({MIN_REGISTROS}-{MAX_REGISTROS})",
    )
    generar.add_argument(
        "--formato",
        choices=("csv", "json"),
        required=True,
        help="formato de salida",
    )
    generar.add_argument(
        "--salida",
        required=True,
        metavar="RUTA",
        help="archivo de destino; la carpeta debe existir",
    )
    generar.add_argument(
        "--semilla",
        type=int,
        default=None,
        metavar="ENTERO",
        help="semilla para reproducir el mismo lote",
    )
    generar.add_argument(
        "--perfil",
        choices=tuple(PRESETS),
        default=None,
        help=(
            "conjunto de columnas predefinido: base (9), "
            "sabana_ventas (10), "
            "transacciones (12), clientes (11), comercio_demo (29) "
            "o completo (44). No se puede combinar "
            "con --campos."
        ),
    )
    generar.add_argument(
        "--campos",
        type=_parse_campos,
        default=None,
        metavar="LISTA",
        help=(
            "columnas separadas por coma, en el orden deseado. "
            f"Disponibles: {', '.join(CAMPOS_DISPONIBLES)}"
        ),
    )
    generar.add_argument(
        "--formato-rut",
        choices=FORMATOS_RUT,
        default="con_puntos",
        help=(
            "formato del RUT: con_puntos (12.345.678-5), "
            "sin_puntos (12345678-5) o sin_separadores (123456785)"
        ),
    )
    generar.add_argument(
        "--region",
        metavar="NOMBRE",
        help="filtra los registros por una región del catálogo",
    )
    generar.add_argument(
        "--comuna",
        metavar="NOMBRE",
        help="filtra por comuna; requiere indicar también --region",
    )
    generar.add_argument(
        "--fecha-desde",
        type=_parse_fecha,
        default=FECHA_MINIMA,
        metavar="AAAA-MM-DD",
        help=f"fecha inicial (por defecto {FECHA_MINIMA.isoformat()})",
    )
    generar.add_argument(
        "--fecha-hasta",
        type=_parse_fecha,
        default=FECHA_MAXIMA,
        metavar="AAAA-MM-DD",
        help=f"fecha final (por defecto {FECHA_MAXIMA.isoformat()})",
    )
    generar.add_argument(
        "--monto-min",
        type=int,
        default=MONTO_MINIMO,
        metavar="CLP",
        help=f"monto mínimo (por defecto {MONTO_MINIMO})",
    )
    generar.add_argument(
        "--monto-max",
        type=int,
        default=MONTO_MAXIMO,
        metavar="CLP",
        help=f"monto máximo (por defecto {MONTO_MAXIMO})",
    )
    generar.add_argument(
        "--monto-paso",
        type=int,
        default=PASO_MONTO,
        metavar="CLP",
        help=f"múltiplo de los montos (por defecto {PASO_MONTO})",
    )
    generar.add_argument(
        "--iva-pct",
        type=int,
        default=19,
        metavar="PORCENTAJE",
        help="tasa simulada para separar el IVA del total (0-100; por defecto 19)",
    )
    generar.add_argument(
        "--estados-pago",
        type=lambda texto: _parse_valores(texto, ESTADOS_PAGO, "estados de pago"),
        default=ESTADOS_PAGO,
        metavar="LISTA",
        help="estados permitidos separados por coma",
    )
    generar.add_argument(
        "--tipos-cliente",
        type=lambda texto: _parse_valores(texto, TIPOS_CLIENTE, "tipos de cliente"),
        default=TIPOS_CLIENTE,
        metavar="LISTA",
        help="tipos de cliente permitidos separados por coma",
    )
    generar.add_argument(
        "--tipos-documento",
        type=lambda texto: _parse_valores(
            texto, TIPOS_DOCUMENTO_PAGO, "tipos de documento"
        ),
        default=TIPOS_DOCUMENTO_PAGO,
        metavar="LISTA",
        help="tipos de documento permitidos separados por coma",
    )
    generar.add_argument(
        "--pasarelas",
        type=lambda texto: _parse_valores(texto, PASARELAS_PAGO, "pasarelas"),
        default=PASARELAS_PAGO,
        metavar="LISTA",
        help="pasarelas permitidas separadas por coma",
    )
    generar.add_argument(
        "--canales-venta",
        type=lambda texto: _parse_valores(texto, CANALES_VENTA, "canales de venta"),
        default=CANALES_VENTA,
        metavar="LISTA",
        help="canales permitidos separados por coma",
    )
    generar.add_argument(
        "--dominio-correo",
        default=DOMINIO_CORREO,
        metavar="DOMINIO",
        help="dominio de correo terminado en .test (por defecto ejemplo.test)",
    )
    generar.add_argument(
        "--delimitador",
        choices=(";", ",", "tab"),
        default=";",
        help="delimitador del CSV: ; , o tab (por defecto ;)",
    )
    generar.add_argument(
        "--sin-bom",
        action="store_false",
        dest="incluir_bom",
        help="escribe el CSV sin BOM UTF-8",
    )
    generar.add_argument(
        "--sobrescribir",
        action="store_true",
        help="permite reemplazar un archivo de salida existente",
    )

    validar = subcomandos.add_parser(
        "validar-rut",
        help="valida un RUT sin crear archivos",
        description=(
            "Normaliza y valida el dígito verificador de un RUT con módulo 11. "
            "No consulta el Registro Civil ni comprueba existencia real."
        ),
    )
    validar.add_argument("rut", metavar="RUT", help="RUT con o sin puntos y guion")

    subcomandos.add_parser(
        "gui",
        help="abre la interfaz gráfica de escritorio",
        description=(
            "Abre la interfaz gráfica local para elegir columnas, formatos, "
            "rangos y archivo de salida sin escribir comandos."
        ),
    )

    return parser


def _generar(args: argparse.Namespace) -> int:
    print(f"Aviso: {ADVERTENCIA}", file=sys.stderr)
    if args.campos is not None and args.perfil is not None:
        raise _ErrorDeUso("Use --perfil o --campos, no ambos.")
    if args.campos is not None:
        campos = args.campos
    elif args.perfil is not None:
        campos = campos_de_preset(args.perfil)
    else:
        campos = CAMPOS_POR_DEFECTO

    opciones = OpcionesGeneracion(
        cantidad=args.cantidad,
        semilla=args.semilla,
        campos=campos,
        formato_rut=args.formato_rut,
        region=args.region,
        comuna=args.comuna,
        fecha_desde=args.fecha_desde,
        fecha_hasta=args.fecha_hasta,
        monto_min=args.monto_min,
        monto_max=args.monto_max,
        monto_paso=args.monto_paso,
        iva_pct=args.iva_pct,
        estados_pago=args.estados_pago,
        tipos_cliente=args.tipos_cliente,
        tipos_documento_pago=args.tipos_documento,
        pasarelas_pago=args.pasarelas,
        canales_venta=args.canales_venta,
        dominio_correo=args.dominio_correo,
    )
    try:
        registros, semilla_usada = generar_lote(opciones)
    except GenerationError as exc:
        raise _ErrorDeUso(str(exc)) from exc

    delimitador = "\t" if args.delimitador == "tab" else args.delimitador
    try:
        if args.formato == "csv":
            destino = exportar_csv(
                args.salida,
                registros,
                sobrescribir=args.sobrescribir,
                campos=opciones.campos,
                delimitador=delimitador,
                incluir_bom=args.incluir_bom,
            )
        else:
            destino = exportar_json(
                args.salida,
                registros,
                sobrescribir=args.sobrescribir,
                campos=opciones.campos,
            )
    except ExportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Archivo generado: {destino.resolve()}")
    print(
        f"Registros: {len(registros)} | Formato: {args.formato.upper()} | "
        f"Campos: {len(opciones.campos)} | Semilla: {semilla_usada}"
    )
    if args.semilla is None:
        print(
            f"Semilla elegida automáticamente. Use --semilla {semilla_usada} "
            "para reproducir este lote."
        )
    return 0


def _validar_rut(args: argparse.Namespace) -> int:
    try:
        canonico = validar_o_error(args.rut)
    except RutError as exc:
        print(f"RUT inválido: {exc}", file=sys.stderr)
        return 2
    print(f"RUT válido: {canonico}")
    return 0


def _gui(_args: argparse.Namespace) -> int:
    try:
        from .gui import ejecutar
    except ImportError as exc:
        print(
            "Error: no se pudo cargar la interfaz gráfica. "
            "Verifique que tkinter esté disponible en su instalación de Python.",
            file=sys.stderr,
        )
        return 1
    return ejecutar()


def main(argv: Sequence[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)

    if args.comando is None:
        parser.print_help()
        return 0

    try:
        if args.comando == "generar":
            return _generar(args)
        if args.comando == "validar-rut":
            return _validar_rut(args)
        if args.comando == "gui":
            return _gui(args)
    except _ErrorDeUso as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    parser.print_help()
    return 2
