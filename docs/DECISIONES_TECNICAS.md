# Decisiones técnicas

**Proyecto:** DatosDemoCL (nombre de trabajo de Chilean Mock Data Generator)
**Versión:** 0.8.0
**Fecha:** 6 de noviembre de 2026

Este documento registra las decisiones breves que sostienen la implementación.
No describe funcionalidades futuras como si ya existieran.

## 1. Stack y ejecución

- Python 3.11+ con biblioteca estándar para uso normal. PyInstaller se usa
  sólo al construir el ejecutable de Windows.
- El paquete se ejecuta con `python -m datosdemocl` desde la raíz del
  proyecto. No se requiere instalación para esta versión.
- La interfaz gráfica usa Tkinter, incluido en la biblioteca estándar. En
  Windows se ofrece `DatosDemoCL.exe`; también se puede abrir con
  `python -m datosdemocl gui` desde el código fuente.
- No se agregó framework web, base de datos, servicio en la nube ni API.
- No hay llamadas de red, telemetría ni lectura de archivos de terceros.

Justificación: el problema es local, acotado y debe funcionar sin conexión. Un
CLI y una GUI con la biblioteca estándar reducen superficie de error,
dependencias y mantenimiento.

## 2. Módulos

| Módulo | Responsabilidad |
| --- | --- |
| `datosdemocl/rut.py` | Limpieza, formato canónico, cálculo módulo 11, validación y errores tipados. |
| `datosdemocl/catalog.py` | Listas locales de nombres/apellidos y pares región/comuna. |
| `datosdemocl/schema.py` | Contrato de los 44 campos, etiquetas, descripciones y perfiles de salida. |
| `datosdemocl/generator.py` | `OpcionesGeneracion`, lote determinista, validación y control de duplicados. |
| `datosdemocl/exporters.py` | Serialización CSV/JSON, columnas, delimitador, BOM y escritura atómica. |
| `datosdemocl/gui.py` | Ventana Tkinter, formularios, vista previa y acciones de escritura. |
| `datosdemocl/cli.py` | Argumentos, mensajes, advertencia, límites y códigos de salida. |

Ni la CLI ni la GUI contienen lógica de generación o de formato; ambas delegan
en el motor y en los exportadores.

## 3. Contrato de salida

Columnas por defecto, en orden: `id_prueba`, `nombre`, `apellido`, `rut`,
`correo`, `region`, `comuna`, `fecha_registro`, `monto_clp`.

Columnas opcionales: `nombre_completo`, `fecha_nacimiento`, `edad`, `estado`,
`categoria`, `descuento_pct`.

Decisiones:

- `id_prueba` secuencial con prefijo `DEMO-` y seis dígitos. Sirve para
  identificar filas sin usar un identificador real.
- `rut` se guarda como texto. El formato por defecto es con puntos y guion
  (`12.345.678-5`); también se admiten `12345678-5` y `123456785`. Es legible
  en Excel y evita perder el dígito verificador `K`.
- `correo` usa siempre un dominio bajo el TLD `.test`, por defecto
  `@ejemplo.test`. El TLD está reservado para pruebas; no se usan dominios de
  terceros.
- `fecha_registro` es una fecha ISO sin hora. El rango por defecto es
  `2023-01-01` a `2025-12-31` y puede configurarse entre `1900-01-01` y
  `2100-12-31`.
- `fecha_nacimiento` y `edad` son coherentes entre sí: se elige una edad
  adulta entre 18 y 80 años y se deriva la fecha de nacimiento respecto de la
  fecha de registro. Así se evitan edades negativas o incoherentes.
- `monto_clp` es un entero de pesos, sin decimales ni símbolos. Por defecto es
  múltiplo de 100; el rango y el paso son configurables.
- `estado`, `categoria` y `descuento_pct` son valores ficticios de catálogo,
  útiles para probar filtros y formularios.
- El orden de salida es el orden solicitado en `campos`; la GUI respeta el
  orden de la lista de columnas.
- No se agregan teléfonos ni direcciones: aumentarían el riesgo de parecer
  datos personales reales sin aportar al caso de uso.

## 4. RUT de prueba

- Se normalizan puntos, guiones, espacios y ceros a la izquierda.
- El dígito verificador se calcula con módulo 11: resto 11 → `0`, resto 10 →
  `K`, resto 1–9 → dígito.
- `validar` devuelve un booleano; `validar_o_error` devuelve la forma canónica
  o lanza `RutChecksumError`/`RutFormatError`.
- No existe un rango oficial de RUT para pruebas. Los cuerpos generados se
  eligen entre `50.000.000` y `99.999.999` para reducir la probabilidad de
  coincidir con RUT ya emitidos. La probabilidad no se elimina y se advierte
  en README, ayuda y salida de `generar`.
- No se consulta el Registro Civil, el SII, bases de datos ni servicios de
  terceros. El validador comprueba coherencia matemática, no existencia.

## 5. Determinismo y unicidad

- El flujo principal usa `random.Random(semilla)` con un orden de extracción
  fijo. La misma versión, semilla, cantidad y opciones producen los mismos
  registros base.
- Los campos opcionales usan un segundo flujo
  `random.Random(semilla ^ 0x5DEECE66D)`. Agregar o quitar columnas opcionales
  no altera los valores base de la versión 0.1.0. La prueba
  `test_campos_opcionales_no_alteran_los_base` lo verifica.
- Si no se entrega semilla, se obtiene una con `secrets.randbits(32)` y se
  informa. Así el lote se puede reproducir después. La GUI mantiene vacío el
  campo automático, muestra la semilla usada en el resumen y la conserva en
  memoria durante la sesión para que la exportación coincida con la muestra.
- El formato de salida no consume números aleatorios: CSV y JSON contienen los
  mismos datos.
- Los RUT se controlan con un conjunto de cuerpos usados en el lote. La
  unicidad se garantiza sólo dentro del lote, no entre ejecuciones.
- Los correos incorporan el número de secuencia, por lo que también son únicos
  dentro del lote aunque se repitan nombre y apellido.

## 6. Formatos de archivo

### CSV

- Codificación UTF-8 con BOM (`utf-8-sig`) por defecto, para que Excel muestre
  tildes y `ñ` correctamente. El BOM puede omitirse con `--sin-bom` o con la
  casilla de la GUI.
- Delimitador `;` por defecto, coherente con la configuración regional chilena
  de Excel. También se admiten `,` y tabulador.
- Saltos CRLF y encabezado en la primera fila.
- `monto_clp` y `edad` se escriben sin separador de miles para que Excel los
  trate como números.
- `rut` y `correo` quedan como texto; el RUT incluye el formato elegido.

### JSON

- UTF-8 sin BOM.
- Arreglo de objetos, `ensure_ascii=False`, indentación de 2 espacios y salto
  final.
- Mismos nombres de campo que el CSV; `monto_clp` y `edad` son numéricos.

## 7. Interfaz gráfica

- Una sola ventana en paneles: configuración a la izquierda, organizada en
  pestañas de Datos, Campos, Valores permitidos y Salida; muestra de cinco filas
  a la derecha. La muestra se actualiza con debounce cuando cambian los
  parámetros y no escribe archivos.
- Los campos se buscan por etiqueta, clave o descripción, y se aplican
  perfiles de datos generales, sábana, clientes y comercio.
- La selección de estados de pago, tipos de documento, pasarelas y canales
  limita los valores generados. Los estados de transacción y pedido se derivan
  del estado de pago para conservar su coherencia.
- El tipo de cliente puede limitarse a Persona o Empresa. `empresa` sólo tiene
  un valor para clientes Empresa; al seleccionar únicamente ese tipo, ninguna
  fila queda vacía en esa columna.
- Los controles categóricos son botones con estilo activo/inactivo; limpiar
  una categoría vacía la vista previa y muestra qué falta para volver a
  generarla. Al elegir un valor, la muestra se actualiza inmediatamente.
- La generación se ejecuta en el hilo principal; el refresco de muestra se
  demora brevemente para agrupar cambios seguidos y evitar recalcular al
  escribir cada carácter.
- Los valores se leen y validan con `OpcionesGeneracion.validar()` antes de
  generar. Los errores se muestran en un cuadro de diálogo y en la barra de
  estado.
- La vista previa genera el lote completo en memoria y muestra sólo las
  primeras cinco filas. No escribe archivos.
- La generación de archivo comprueba la ruta, pide confirmación si el destino
  existe y reutiliza los exportadores de la CLI.
- La GUI conserva un orden estable por grupo; la CLI permite definir un orden
  arbitrario mediante `--campos`.
- No se guardan preferencias en disco: la configuración vive sólo mientras la
  ventana está abierta.
- La tasa de IVA para los campos de comercio es configurable de 0 a 100%; la
  boleta exenta usa tasa cero. Es un valor de QA, no una regla para emitir
  documentos tributarios.
- Productos y empresas provienen de catálogos locales de demostración. No se
  generan teléfonos ni direcciones que puedan parecer datos de contacto.

## 8. Escritura segura

- La carpeta de destino debe existir; no se crean directorios de forma
  implícita.
- Si el destino existe y no se autorizó la sobrescritura, se aborta y no se
  modifica el archivo. En la CLI se usa `--sobrescribir`; en la GUI se pide
  confirmación.
- La escritura se realiza en un archivo temporal en la misma carpeta y luego
  se reemplaza con `os.replace`. Si falla, se intenta borrar el temporal.
- No se sigue una política de respaldo automático: la sobrescritura es una
  decisión explícita del usuario.

## 9. Límites y errores

- Cantidad mínima 1 y máxima 10.000; el máximo evita salidas accidentales
  enormes y se valida tanto en la CLI y la GUI como en la API.
- Fechas entre `1900-01-01` y `2100-12-31`; la fecha inicial no puede ser
  posterior a la final.
- Montos enteros positivos, con máximo mayor o igual al mínimo y al menos un
  múltiplo del paso dentro del rango.
- Dominio de correo con formato válido y terminado en `.test`.
- Región conocida; comuna existente dentro de la región indicada.
- Códigos de salida de la CLI: 0 éxito, 1 error de escritura/archivo, 2
  argumentos o RUT inválido.
- Los mensajes distinguen formato inválido, checksum inválido, archivo
  existente, carpeta inexistente y fallo de escritura.

## 10. Pruebas

- `unittest` de la biblioteca estándar, sin dependencias.
- Se prueban unidades (RUT, catálogo, esquema, generador, exportadores) y la
  CLI mediante subprocesos, incluyendo códigos de salida y archivos reales en
  carpetas temporales.
- La GUI tiene pruebas funcionales con Tkinter para configuración, cambio de
  formato de RUT, actualización de comunas, filtros categóricos, estado vacío
  de la vista previa, recuperación al re-seleccionar valores, consistencia de
  semilla y exportación CSV/JSON. Se omiten automáticamente si el entorno no
  puede abrir una ventana.
- La suite se ejecutó en Windows con Python 3.12.4: 131 pruebas correctas.
  Incluye CLI y exportadores además de la interfaz. La evidencia y límites
  están en `docs/RESULTADO_PRUEBAS.md`.
- Evidencia de la última ejecución en `docs/RESULTADO_PRUEBAS.md`.

## 11. Pendiente y fuera de alcance

- No se ha creado el repositorio remoto ni publicado una release. Esta tarea
  prepara la documentación y CI local del proyecto, no sube código a GitHub.
- El empaquetado instalable con `pip` y el branding definitivo siguen fuera del
  alcance.
- Interfaz web, servicio en línea, base de datos, teléfonos, direcciones,
  documentos fiscales y otras fases del catálogo: fuera del alcance.
- Cobertura geográfica exhaustiva: no implementada; el catálogo actual es una
  muestra explícitamente limitada.
- Reordenamiento de columnas con arrastrar y soltar en la GUI: no
  implementado; se usa el orden de la lista o `--campos` en la CLI.
