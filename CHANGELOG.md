# Changelog

Formato basado en Keep a Changelog. El proyecto no está publicado todavía.

## [Unreleased]

### Documentación y desarrollo

- Se actualiza la evidencia de pruebas para DatosDemoCL 0.8.0 y 131 pruebas.
- Se agregan guías para contribuir y reportar vulnerabilidades.
- Se agrega CI de GitHub Actions para probar Python 3.11/3.12 y construir el
  ejecutable de Windows.

## [0.8.0] - 2026-11-05

### Cambiado

- Al limpiar una categoría, la vista previa muestra un estado vacío sin filas
  anteriores; al elegir un valor se actualiza inmediatamente.
- La semilla deja de iniciar con `2026`. Vacía usa una semilla automática que
  aparece en el resumen y se reutiliza al exportar para igualar la muestra.
- El campo `id_prueba` aparece como **ID de registro** y no usa subrayado.
- La pestaña Datos distribuye ubicación, rangos y formato en tarjetas compactas;
  las opciones y el resumen se reacomodan según el ancho disponible.
- Se aumenta la versión a `0.8.0`.

## [0.7.0] - 2026-11-05

### Agregado

- Selección de tipos de cliente Persona y Empresa en GUI y CLI. Al elegir sólo
  Empresa, todas las filas llevan un nombre de empresa demo.
- Controles de valores categóricos como botones compactos con estado visual
  claro y conteo de selección por grupo.

### Cambiado

- La vista previa conserva su última muestra válida cuando una selección queda
  vacía y explica qué categoría debe completarse.
- Se aumenta la versión a `0.7.0`.

## [0.6.0] - 2026-11-05

### Agregado

- Selección de valores permitidos para estados de pago, tipos de documento,
  pasarelas y canales, tanto en GUI como en CLI.
- Muestra en vivo que refleja las selecciones categóricas antes de exportar.

### Cambiado

- La configuración de la GUI se organiza en las pestañas Datos, Campos,
  Valores permitidos y Salida; RUT y dominio de correo quedan compactos junto
  a los parámetros generales.
- La ventana ya no incluye el texto explicativo de QA ni el aviso de privacidad;
  la advertencia de RUT sigue en README y en la CLI.
- Se aumenta la versión a `0.6.0`.

## [0.5.0] - 2026-11-05

### Agregado

- Perfiles de clientes y comercio demo, con empresa ficticia, catálogo de
  productos, SKU, cantidades, precios netos, IVA configurable, estados y
  fechas de pedido.
- Muestra de cinco registros siempre visible, que se actualiza al cambiar la
  selección o los parámetros.
- Búsqueda de campos, perfiles rápidos y diseño en paneles para aprovechar
  mejor el espacio de la ventana.
- Opción `--iva-pct` en la CLI y campo de IVA en la GUI.

### Cambiado

- La GUI inicia con el perfil Sábana de ventas y permite combinar campos de
  clientes, ventas y pagos antes de exportar.
- Los campos nuevos se calculan en un flujo reproducible independiente; los
  subtotales, IVA y total quedan relacionados entre sí.
- Se aumenta la versión a `0.5.0`.

## [0.4.0] - 2026-11-05

### Agregado

- Perfil **Sábana de ventas** con los 10 campos de transacción solicitados y
  orden directo para exportación CSV o JSON.
- Interfaz agrupada por datos generales y transacciones, con referencia al
  origen del folio Chipax.
- Empaquetado gráfico de Windows como `DatosDemoCL.exe` y script PowerShell
  reproducible para reconstruirlo.

### Cambiado

- La documentación explica la simulación y el mapeo de
  `dp.extra_json->>'$.chipaxSaleNoteFolio'` a `chipax_sale_note_folio`.
- Se elimina el lanzador por lotes de Windows.

## [0.2.0] - 2026-11-04

### Agregado

- Interfaz gráfica de escritorio con Tkinter (`python -m datosdemocl gui`),
  con pestañas de configuración y vista previa, selección de columnas,
  validación de entradas, confirmación de sobrescritura y apertura de la
  carpeta de salida.
- Lanzador `DatosDemoCL.bat` para abrir la GUI en Windows.
- Seis columnas opcionales: `nombre_completo`, `fecha_nacimiento`, `edad`,
  `estado`, `categoria` y `descuento_pct` (15 columnas en total).
- Selección y orden de columnas mediante `--campos` y la GUI.
- Formatos de RUT `con_puntos`, `sin_puntos` y `sin_separadores`.
- Filtros por región y comuna, con validación de pertenencia al catálogo.
- Rango configurable de fechas y de montos, incluido el múltiplo del monto.
- Dominio de correo configurable, siempre bajo el TLD reservado `.test`.
- Delimitador CSV configurable (`;`, `,` o tabulador) y opción para omitir el
  BOM UTF-8.
- API pública ampliada: `OpcionesGeneracion`, `generar_lote`,
  `exportar_csv`, `exportar_json`, `CAMPOS_DISPONIBLES` y
  `CAMPOS_POR_DEFECTO`.
- Ejemplos nuevos con las 15 columnas y con columnas personalizadas.
- Pruebas de esquema, opciones avanzadas, CLI y humo de la GUI: **113 pruebas**
  en total.

### Cambiado

- El motor de generación ahora recibe una configuración completa mediante
  `OpcionesGeneracion`; `generar_registros` se mantiene como envoltorio
  compatible.
- La edad y la fecha de nacimiento se calculan de forma coherente para
  personas adultas (18 a 80 años).
- El resumen de la CLI incluye la cantidad de columnas generadas.

### Compatibilidad

- La generación por defecto conserva las 9 columnas y los mismos valores de
  `0.1.0` para la misma semilla. Los ejemplos versionados mantienen sus hashes
  SHA-256.
- Los comandos existentes (`generar`, `validar-rut`, `--cantidad`,
  `--formato`, `--salida`, `--semilla`, `--sobrescribir`) siguen funcionando.

### Limitaciones conocidas

- La unicidad de RUT sólo se garantiza dentro de un lote; puede haber
  coincidencias con RUT reales.
- Catálogo geográfico reducido, no exhaustivo.
- Sin instalación mediante `pip`, publicación, release ni interfaz web.
- La GUI requiere Tkinter y un entorno de escritorio.

## [0.1.0] - 2026-11-04

### Agregado

- Paquete Python ejecutable con `python -m datosdemocl`, sin dependencias
  externas ni conexión a red.
- Normalización, cálculo de dígito verificador y validación de RUT chileno con
  módulo 11, incluyendo `K`/`k`, puntos, guion y errores tipados.
- Generación determinista de lotes sintéticos con semilla, unicidad de RUT
  dentro del lote y catálogo local de nombres, apellidos, 16 regiones y 45
  comunas.
- Registros con `id_prueba`, nombre, apellido, RUT, correo `.test`, región,
  comuna, fecha ISO y monto entero en CLP.
- Exportación CSV (UTF-8 con BOM, delimitador `;`, CRLF) y JSON (UTF-8).
- Protección contra sobrescritura accidental y escritura mediante temporal.
- Límite de 1 a 10.000 registros por ejecución.
- CLI `generar` y `validar-rut`, con ayuda, ejemplos y códigos de salida
  documentados.
- 64 pruebas automatizadas con `unittest`.
- README en español, decisiones técnicas, ejemplos ficticios y licencia MIT.

### Limitaciones conocidas

- La unicidad de RUT sólo se garantiza dentro de un lote; puede haber
  coincidencias con RUT reales.
- Catálogo geográfico reducido, no exhaustivo.
- Sin instalación mediante `pip`, publicación, release ni interfaz web.
