"""Exportación local a CSV y JSON con escritura protegida."""

from __future__ import annotations

import csv
import io
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .schema import CAMPOS_POR_DEFECTO

DELIMITADOR_CSV = ";"
CODIFICACION_CSV = "utf-8-sig"  # BOM para que Excel reconozca los acentos.
CODIFICACION_JSON = "utf-8"

# Alias de compatibilidad.
CAMPOS = CAMPOS_POR_DEFECTO


class ExportError(Exception):
    """Error controlado al escribir un archivo de salida."""


class OutputExistsError(ExportError):
    """La ruta de salida ya existe y no se autorizó sobrescribirla."""


class OutputPathError(ExportError):
    """La ruta de salida no es utilizable."""


def _comprobar_registros(
    registros: Iterable[Mapping[str, object]],
    campos: Sequence[str],
) -> list[dict]:
    columnas = tuple(campos)
    if not columnas:
        raise ExportError("Debe indicar al menos una columna para exportar.")

    lista = []
    for posicion, registro in enumerate(registros, start=1):
        faltantes = [campo for campo in columnas if campo not in registro]
        if faltantes:
            raise ExportError(
                f"El registro {posicion} no tiene los campos requeridos: "
                f"{', '.join(faltantes)}."
            )
        lista.append({campo: registro[campo] for campo in columnas})
    return lista


def _validar_delimitador(delimitador: str) -> None:
    if not isinstance(delimitador, str) or len(delimitador) != 1:
        raise ExportError(
            "El delimitador CSV debe ser exactamente un carácter."
        )


def serializar_csv(
    registros: Iterable[Mapping[str, object]],
    campos: Sequence[str] = CAMPOS_POR_DEFECTO,
    delimitador: str = DELIMITADOR_CSV,
) -> str:
    """Serializa los registros con el delimitador indicado y saltos CRLF."""
    _validar_delimitador(delimitador)
    filas = _comprobar_registros(registros, campos)
    buffer = io.StringIO(newline="")
    escritor = csv.DictWriter(
        buffer,
        fieldnames=tuple(campos),
        delimiter=delimitador,
        lineterminator="\r\n",
        extrasaction="raise",
    )
    escritor.writeheader()
    escritor.writerows(filas)
    return buffer.getvalue()


def serializar_json(
    registros: Iterable[Mapping[str, object]],
    campos: Sequence[str] = CAMPOS_POR_DEFECTO,
) -> str:
    """Serializa una lista de objetos con acentos sin escapar."""
    filas = _comprobar_registros(registros, campos)
    return json.dumps(filas, ensure_ascii=False, indent=2) + "\n"


def _escribir(ruta: str | os.PathLike[str], datos: bytes, sobrescribir: bool) -> Path:
    destino = Path(ruta)
    if destino.exists():
        if destino.is_dir():
            raise OutputPathError(f"La ruta de salida es una carpeta: {destino}.")
        if not sobrescribir:
            raise OutputExistsError(
                f"El archivo ya existe: {destino}. "
                "Use --sobrescribir para reemplazarlo de forma explícita."
            )

    carpeta = destino.parent if str(destino.parent) else Path(".")
    if not carpeta.exists():
        raise OutputPathError(f"La carpeta de destino no existe: {carpeta}.")
    if not carpeta.is_dir():
        raise OutputPathError(f"La ruta padre no es una carpeta: {carpeta}.")

    try:
        descriptor, temporal = tempfile.mkstemp(
            prefix=f".{destino.name}.", suffix=".tmp", dir=carpeta
        )
    except OSError as exc:
        raise ExportError(
            f"No se pudo crear un archivo temporal en {carpeta}: {exc}"
        ) from exc

    try:
        with os.fdopen(descriptor, "wb") as archivo:
            archivo.write(datos)
        os.replace(temporal, destino)
    except OSError as exc:
        raise ExportError(f"No se pudo escribir {destino}: {exc}") from exc
    finally:
        if os.path.exists(temporal):
            try:
                os.unlink(temporal)
            except OSError:
                pass
    return destino


def exportar_csv(
    ruta: str | os.PathLike[str],
    registros: Iterable[Mapping[str, object]],
    sobrescribir: bool = False,
    campos: Sequence[str] = CAMPOS_POR_DEFECTO,
    delimitador: str = DELIMITADOR_CSV,
    incluir_bom: bool = True,
) -> Path:
    """Escribe un CSV UTF-8, con BOM y delimitador configurables."""
    if not isinstance(incluir_bom, bool):
        raise ExportError("La opción de BOM debe ser verdadera o falsa.")
    texto = serializar_csv(registros, campos=campos, delimitador=delimitador)
    codificacion = CODIFICACION_CSV if incluir_bom else "utf-8"
    return _escribir(ruta, texto.encode(codificacion), sobrescribir)


def exportar_json(
    ruta: str | os.PathLike[str],
    registros: Iterable[Mapping[str, object]],
    sobrescribir: bool = False,
    campos: Sequence[str] = CAMPOS_POR_DEFECTO,
) -> Path:
    """Escribe un JSON UTF-8 sin BOM."""
    texto = serializar_json(registros, campos=campos)
    return _escribir(ruta, texto.encode(CODIFICACION_JSON), sobrescribir)
