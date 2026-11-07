# Revisión funcional — DatosDemoCL 0.8.0

**Fecha:** 6 de noviembre de 2026
**Entorno:** Windows 11, Python 3.12.4
**Alcance:** pruebas automatizadas del código, flujos de GUI con Tkinter,
generación por CLI y construcción local del ejecutable.

## Resultado

Comando ejecutado desde la raíz del proyecto:

```powershell
python -m unittest discover -s tests -q
```

```text
Ran 131 tests
OK
```

La suite usa `unittest` y no requiere dependencias de terceros. Las pruebas
comprueban unidades del generador, validación de RUT y campos, además de
archivos CSV/JSON reales en carpetas temporales y llamadas a la CLI como
subprocesos. Las pruebas de GUI crean una ventana Tkinter, la ocultan y
verifican su estado y acciones sin requerir una inspección visual.

## Flujos funcionales revisados

- **Valores permitidos:** elegir un subconjunto de estados de pago, documentos,
  tipos de cliente, medios y canales restringe las filas generadas.
- **Limpiar y recuperar:** limpiar una categoría borra las filas de la muestra;
  volver a elegir un valor repuebla la vista sin cambiar de pestaña.
- **Validación:** una selección vacía explica qué grupo falta y bloquea la
  exportación; no queda un archivo incompleto.
- **Estado de pago:** se comprobó que la vista y el archivo respetan un filtro
  único, por ejemplo `Rechazado`.
- **Tipo Empresa:** una ejecución CLI de ocho filas, filtrada a `Empresa`, dejó
  el tipo y la razón social completos en todas las filas.
- **Vista previa y semilla:** con semilla automática, las filas exportadas
  coinciden con la muestra; una semilla explícita permite repetir el lote.
- **Columnas:** selección de perfiles, campos individuales y rechazos de listas
  vacías, duplicadas o desconocidas.
- **CSV:** encabezado y orden de campos, delimitadores, BOM, codificación,
  acentos, extensión, sobrescritura y limpieza de temporales.
- **JSON:** tipo de salida, Unicode, números, columnas y generación desde GUI y
  CLI.
- **Entradas:** límites de cantidad, fechas, montos, dominios `.test`, región y
  comuna, formatos de RUT y valores categóricos inválidos.
- **RUT:** módulo 11, dígito `K`, normalización, entradas incorrectas y
  unicidad dentro de un lote.

La prueba CLI de humo comprobó ocho filas CSV con 29 campos del perfil
`comercio_demo`, todas con pago `Rechazado`, tipo `Empresa` y razón social
completa. El archivo temporal generado para esta comprobación fue eliminado.

## Construcción

El script `construir_ejecutable.ps1` terminó correctamente con PyInstaller
6.13.0 y generó `DatosDemoCL.exe` para Windows. La suite verifica la lógica de
la GUI mediante Tkinter; no se realizó una revisión visual de la ventana en
esta ejecución.

## Límites de esta revisión

- No se probó la representación de los archivos abriéndolos en Excel.
- No se verificó la interfaz visual en distintas resoluciones o escalas.
- No se ejecutó el `.exe` interactuando con la ventana; se comprobó la
  construcción y se probaron los flujos de GUI mediante Tkinter en Python.
- No se hizo captura de tráfico de red. La revisión de código no encontró
  imports ni llamadas de red o telemetría en el paquete de la aplicación.
- No se puede certificar que un RUT matemáticamente válido no corresponda a
  una persona real; esa advertencia se mantiene en README y CLI.
- No se publicó el proyecto ni se probó un flujo remoto de GitHub Actions.
