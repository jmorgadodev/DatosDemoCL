# DatosDemoCL

Generador local de datos sintéticos de prueba con convenciones chilenas:
RUT con dígito verificador coherente, nombres y apellidos ficticios, pares
región/comuna, fechas ISO y montos en pesos chilenos. Incluye una **interfaz
gráfica de escritorio** y una **CLI**, exporta CSV y JSON, y funciona sin
conexión a Internet, sin cuentas, sin telemetría y sin dependencias externas.

**Versión:** `0.8.0` · **Licencia:** MIT.

> **Advertencia sobre los RUT**
>
> Un RUT matemáticamente válido **no garantiza una identidad ficticia**: puede
> coincidir con el RUT de una persona real. La herramienta sólo calcula y
> valida el dígito verificador con módulo 11; **no consulta el Registro Civil,
> el SII ni ningún servicio externo**, y no comprueba si el RUT existe o a
> quién pertenece.
>
> Estos datos sirven para pruebas de software. No constituyen un proceso de
> anonimización, no reemplazan datos personales en entornos regulados y no
> deben usarse como documentos fiscales o legales.
>
Este aviso se conserva en la documentación y en los mensajes de la CLI.

## Qué problema resuelve

Probar formularios, importadores, planillas y validaciones chilenas suele
requerir datos con RUT, regiones, fechas y montos plausibles. Copiar datos de
clientes o inventar valores a mano es lento y riesgoso. DatosDemoCL genera un
lote reproducible de registros ficticios y lo guarda en un archivo local.

La interfaz gráfica mantiene una muestra visible mientras se ajustan los
campos, perfiles y rangos, y deja elegir formato y destino antes de exportar.

El proyecto no utiliza datos de personas reales: los nombres provienen de
listas locales de ejemplo y los correos usan el dominio reservado `.test`.
Tampoco genera teléfonos, direcciones ni cuentas.

## Requisitos y ejecución

- Ejecutable Windows `DatosDemoCL.exe`, compilado desde este proyecto con
  Python 3.12.4.
- Para ejecutar desde el código fuente: Python 3.11 o superior.
- Sólo biblioteca estándar: no requiere `pip install`, red ni credenciales.
- La GUI usa Tkinter, que normalmente viene incluido con Python. En algunas
  distribuciones de Linux puede requerir el paquete del sistema `python3-tk`.

Ejecuta los comandos desde la carpeta que contiene el paquete `datosdemocl/`.

### Abrir la interfaz gráfica en Windows

Haz doble clic en `DatosDemoCL.exe`. No requiere instalar Python en el equipo
que lo ejecuta.

Para reconstruir el ejecutable desde el código fuente, instala Python 3.11 o
superior y ejecuta:

```powershell
python -m pip install -r requirements-build.txt
./construir_ejecutable.ps1
```

Para abrir la GUI desde el código fuente:

```powershell
python -m datosdemocl gui
```

### Usar la CLI

```powershell
python -m datosdemocl --help
```

No es necesario instalar el paquete para esta versión. La instalación con
`pip` no forma parte de lo verificado.

## Interfaz gráfica

La ventana mantiene la muestra de datos a la vista y organiza la configuración
en cuatro pestañas compactas:

### Datos

- **Datos y rangos:** cantidad (1 a 10.000), semilla, región/comuna, fechas,
  rango y múltiplo de montos e IVA configurable (0 a 100%; 19% inicial).
- **Formato compacto:** el RUT (con puntos, sin puntos o sin separadores) y el
  dominio de correo `.test` están junto a los parámetros generales.

### Campos

- Búsqueda por nombre, selección individual y perfiles
  para base, sábana de ventas, transacciones, clientes y comercio completo.
  Los campos se agrupan por personas/clientes y ventas/productos/pagos.
- **Comercio demo:** productos y SKU ficticios, cantidad y precio neto
  coherentes, subtotal, tasa/importe de IVA, estado de pago y pedido, fecha
  estimada y moneda. Perfil de cliente incluye tipo, empresa, segmento, estado
  y fecha de alta. No genera teléfonos.

### Valores permitidos

- Elige los estados de pago que pueden aparecer: **Aprobado**, **Pendiente**,
  **Rechazado** y **Reembolsado**.
- Elige **Persona**, **Empresa** o ambos tipos de cliente. El campo `empresa`
  se completa cuando el cliente es Empresa; para personas queda vacío porque
  no tienen una empresa asociada.
- Limita los tipos de documento, pasarelas y canales de venta. Cada grupo
  ofrece botones compactos que muestran claramente qué opciones están activas,
  además de acciones **Todas** y **Limpiar**. **Restablecer opciones** activa el
  catálogo completo.
- La muestra en vivo aplica los filtros de inmediato. Los estados de pago,
  transacción y pedido se mantienen relacionados; los documentos exentos usan
  IVA 0%. Si se limpia una categoría, la tabla pasa a un estado vacío y la
  interfaz indica qué falta para generar.

### Salida

- CSV o JSON, delimitador (`;`, `,` o tabulador), BOM
  UTF-8 para Excel y ruta de destino. El botón **Examinar…** abre el selector
  de archivos.

### Muestra y acciones

La muestra permanece junto a la configuración: presenta cinco filas, el
resumen de campos y el formato de salida, con desplazamiento horizontal. Se
actualiza al cambiar una columna, un rango o un valor permitido. Las acciones
**Vista previa**, **Generar archivo**, **Restablecer** y **Abrir carpeta** están
disponibles al pie de la ventana.

### Vista previa

Muestra las primeras cinco filas junto al formulario y actualiza el ejemplo al
cambiar un campo o parámetro. Si dejas la semilla vacía, se elige una
automáticamente y aparece en el resumen de la muestra; el archivo generado
reutiliza esa semilla para coincidir con la vista previa. Escribe un número
para fijar una semilla propia.

Antes de reemplazar un archivo existente, la aplicación pide confirmación
explícita. La carpeta de destino debe existir; no se crean carpetas de forma
implícita.

## Uso con la CLI

### Generar un CSV o un JSON

```powershell
python -m datosdemocl generar --cantidad 25 --formato csv --salida .\ejemplos\mi_lote.csv --semilla 2026
python -m datosdemocl generar --cantidad 25 --formato json --salida .\ejemplos\mi_lote.json --semilla 2026
```

Salida esperada (resumida):

```text
Aviso: un RUT matemáticamente válido no garantiza una identidad ficticia...
Archivo generado: C:\...\DatosDemoCL\ejemplos\mi_lote.csv
Registros: 25 | Formato: CSV | Campos: 9 | Semilla: 2026
```

El aviso se escribe en la salida de error (`stderr`).

### Elegir columnas, formato de RUT y filtros

```powershell
python -m datosdemocl generar `
  --cantidad 100 `
  --formato csv `
  --salida .\ejemplos\lote_personalizado.csv `
  --semilla 42 `
  --campos rut,nombre,region,comuna,estado,monto_clp `
  --formato-rut sin_puntos `
  --region "Biobío" `
  --comuna "Concepción" `
  --dominio-correo qa.ejemplo.test `
  --delimitador ";" `
  --sobrescribir
```

Se pueden restringir los valores categóricos antes de generar:

```powershell
python -m datosdemocl generar --cantidad 50 --formato csv --salida .\ejemplos\aprobados.csv `
  --perfil sabana_ventas --estados-pago Aprobado --tipos-cliente Empresa `
  --tipos-documento "Boleta electrónica,Factura electrónica" `
  --pasarelas "Webpay,Flow" --canales-venta "Web,App"
```

Opciones principales de `generar`:

| Opción | Valores / efecto |
| --- | --- |
| `--cantidad N` | 1 a 10.000 registros. Obligatoria. |
| `--formato csv\|json` | Formato de salida. Obligatorio. |
| `--salida RUTA` | Archivo de destino; la carpeta debe existir. Obligatorio. |
| `--semilla ENTERO` | Reproduce el mismo lote. Si se omite, se elige y se informa. |
| `--campos LISTA` | Columnas separadas por coma, en el orden deseado. |
| `--formato-rut` | `con_puntos` (por defecto), `sin_puntos` o `sin_separadores`. |
| `--region NOMBRE` | Filtra por una de las 16 regiones del catálogo. |
| `--comuna NOMBRE` | Filtra por comuna; requiere `--region`. |
| `--fecha-desde`, `--fecha-hasta` | Fechas ISO `AAAA-MM-DD` (por defecto 2023-01-01 a 2025-12-31). |
| `--monto-min`, `--monto-max` | Rango entero en CLP (por defecto 1.000 a 5.000.000). |
| `--monto-paso` | Múltiplo de los montos (por defecto 100). |
| `--iva-pct` | Tasa simulada entre 0 y 100 (por defecto 19); las boletas exentas usan 0. |
| `--estados-pago` | Lista separada por coma: Aprobado, Pendiente, Rechazado o Reembolsado. |
| `--tipos-cliente` | `Persona`, `Empresa` o ambos; Empresa limita la muestra a clientes con nombre de empresa. |
| `--tipos-documento` | Tipos permitidos: Boleta electrónica, Factura electrónica, Boleta exenta o Nota de venta. |
| `--pasarelas` | Medios permitidos: Webpay, Mercado Pago, Flow, Khipu, Transferencia o Efectivo. |
| `--canales-venta` | Canales permitidos: Web, App, Tienda, Call center o Marketplace. |
| `--dominio-correo` | Dominio terminado en `.test` (por defecto `ejemplo.test`). |
| `--delimitador` | `;` (por defecto), `,` o `tab`. |
| `--sin-bom` | Escribe el CSV sin BOM UTF-8. |
| `--sobrescribir` | Permite reemplazar un archivo existente. |

Perfiles adicionales: `--perfil clientes` (11 campos) y
`--perfil comercio_demo` (29 campos). El perfil `completo` incluye todos los
44 campos disponibles. `--campos` permite elegir cualquier combinación y
definir su orden.

La lista completa de columnas está en la sección
[Contrato de salida](#contrato-de-salida).

El campo `chipax_sale_note_folio` representa el valor que suele extraerse de
`dp.extra_json->>'$.chipaxSaleNoteFolio'`. El generador simula el folio y lo
exporta con un nombre de columna limpio; no se conecta a Chipax ni a una base
de datos.

### Repetir o reemplazar un lote

La misma semilla, cantidad y opciones producen exactamente los mismos
registros, sin importar el formato:

```powershell
python -m datosdemocl generar --cantidad 25 --formato csv --salida .\ejemplos\mi_lote.csv --semilla 2026 --sobrescribir
```

Sin `--sobrescribir`, la herramienta se niega a reemplazar un archivo
existente y termina con código 1. Si omite `--semilla`, se elige una semilla
automáticamente y se informa en pantalla para poder reproducir el lote.

### Validar un RUT sin crear archivos

```powershell
python -m datosdemocl validar-rut 12.345.678-5
python -m datosdemocl validar-rut "57.994.000-K"
```

Salida del primer comando:

```text
RUT válido: 12.345.678-5
```

Un dígito verificador incorrecto o un formato inválido termina con código 2:

```text
RUT inválido: Dígito verificador inválido para el cuerpo 12.345.678: se esperaba 5.
```

La normalización ignora puntos, guiones y espacios; acepta `k` minúscula y
ceros a la izquierda, y devuelve la forma canónica `12.345.678-5`. El cuerpo
debe tener entre 1 y 8 dígitos y ser mayor que cero.

## Contrato de salida

### Perfil Sábana de ventas (10 campos)

El botón **Sábana de ventas** y `--perfil sabana_ventas` producen estas
columnas, en el orden indicado:

| Campo exportado | Regla de simulación |
| --- | --- |
| `fecha_hora_transaccion` | Fecha del registro y hora aleatoria en formato `AAAA-MM-DD HH:MM:SS`. |
| `cliente_interno` | Código `CLI-000001` reutilizado entre compras del mismo cliente ficticio. |
| `idventa` | Identificador de venta único dentro del lote. |
| `monto_total` | Monto CLP de la venta, consistente con `monto_clp` si se incluye. |
| `tipo_documento_pago` | Tipo de documento simulado. |
| `id_chipax` | Identificador de venta simulado, único dentro del lote. |
| `pasarela_pago` | Pasarela o medio de pago ficticio. |
| `identificador_tributario` | RUT ficticio estable por cliente; puede coincidir con uno real. |
| `chipax_sale_note_folio` | Folio simulado; corresponde a `dp.extra_json->>'$.chipaxSaleNoteFolio'` en el origen. |
| `idpayment_sale` | Identificador de pago simulado, único dentro del lote. |

Para obtener sólo esos campos desde la CLI:

```powershell
python -m datosdemocl generar --cantidad 100 --formato csv --salida .\sabana_ventas.csv --semilla 2026 --perfil sabana_ventas
```

### Columnas por defecto (9)

Cada registro generado con la configuración por defecto tiene exactamente
estos campos, en este orden:

| Campo | Tipo | Regla |
| --- | --- | --- |
| `id_prueba` | texto | Secuencia `DEMO-000001`, `DEMO-000002`, … |
| `nombre` | texto | Lista local de nombres de ejemplo |
| `apellido` | texto | Lista local de apellidos de ejemplo |
| `rut` | texto | Formato `12.345.678-5`; DV calculado con módulo 11 |
| `correo` | texto | `<nombre>.<apellido><secuencia>@ejemplo.test` |
| `region` | texto | Una de las 16 regiones del catálogo local |
| `comuna` | texto | Comuna perteneciente a la región indicada |
| `fecha_registro` | texto | Fecha ISO `AAAA-MM-DD`, entre 2023-01-01 y 2025-12-31 |
| `monto_clp` | entero | CLP simulado, entre 1.000 y 5.000.000, múltiplo de 100 |

### Columnas opcionales (6)

Se agregan con `--campos` o marcándolas en la GUI:

| Campo | Tipo | Regla |
| --- | --- | --- |
| `nombre_completo` | texto | `nombre` y `apellido` en una columna |
| `fecha_nacimiento` | texto | Fecha ISO de una persona adulta |
| `edad` | entero | Edad calculada a la fecha de registro, entre 18 y 80 |
| `estado` | texto | `Activo`, `Inactivo` o `Pendiente` |
| `categoria` | texto | `Básica`, `Estándar` o `Premium` |
| `descuento_pct` | entero | Porcentaje de 0 a 50, múltiplo de 5 |

### Campos de cliente y comercio

El perfil `clientes` suma `tipo_cliente`, `empresa`, `segmento_cliente`,
`estado_cliente` y `fecha_alta` a una selección breve de identificación. El
perfil `comercio_demo` suma esos campos y los siguientes a la sábana de venta:

El campo `empresa` queda vacío para clientes Persona por coherencia. En la
pestaña **Valores permitidos** se puede elegir sólo **Empresa** para que ese
campo esté completo en todas las filas. La fecha de entrega también puede
quedar vacía para pagos pendientes, rechazados o reembolsados. `monto_total`
y `monto_clp` representan el mismo total; incluir ambos sólo es útil si el
sistema de destino necesita esas dos columnas.

En perfiles de comercio, `identificador_tributario` se mantiene estable por
cliente y sirve para relacionar sus ventas con `cliente_interno`. El campo
general `rut` es un identificador de fila independiente; para relaciones de
ventas y clientes, usa el par de campos del perfil de comercio.

| Campo | Regla |
| --- | --- |
| `producto`, `sku`, `categoria_producto` | Catálogo local ficticio con códigos `SKU-DEMO`. |
| `cantidad`, `precio_unitario_clp`, `subtotal_neto_clp` | `cantidad × precio unitario = subtotal neto`. |
| `tasa_iva_pct`, `iva_clp`, `monto_total` | `subtotal neto + IVA = total`; el IVA se puede ajustar y el documento exento usa tasa cero. |
| `estado_pago`, `estado_pedido` | Coherentes con aprobación, rechazo, reversa o espera de la transacción. |
| `fecha_entrega_estimada`, `moneda` | Fecha estimada para ventas aprobadas y moneda `CLP`. |

La tasa inicial del 19% es sólo una regla de simulación; el SII publica esa
tasa general para el IVA, pero estos valores no generan ni representan
documentos tributarios válidos. [Referencia del SII](https://www.sii.cl/preguntas_frecuentes/impuestos_mensuales/001_130_0572.htm).

Ejemplo real generado con semilla `2026` (datos inventados):

```csv
id_prueba;nombre;apellido;rut;correo;region;comuna;fecha_registro;monto_clp
DEMO-000001;Fernanda;Ortiz;57.994.000-K;fernanda.ortiz0001@ejemplo.test;Atacama;Copiapó;2025-05-11;3753300
DEMO-000002;Sofía;Silva;86.763.004-K;sofia.silva0002@ejemplo.test;Magallanes;Puerto Natales;2024-05-06;17600
DEMO-000003;Benjamín;Castillo;91.218.551-6;benjamin.castillo0003@ejemplo.test;Ñuble;Chillán;2025-07-09;76200
```

Puede ver lotes completos en:

- [`ejemplos/ejemplo_datos.csv`](ejemplos/ejemplo_datos.csv) y
  [`ejemplos/ejemplo_datos.json`](ejemplos/ejemplo_datos.json): 25 registros
  con las 9 columnas por defecto.
- [`ejemplos/ejemplo_completo.csv`](ejemplos/ejemplo_completo.csv): 12
  registros con las 15 columnas generales.
- [`ejemplos/ejemplo_personalizado.csv`](ejemplos/ejemplo_personalizado.csv):
  12 registros con columnas elegidas, RUT sin puntos y región Biobío.

## Formatos de archivo

- **CSV:** por defecto UTF-8 con BOM, delimitador punto y coma (`;`), saltos
  de línea CRLF y encabezado en la primera fila. Está pensado para abrirse
  directamente en Excel en configuración regional chilena sin perder tildes,
  `ñ` ni la estructura de columnas. El delimitador y el BOM se pueden cambiar.
- **JSON:** UTF-8 sin BOM. Es un arreglo de objetos con los mismos nombres de
  campo que el CSV; `monto_clp` y `edad` se serializan como números enteros.

Los archivos se escriben primero en un temporal dentro de la carpeta de
destino y luego se renombran, para reducir el riesgo de dejar archivos
parciales. No se crean carpetas automáticamente.

## Reproducibilidad y unicidad

- Misma versión del proyecto + misma semilla + misma cantidad y opciones =
  mismos registros. El formato de salida no altera los datos.
- Los RUT no se repiten dentro de un mismo lote.
- Todos los RUT generados pasan el validador incluido.
- Los campos base (`id_prueba` a `monto_clp`) usan un flujo aleatorio principal;
  los campos opcionales usan un flujo independiente. Por eso, **agregar
  columnas opcionales no cambia los datos base** de la versión 0.1.0 con la
  misma semilla.
- La unicidad **entre ejecuciones distintas no está garantizada**. Además, un
  RUT válido puede coincidir con una persona real; no existe un rango oficial
  de RUT reservado para pruebas.
- Para reducir coincidencias accidentales, los cuerpos generados se eligen
  entre `50.000.000` y `99.999.999`. Esto disminuye la probabilidad, pero no
  la elimina.
- Un lote sin `--semilla` no es reproducible salvo que reutilice la semilla
  que la herramienta imprime.

## Límites y códigos de salida

- Cantidad permitida: **1 a 10.000** registros por ejecución.
- Fechas permitidas: **1900-01-01 a 2100-12-31**. El rango por defecto es
  2023-01-01 a 2025-12-31.
- Montos: enteros positivos; el máximo debe ser mayor o igual al mínimo y el
  rango debe contener al menos un múltiplo del paso.
- El dominio de correo debe terminar en `.test`.
- La carpeta de destino debe existir; no se sobrescribe un archivo sin
  `--sobrescribir` en la CLI o sin confirmación en la GUI.
- `0` (éxito), `1` (error de escritura o archivo existente), `2` (argumentos o
  RUT inválido).
- No hay conexiones de red, telemetría, claves ni lectura de archivos de
  terceros.

## Uso como biblioteca

Desde la raíz del proyecto:

```python
from datosdemocl import OpcionesGeneracion, exportar_csv, generar_lote, validar

opciones = OpcionesGeneracion(
    cantidad=5,
    semilla=2026,
    campos=("rut", "nombre", "region", "comuna", "estado", "monto_clp"),
    formato_rut="sin_puntos",
    region="Biobío",
)
registros, semilla = generar_lote(opciones)
exportar_csv(
    "mi_lote.csv",
    registros,
    campos=opciones.campos,
    delimitador=",",
    incluir_bom=False,
)
print(registros[0]["rut"], semilla, validar(registros[0]["rut"]))
```

La API pública principal está en `datosdemocl/__init__.py`; los módulos
`rut`, `generator`, `schema`, `catalog`, `exporters` y `gui` también pueden
importarse por separado.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

La última ejecución local registrada corresponde a la versión `0.8.0`:
**131 pruebas correctas** en Windows con Python 3.12.4. Cubren cálculo y
validación de RUT, generación y coherencia de datos, filtros, rangos, CSV/JSON,
CLI, campos, vista previa, selección y limpieza de opciones, semilla y
exportación desde la GUI. La compilación del ejecutable también se verificó.
El detalle, alcance y límites de la revisión están en
[`docs/RESULTADO_PRUEBAS.md`](docs/RESULTADO_PRUEBAS.md).

## Estructura

```text
DatosDemoCL/
├── datosdemocl/
│   ├── rut.py          # normalización, DV y validación
│   ├── catalog.py      # nombres, apellidos, regiones y comunas
│   ├── schema.py       # contrato, perfiles y etiquetas de campos
│   ├── generator.py    # opciones, lote determinista y unicidad
│   ├── exporters.py    # CSV/JSON, columnas, delimitador y BOM
│   ├── gui.py          # interfaz gráfica Tkinter
│   └── cli.py          # argparse, mensajes y códigos de salida
├── tests/              # pruebas unittest
├── ejemplos/           # lotes ficticios generados por la herramienta
├── docs/               # decisiones técnicas y evidencia de pruebas
├── .github/workflows/  # pruebas y build de Windows en GitHub Actions
├── DatosDemoCL.exe     # aplicación gráfica para Windows
├── construir_ejecutable.ps1
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

## Alcance y limitaciones

- Catálogo geográfico reducido: **16 regiones y 45 comunas**. No es una
  cobertura exhaustiva de Chile ni una validación de existencia.
- Nombres y apellidos son listas de ejemplo; no representan personas.
- No se generan teléfonos, direcciones, cuentas bancarias ni documentos
  fiscales. Los identificadores de cliente y pago son códigos inventados para
  pruebas y no corresponden a plataformas reales.
- Fechas, montos y categorías son simulaciones para QA; no son comprobantes ni
  registros contables.
- La GUI requiere un entorno de escritorio con Tkinter; no hay interfaz web,
  base de datos, API remota ni integración con servicios estatales.
- No se comprueba que un RUT no pertenezca a una persona real; eso requeriría
  consultar servicios externos, que están fuera del alcance.
- La versión de código fuente documentada es `0.8.0`. Los binarios de Windows
  se pueden descargar desde una release cuando el proyecto publique una.

## Licencia

MIT. Consulte [`LICENSE`](LICENSE).

## Contribuir y reportar problemas

Las instrucciones para ejecutar pruebas y proponer cambios están en
[`CONTRIBUTING.md`](CONTRIBUTING.md). Para reportar vulnerabilidades, siga
[`SECURITY.md`](SECURITY.md).
