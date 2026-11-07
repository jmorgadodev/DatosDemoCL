"""Normalización, cálculo y validación del RUT chileno (módulo 11).

Este módulo no consulta servicios externos ni verifica la existencia real de
un RUT. Sólo comprueba que el formato sea razonable y que el dígito
verificador coincida con el cálculo módulo 11.
"""

from __future__ import annotations

CUERPO_MAXIMO = 99_999_999


class RutError(ValueError):
    """Error base para problemas de RUT."""


class RutFormatError(RutError):
    """El texto recibido no tiene una estructura de RUT admisible."""


class RutChecksumError(RutError):
    """El dígito verificador no corresponde al cuerpo indicado."""


def _limpiar(rut: str) -> str:
    if not isinstance(rut, str):
        raise RutFormatError("El RUT debe entregarse como texto.")
    limpio = "".join(rut.split()).replace(".", "").replace("-", "").upper()
    if not limpio:
        raise RutFormatError("El RUT está vacío.")
    return limpio


def _partes(rut: str) -> tuple[int, str]:
    limpio = _limpiar(rut)
    if len(limpio) < 2:
        raise RutFormatError(
            "El RUT debe incluir el cuerpo y el dígito verificador."
        )

    cuerpo_texto, dv = limpio[:-1], limpio[-1]
    if not cuerpo_texto.isdigit():
        raise RutFormatError("El cuerpo del RUT debe contener sólo dígitos.")
    if not (dv.isdigit() or dv == "K"):
        raise RutFormatError("El dígito verificador debe ser un número o la letra K.")

    cuerpo = int(cuerpo_texto)
    if cuerpo <= 0:
        raise RutFormatError("El cuerpo del RUT debe ser mayor que cero.")
    if len(str(cuerpo)) > 8:
        raise RutFormatError("El cuerpo del RUT no puede tener más de 8 dígitos.")
    return cuerpo, dv


def formatear_cuerpo(cuerpo: int) -> str:
    """Devuelve un cuerpo numérico con puntos de miles (ej.: 12345678 -> 12.345.678)."""
    if isinstance(cuerpo, bool) or not isinstance(cuerpo, int):
        raise RutFormatError("El cuerpo del RUT debe ser un número entero.")
    if not 1 <= cuerpo <= CUERPO_MAXIMO:
        maximo = f"{CUERPO_MAXIMO:,}".replace(",", ".")
        raise RutFormatError(
            f"El cuerpo del RUT debe estar entre 1 y {maximo}."
        )
    return f"{cuerpo:,}".replace(",", ".")


def calcular_dv(cuerpo: int | str) -> str:
    """Calcula el dígito verificador de un cuerpo de RUT con módulo 11."""
    if isinstance(cuerpo, str):
        if not cuerpo.isdigit():
            raise RutFormatError("El cuerpo del RUT debe contener sólo dígitos.")
        numero = int(cuerpo)
    elif isinstance(cuerpo, bool) or not isinstance(cuerpo, int):
        raise RutFormatError("El cuerpo del RUT debe ser un número entero.")
    else:
        numero = cuerpo

    if not 1 <= numero <= CUERPO_MAXIMO:
        raise RutFormatError(
            f"El cuerpo del RUT debe estar entre 1 y {CUERPO_MAXIMO}."
        )

    suma = 0
    multiplicador = 2
    while numero:
        suma += (numero % 10) * multiplicador
        numero //= 10
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = suma % 11
    resultado = 11 - resto
    if resultado == 11:
        return "0"
    if resultado == 10:
        return "K"
    return str(resultado)


def normalizar(rut: str) -> str:
    """Devuelve el RUT en formato canónico, sin validar el dígito verificador.

    Acepta puntos y guion opcionales, espacios, y la ``k`` en minúscula.
    El resultado tiene la forma ``12.345.678-5``.
    """
    cuerpo, dv = _partes(rut)
    return f"{formatear_cuerpo(cuerpo)}-{dv}"


def validar_o_error(rut: str) -> str:
    """Valida un RUT y devuelve su forma canónica o lanza una excepción."""
    cuerpo, dv = _partes(rut)
    esperado = calcular_dv(cuerpo)
    if dv != esperado:
        raise RutChecksumError(
            f"Dígito verificador inválido para el cuerpo "
            f"{formatear_cuerpo(cuerpo)}: se esperaba {esperado}."
        )
    return f"{formatear_cuerpo(cuerpo)}-{esperado}"


def validar(rut: str) -> bool:
    """Indica si un RUT tiene formato y dígito verificador correctos."""
    try:
        validar_o_error(rut)
    except RutError:
        return False
    return True
