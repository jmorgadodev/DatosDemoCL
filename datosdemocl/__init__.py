"""DatosDemoCL: generador local de datos sintéticos de prueba para Chile."""

from __future__ import annotations

__version__ = "0.8.0"

from .exporters import exportar_csv, exportar_json
from .generator import (
    OpcionesGeneracion,
    generar_lote,
    generar_registros,
)
from .rut import calcular_dv, normalizar, validar
from .schema import (
    CAMPOS_DISPONIBLES,
    CAMPOS_POR_DEFECTO,
    CAMPOS_TRANSACCION,
    PRESETS,
)

__all__ = [
    "__version__",
    "CAMPOS_DISPONIBLES",
    "CAMPOS_POR_DEFECTO",
    "CAMPOS_TRANSACCION",
    "PRESETS",
    "OpcionesGeneracion",
    "calcular_dv",
    "exportar_csv",
    "exportar_json",
    "generar_lote",
    "generar_registros",
    "normalizar",
    "validar",
]
