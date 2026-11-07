"""Interfaz gráfica de escritorio (Tkinter) para DatosDemoCL."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import __version__
from .catalog import REGIONES
from .exporters import ExportError, exportar_csv, exportar_json
from .generator import (
    DOMINIO_CORREO,
    CANALES_VENTA,
    ESTADOS_PAGO,
    FECHA_MAXIMA,
    FECHA_MINIMA,
    FORMATO_RUT_CON_PUNTOS,
    FORMATOS_RUT,
    MAX_REGISTROS,
    MIN_REGISTROS,
    MONTO_MAXIMO,
    MONTO_MINIMO,
    PASO_MONTO,
    PASARELAS_PAGO,
    TIPOS_CLIENTE,
    TIPOS_DOCUMENTO_PAGO,
    GenerationError,
    OpcionesGeneracion,
    generar_lote,
)
from .schema import (
    CAMPOS_INFO,
    DESCRIPCIONES,
    ETIQUETAS,
    ETIQUETAS_PRESETS,
    GRUPO_CLIENTES,
    GRUPO_COMERCIO,
    PRESETS,
    campos_de_preset,
)

TODAS_REGIONES = "Todas las regiones"
TODAS_COMUNAS = "Todas las comunas"

REGIONES_POR_NOMBRE = {nombre: comunas for nombre, comunas in REGIONES}

ETIQUETAS_FORMATO_RUT = {
    "con_puntos": "Con puntos y guion (12.345.678-5)",
    "sin_puntos": "Sin puntos, con guion (12345678-5)",
    "sin_separadores": "Sin puntos ni guion (123456785)",
}
FORMATO_RUT_POR_ETIQUETA = {
    etiqueta: clave for clave, etiqueta in ETIQUETAS_FORMATO_RUT.items()
}

DELIMITADORES = {
    "Punto y coma (;)": ";",
    "Coma (,)": ",",
    "Tabulador": "\t",
}


class Aplicacion(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self) -> None:
        super().__init__()
        self.title("DatosDemoCL — Generador de datos de prueba")
        self.geometry("1480x900")
        self.minsize(1180, 760)
        self._configurar_estilos()
        self._crear_variables()
        self._semilla_lote_actual: int | None = None
        self._preview_after_id: str | None = None
        self._construir_interfaz()
        self._actualizar_comunas()
        self._actualizar_formato()
        self._actualizar_resumen_columnas()
        self._conectar_actualizaciones()
        self.after(10, self._centrar_ventana)
        self.after(100, self._programar_vista_previa)

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        self.configure(background="#EDF2F1")
        estilo.configure("TFrame", background="#EDF2F1")
        estilo.configure("TNotebook", background="#EDF2F1", borderwidth=0)
        estilo.configure(
            "TNotebook.Tab",
            background="#DCE7E5",
            foreground="#38535F",
            padding=(15, 8),
            font=("Segoe UI", 9, "bold"),
        )
        estilo.map(
            "TNotebook.Tab",
            background=[("selected", "#FFFFFF"), ("active", "#EAF1F0")],
            foreground=[("selected", "#0B746E")],
        )
        estilo.configure("TLabelframe", background="#FFFFFF", bordercolor="#D5E0DE")
        estilo.configure(
            "TLabelframe.Label",
            background="#FFFFFF",
            foreground="#173444",
            font=("Segoe UI", 9, "bold"),
        )
        estilo.configure("TLabel", background="#EDF2F1", foreground="#173444")
        estilo.configure(
            "Titulo.TLabel", font=("Segoe UI", 20, "bold"),
            foreground="#173444", background="#EDF2F1"
        )
        estilo.configure(
            "Subtitulo.TLabel", font=("Segoe UI", 9),
            foreground="#526B78", background="#EDF2F1"
        )
        estilo.configure(
            "Hint.TLabel", font=("Segoe UI", 8),
            foreground="#637983", background="#FFFFFF"
        )
        estilo.configure(
            "Accion.TButton",
            foreground="#FFFFFF",
            background="#0B746E",
            padding=(14, 8),
        )
        estilo.map(
            "Accion.TButton",
            foreground=[("disabled", "#DCE7E5"), ("!disabled", "#FFFFFF")],
            background=[("active", "#075E59"), ("!disabled", "#0B746E")],
        )
        estilo.configure(
            "Opcion.TButton",
            background="#F2F5F4",
            foreground="#294450",
            padding=(8, 4),
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9),
        )
        estilo.map(
            "Opcion.TButton",
            background=[("active", "#E5ECEA")],
            foreground=[("disabled", "#89999D")],
        )
        estilo.configure(
            "OpcionActiva.TButton",
            background="#D7EEE9",
            foreground="#075E59",
            padding=(8, 4),
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 9, "bold"),
        )
        estilo.map(
            "OpcionActiva.TButton",
            background=[("active", "#C6E5DF")],
            foreground=[("disabled", "#89999D")],
        )
        estilo.configure(
            "Treeview",
            rowheight=27,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#173444",
            bordercolor="#D5E0DE",
        )
        estilo.configure(
            "Treeview.Heading",
            background="#173444",
            foreground="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            padding=(8, 7),
        )
        estilo.map("Treeview", background=[("selected", "#D3EAE6")], foreground=[("selected", "#173444")])

    def _crear_variables(self) -> None:
        self.var_cantidad = tk.StringVar(value="25")
        self.var_semilla = tk.StringVar(value="")
        self.var_region = tk.StringVar(value=TODAS_REGIONES)
        self.var_comuna = tk.StringVar(value=TODAS_COMUNAS)
        self.var_formato_rut = tk.StringVar(
            value=ETIQUETAS_FORMATO_RUT[FORMATO_RUT_CON_PUNTOS]
        )
        self.var_dominio = tk.StringVar(value=DOMINIO_CORREO)
        self.var_fecha_desde = tk.StringVar(value=FECHA_MINIMA.isoformat())
        self.var_fecha_hasta = tk.StringVar(value=FECHA_MAXIMA.isoformat())
        self.var_monto_min = tk.StringVar(value=str(MONTO_MINIMO))
        self.var_monto_max = tk.StringVar(value=str(MONTO_MAXIMO))
        self.var_monto_paso = tk.StringVar(value=str(PASO_MONTO))
        self.var_iva_pct = tk.StringVar(value="19")
        self.var_formato = tk.StringVar(value="CSV")
        self.var_delimitador = tk.StringVar(value="Punto y coma (;)")
        self.var_bom = tk.BooleanVar(value=True)
        self.var_salida = tk.StringVar(value=str(Path.cwd() / "sabana_ventas.csv"))
        self.var_estado = tk.StringVar(value="Listo para generar.")
        self.var_busqueda_campos = tk.StringVar()
        self.var_perfil = tk.StringVar(value=ETIQUETAS_PRESETS["sabana_ventas"])
        self.var_campos = {
            info.clave: tk.BooleanVar(
                value=info.clave in PRESETS["sabana_ventas"]
            )
            for info in CAMPOS_INFO
        }
        self.chk_campos: dict[str, ttk.Checkbutton] = {}
        self.marcos_grupo: dict[str, ttk.LabelFrame] = {}
        self.var_opciones = {
            "estados_pago": {
                valor: tk.BooleanVar(value=True) for valor in ESTADOS_PAGO
            },
            "tipos_cliente": {
                valor: tk.BooleanVar(value=True) for valor in TIPOS_CLIENTE
            },
            "tipos_documento_pago": {
                valor: tk.BooleanVar(value=True) for valor in TIPOS_DOCUMENTO_PAGO
            },
            "pasarelas_pago": {
                valor: tk.BooleanVar(value=True) for valor in PASARELAS_PAGO
            },
            "canales_venta": {
                valor: tk.BooleanVar(value=True) for valor in CANALES_VENTA
            },
        }
        self.btn_opciones: dict[str, dict[str, ttk.Button]] = {}
        self.marcos_opciones: dict[str, ttk.LabelFrame] = {}
        self.var_resumen_opciones = tk.StringVar()
        self.ultima_carpeta: Path | None = None

    def _construir_interfaz(self) -> None:
        cabecera = ttk.Frame(self, padding=(18, 12, 18, 6))
        cabecera.pack(fill="x")
        ttk.Label(cabecera, text="DatosDemoCL", style="Titulo.TLabel").pack(
            side="left"
        )
        ttk.Label(
            cabecera,
            text=f"Generador de datos de prueba · v{__version__}",
            style="Subtitulo.TLabel",
        ).pack(side="left", padx=(12, 0), pady=(8, 0))
        contenido = ttk.Panedwindow(self, orient="horizontal")
        contenido.pack(fill="both", expand=True, padx=14, pady=(6, 4))

        self.tab_config = ttk.Frame(contenido)
        self.tab_preview = ttk.Frame(contenido, padding=(14, 12))
        contenido.add(self.tab_config, weight=3)
        contenido.add(self.tab_preview, weight=2)

        self._construir_configuracion(self.tab_config)
        self._construir_vista_previa(self.tab_preview)
        self._construir_acciones()

    def _construir_configuracion(self, padre: ttk.Frame) -> None:
        padre.columnconfigure(0, weight=1)
        padre.rowconfigure(0, weight=1)
        self.config_tabs = ttk.Notebook(padre)
        self.config_tabs.grid(row=0, column=0, sticky="nsew")
        self.tab_datos = ttk.Frame(self.config_tabs, padding=12)
        self.tab_campos = ttk.Frame(self.config_tabs, padding=12)
        self.tab_valores = ttk.Frame(self.config_tabs, padding=12)
        self.tab_salida = ttk.Frame(self.config_tabs, padding=12)
        self.config_tabs.add(self.tab_datos, text="Datos")
        self.config_tabs.add(self.tab_campos, text="Campos")
        self.config_tabs.add(self.tab_valores, text="Valores permitidos")
        self.config_tabs.add(self.tab_salida, text="Salida")

        padre = self.tab_datos
        padre.columnconfigure(0, weight=1)
        padre.columnconfigure(1, weight=1)
        lote = ttk.LabelFrame(padre, text="Lote y ubicación", padding=10)
        lote.grid(row=0, column=0, sticky="new", padx=(0, 6), pady=(0, 8))
        lote.columnconfigure(1, weight=1)
        rangos = ttk.LabelFrame(padre, text="Fechas y montos", padding=10)
        rangos.grid(row=0, column=1, sticky="new", padx=(6, 0), pady=(0, 8))
        rangos.columnconfigure(1, weight=1)
        formato = ttk.LabelFrame(padre, text="Formato de identificación", padding=10)
        formato.grid(row=1, column=0, sticky="new", padx=(0, 6))
        formato.columnconfigure(1, weight=1)
        coherencia = ttk.LabelFrame(
            padre, text="Coherencia de la muestra", padding=10
        )
        coherencia.grid(row=1, column=1, sticky="new", padx=(6, 0))
        coherencia.columnconfigure(0, weight=1)
        ttk.Label(
            coherencia,
            text=(
                "Empresa se completa para clientes Empresa.\n"
                "Estado de pago determina transacción y pedido.\n"
                "Total = subtotal + IVA; documentos exentos usan IVA 0%."
            ),
            style="Hint.TLabel",
            wraplength=440,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(lote, text="Cantidad").grid(
            row=0, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        ttk.Spinbox(
            lote,
            from_=MIN_REGISTROS,
            to=MAX_REGISTROS,
            textvariable=self.var_cantidad,
            width=12,
        ).grid(row=0, column=1, sticky="ew", pady=3)

        ttk.Label(lote, text="Semilla").grid(
            row=1, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        ttk.Entry(lote, textvariable=self.var_semilla, width=14).grid(
            row=1, column=1, sticky="ew", pady=3
        )
        ttk.Label(
            lote,
            text="Número para repetir; vacío = automático.",
            style="Hint.TLabel",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 3))

        ttk.Label(lote, text="Región").grid(
            row=3, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        self.cmb_region = ttk.Combobox(
            lote,
            textvariable=self.var_region,
            state="readonly",
            width=28,
            values=(TODAS_REGIONES,) + tuple(r for r, _ in REGIONES),
        )
        self.cmb_region.grid(
            row=3, column=1, sticky="ew", pady=3
        )
        self.cmb_region.bind("<<ComboboxSelected>>", self._actualizar_comunas)

        ttk.Label(lote, text="Comuna").grid(
            row=4, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        self.cmb_comuna = ttk.Combobox(
            lote, textvariable=self.var_comuna, state="readonly", width=28
        )
        self.cmb_comuna.grid(
            row=4, column=1, sticky="ew", pady=3
        )

        ttk.Label(rangos, text="Fecha desde").grid(
            row=0, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        ttk.Entry(rangos, textvariable=self.var_fecha_desde, width=14).grid(
            row=0, column=1, sticky="ew", pady=3
        )
        ttk.Label(rangos, text="AAAA-MM-DD", style="Hint.TLabel").grid(
            row=0, column=2, sticky="w", padx=(8, 0), pady=3
        )

        ttk.Label(rangos, text="Fecha hasta").grid(
            row=1, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        ttk.Entry(rangos, textvariable=self.var_fecha_hasta, width=14).grid(
            row=1, column=1, sticky="ew", pady=3
        )
        ttk.Label(rangos, text="AAAA-MM-DD", style="Hint.TLabel").grid(
            row=1, column=2, sticky="w", padx=(8, 0), pady=3
        )

        ttk.Separator(rangos, orient="horizontal").grid(
            row=2, column=0, columnspan=3, sticky="ew", pady=6
        )
        ttk.Label(rangos, text="Monto mínimo").grid(
            row=3, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        ttk.Entry(rangos, textvariable=self.var_monto_min, width=14).grid(
            row=3, column=1, sticky="ew", pady=3
        )
        ttk.Label(rangos, text="CLP entero", style="Hint.TLabel").grid(
            row=3, column=2, sticky="w", padx=(8, 0), pady=3
        )
        ttk.Label(rangos, text="Monto máximo").grid(
            row=4, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        ttk.Entry(rangos, textvariable=self.var_monto_max, width=14).grid(
            row=4, column=1, sticky="ew", pady=3
        )
        ttk.Label(rangos, text="CLP entero", style="Hint.TLabel").grid(
            row=4, column=2, sticky="w", padx=(8, 0), pady=3
        )
        ttk.Label(rangos, text="Múltiplo de monto").grid(
            row=5, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        ttk.Entry(rangos, textvariable=self.var_monto_paso, width=14).grid(
            row=5, column=1, sticky="ew", pady=3
        )
        ttk.Label(rangos, text="por ejemplo 100", style="Hint.TLabel").grid(
            row=5, column=2, sticky="w", padx=(8, 0), pady=3
        )
        ttk.Label(rangos, text="IVA del lote (%)").grid(
            row=6, column=0, sticky="w", pady=3, padx=(0, 10)
        )
        ttk.Spinbox(
            rangos,
            from_=0,
            to=100,
            textvariable=self.var_iva_pct,
            width=8,
        ).grid(row=6, column=1, sticky="ew", pady=3)
        ttk.Label(
            rangos,
            text="19% inicial; configurable",
            style="Hint.TLabel",
        ).grid(row=6, column=2, sticky="w", padx=(8, 0), pady=3)
        ttk.Label(formato, text="Formato RUT").grid(
            row=0, column=0, sticky="w", pady=3, padx=(0, 8)
        )
        self.cmb_rut = ttk.Combobox(
            formato,
            textvariable=self.var_formato_rut,
            state="readonly",
            width=30,
            values=tuple(ETIQUETAS_FORMATO_RUT.values()),
        )
        self.cmb_rut.grid(row=0, column=1, sticky="ew", pady=3)

        ttk.Label(formato, text="Dominio de correo").grid(
            row=1, column=0, sticky="w", pady=3, padx=(0, 8)
        )
        ttk.Entry(
            formato, textvariable=self.var_dominio, width=24
        ).grid(row=1, column=1, sticky="ew", pady=3)
        ttk.Label(
            formato,
            text="Dominio .test",
            style="Hint.TLabel",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 0))

        padre = self.tab_campos
        padre.columnconfigure(0, weight=1)
        columnas = ttk.LabelFrame(
            padre, text="Columnas a incluir", padding=10
        )
        columnas.grid(row=0, column=0, sticky="nsew")
        for columna in range(4):
            columnas.columnconfigure(columna, weight=1)

        presets = ttk.Frame(columnas)
        presets.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 7))
        ttk.Label(presets, text="Perfil rápido").pack(side="left", padx=(0, 8))
        self.cmb_perfil = ttk.Combobox(
            presets,
            textvariable=self.var_perfil,
            state="readonly",
            width=29,
            values=(*ETIQUETAS_PRESETS.values(), "Selección personalizada"),
        )
        self.cmb_perfil.pack(side="left")
        ttk.Button(
            presets, text="Aplicar", command=self._aplicar_perfil_elegido
        ).pack(side="left", padx=(6, 12))
        ttk.Button(
            presets, text="Todas", command=self._seleccionar_todas
        ).pack(side="right")
        ttk.Button(
            presets, text="Limpiar", command=self._seleccionar_ninguna
        ).pack(side="right", padx=(0, 6))

        busqueda = ttk.Frame(columnas)
        busqueda.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 6))
        busqueda.columnconfigure(1, weight=1)
        ttk.Label(busqueda, text="Buscar campos").grid(row=0, column=0, padx=(0, 8))
        ttk.Entry(busqueda, textvariable=self.var_busqueda_campos).grid(
            row=0, column=1, sticky="ew"
        )
        self.var_busqueda_campos.trace_add("write", self._filtrar_campos)

        claves_cliente = set(GRUPO_CLIENTES)
        claves_comercio = set(GRUPO_COMERCIO)
        claves_transaccion = set(PRESETS["transacciones"])
        grupos = (
            (
                "Personas y clientes",
                tuple(
                    info for info in CAMPOS_INFO
                    if info.clave not in claves_cliente | claves_comercio | claves_transaccion
                    or info.clave in claves_cliente
                ),
            ),
            (
                "Ventas, productos y pagos",
                tuple(
                    info for info in CAMPOS_INFO
                    if info.clave in claves_comercio | claves_transaccion
                ),
            ),
        )
        campos_frame = ttk.Frame(columnas)
        campos_frame.grid(row=2, column=0, columnspan=4, sticky="ew")
        campos_frame.columnconfigure(0, weight=1)
        campos_frame.columnconfigure(1, weight=1)
        for columna, (titulo, infos) in enumerate(grupos):
            grupo = ttk.LabelFrame(campos_frame, text=titulo, padding=(8, 4))
            self.marcos_grupo[titulo] = grupo
            grupo.grid(
                row=0,
                column=columna,
                sticky="nsew",
                padx=(0, 6) if columna == 0 else (6, 0),
            )
            for posicion, info in enumerate(infos):
                check = ttk.Checkbutton(
                    grupo,
                    text=info.etiqueta,
                    variable=self.var_campos[info.clave],
                    command=self._actualizar_resumen_columnas,
                    underline=-1,
                )
                check.grid(
                    row=posicion // 2,
                    column=posicion % 2,
                    sticky="w",
                    padx=(0, 10),
                    pady=1,
                )
                self.chk_campos[info.clave] = check
                check.bind(
                    "<Enter>",
                    lambda _evento, campo=info: self._mostrar_detalle_campo(campo),
                )
                check.bind(
                    "<FocusIn>",
                    lambda _evento, campo=info: self._mostrar_detalle_campo(campo),
                )
                check.bind("<Leave>", self._limpiar_detalle_campo)
                check.bind("<FocusOut>", self._limpiar_detalle_campo)

        ttk.Label(
            columnas,
            text=(
                "Puedes combinar campos de ambos grupos. La muestra de la derecha "
                "se actualiza al cambiar la selección. El folio Chipax corresponde "
                "a dp.extra_json->>'$.chipaxSaleNoteFolio'."
            ),
            style="Hint.TLabel",
            wraplength=920,
        ).grid(row=3, column=0, columnspan=4, sticky="w", pady=(6, 0))

        self.lbl_columnas = ttk.Label(
            columnas, text="", style="Hint.TLabel"
        )
        self.lbl_columnas.grid(
            row=4,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(6, 0),
        )
        self.lbl_detalle_campo = ttk.Label(
            columnas,
            text="Pasa sobre un campo o selecciónalo con el teclado para ver para qué sirve.",
            style="Hint.TLabel",
            wraplength=920,
        )
        self.lbl_detalle_campo.grid(
            row=5, column=0, columnspan=4, sticky="w", pady=(3, 0)
        )

        padre = self.tab_salida
        padre.columnconfigure(0, weight=1)
        salida = ttk.LabelFrame(padre, text="Archivo de salida", padding=12)
        salida.grid(row=0, column=0, sticky="new")
        salida.columnconfigure(1, weight=1)
        salida.columnconfigure(3, weight=1)

        ttk.Label(salida, text="Formato").grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        self.cmb_formato = ttk.Combobox(
            salida,
            textvariable=self.var_formato,
            state="readonly",
            width=8,
            values=("CSV", "JSON"),
        )
        self.cmb_formato.grid(row=0, column=1, sticky="w")
        self.cmb_formato.bind(
            "<<ComboboxSelected>>", self._actualizar_formato
        )

        ttk.Label(salida, text="Delimitador").grid(
            row=0, column=2, sticky="e", padx=(18, 8)
        )
        self.cmb_delimitador = ttk.Combobox(
            salida,
            textvariable=self.var_delimitador,
            state="readonly",
            width=20,
            values=tuple(DELIMITADORES),
        )
        self.cmb_delimitador.grid(row=0, column=3, sticky="w")
        self.chk_bom = ttk.Checkbutton(
            salida, text="BOM para Excel", variable=self.var_bom
        )
        self.chk_bom.grid(row=0, column=4, sticky="w", padx=(14, 0))

        ttk.Label(salida, text="Ruta").grid(
            row=1, column=0, sticky="w", pady=(8, 0), padx=(0, 8)
        )
        ttk.Entry(salida, textvariable=self.var_salida).grid(
            row=1, column=1, columnspan=3, sticky="ew", pady=(8, 0)
        )
        ttk.Button(salida, text="Examinar…", command=self._examinar).grid(
            row=1, column=4, sticky="w", padx=(8, 0), pady=(8, 0)
        )
        ttk.Label(
            salida,
            text=(
                "La carpeta debe existir. Si el archivo ya existe se pedirá "
                "confirmación antes de reemplazarlo."
            ),
            style="Hint.TLabel",
        ).grid(row=2, column=0, columnspan=5, sticky="w", pady=(6, 0))

        self._construir_opciones_valor(self.tab_valores)

    def _construir_opciones_valor(self, padre: ttk.Frame) -> None:
        padre.columnconfigure(0, weight=1)
        ttk.Label(
            padre,
            text="Elige qué valores pueden aparecer en el lote.",
            style="Subtitulo.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.lbl_ayuda_opciones = ttk.Label(
            padre,
            text=(
                "El estado de pago determina el estado de transacción y el pedido. "
                "Una boleta exenta siempre queda con IVA 0%. "
                "Si eliges solo Empresa, ese campo se completa en todas las filas."
            ),
            style="Hint.TLabel",
            wraplength=520,
        )
        self.lbl_ayuda_opciones.grid(
            row=1, column=0, sticky="w", pady=(0, 10)
        )

        self.lbl_resumen_opciones = ttk.Label(
            padre,
            textvariable=self.var_resumen_opciones,
            style="Hint.TLabel",
            wraplength=520,
        )
        self.lbl_resumen_opciones.grid(
            row=2, column=0, sticky="w", pady=(0, 8)
        )

        ttk.Button(
            padre,
            text="Restablecer opciones",
            command=self._restablecer_opciones_valor,
        ).grid(row=3, column=0, sticky="e", pady=(0, 8))

        grupos = (
            ("estados_pago", "Estado de pago", ESTADOS_PAGO),
            ("tipos_cliente", "Tipo de cliente", TIPOS_CLIENTE),
            ("tipos_documento_pago", "Tipo de documento", TIPOS_DOCUMENTO_PAGO),
            ("pasarelas_pago", "Medio de pago", PASARELAS_PAGO),
            ("canales_venta", "Canal de venta", CANALES_VENTA),
        )
        contenedor = ttk.Frame(padre)
        contenedor.grid(row=4, column=0, sticky="new")
        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=1)
        for posicion, (clave, titulo, valores) in enumerate(grupos):
            fila, columna = divmod(posicion, 2)
            grupo = ttk.LabelFrame(contenedor, text=titulo, padding=(10, 7))
            self.marcos_opciones[clave] = grupo
            grupo.grid(
                row=fila,
                column=columna,
                sticky="new",
                padx=(0, 6) if columna == 0 else (6, 0),
                pady=(0, 10),
            )
            self.btn_opciones[clave] = {}
            barra_grupo = ttk.Frame(grupo)
            barra_grupo.grid(
                row=0, column=0, columnspan=10, sticky="ew", pady=(0, 5)
            )
            ttk.Button(
                barra_grupo,
                text="Todas",
                command=lambda k=clave: self._seleccionar_opciones_grupo(k, True),
            ).pack(side="left")
            ttk.Button(
                barra_grupo,
                text="Limpiar",
                command=lambda k=clave: self._seleccionar_opciones_grupo(k, False),
            ).pack(side="left", padx=(5, 0))
            for indice, valor in enumerate(valores):
                boton = ttk.Button(
                    grupo,
                    text=valor,
                    style="OpcionActiva.TButton",
                    command=lambda k=clave, v=valor: self._alternar_opcion(k, v),
                )
                boton.grid(
                    row=1 + indice // 2,
                    column=indice % 2,
                    sticky="w",
                    padx=(0, 7),
                    pady=3,
                )
                self.btn_opciones[clave][valor] = boton
        self._contenedor_opciones = contenedor
        contenedor.bind("<Configure>", self._ajustar_disposicion_opciones)
        padre.bind("<Configure>", self._ajustar_textos_opciones)
        self.after_idle(self._ajustar_disposicion_opciones)
        self._sincronizar_opciones_visuales()

    def _ajustar_textos_opciones(self, evento) -> None:
        ancho = max(340, evento.width - 28)
        self.lbl_ayuda_opciones.configure(wraplength=ancho)
        self.lbl_resumen_opciones.configure(wraplength=ancho)

    def _ajustar_disposicion_opciones(self, _evento=None) -> None:
        for clave, grupo in self.marcos_opciones.items():
            ancho_disponible = max(120, grupo.winfo_width() - 28)
            columna = 0
            fila = 1
            ancho_fila = 0
            for boton in self.btn_opciones[clave].values():
                ancho_boton = boton.winfo_reqwidth() + 8
                if ancho_fila and ancho_fila + ancho_boton > ancho_disponible:
                    fila += 1
                    columna = 0
                    ancho_fila = 0
                boton.grid_configure(row=fila, column=columna)
                ancho_fila += ancho_boton
                columna += 1

    def _alternar_opcion(self, clave: str, valor: str) -> None:
        variable = self.var_opciones[clave][valor]
        variable.set(not variable.get())
        self._actualizar_vista_previa_ahora()

    def _sincronizar_opciones_visuales(self, *_args) -> None:
        titulos = {
            "estados_pago": "Estado de pago",
            "tipos_cliente": "Tipo de cliente",
            "tipos_documento_pago": "Tipo de documento",
            "pasarelas_pago": "Medio de pago",
            "canales_venta": "Canal de venta",
        }
        nombres_cortos = {
            "estados_pago": "pagos",
            "tipos_cliente": "clientes",
            "tipos_documento_pago": "documentos",
            "pasarelas_pago": "medios de pago",
            "canales_venta": "canales",
        }
        grupos_vacios = []
        resumen = []
        for clave, valores in self.var_opciones.items():
            elegidos = tuple(
                valor for valor, variable in valores.items() if variable.get()
            )
            grupo = self.marcos_opciones.get(clave)
            if grupo is not None:
                grupo.configure(
                    text=f"{titulos[clave]} · {len(elegidos)}/{len(valores)}"
                )
            resumen.append(
                f"{nombres_cortos[clave]} {len(elegidos)}/{len(valores)}"
            )
            if not elegidos:
                grupos_vacios.append(titulos[clave])
            for valor, boton in self.btn_opciones.get(clave, {}).items():
                seleccionado = valores[valor].get()
                boton.configure(
                    text=f"✓  {valor}" if seleccionado else f"○  {valor}",
                    style=(
                        "OpcionActiva.TButton"
                        if seleccionado
                        else "Opcion.TButton"
                    ),
                )
        if grupos_vacios:
            self.var_resumen_opciones.set(
                "Falta elegir al menos un valor en: " + ", ".join(grupos_vacios) + "."
            )
            self.lbl_resumen_opciones.configure(foreground="#9A5A12")
        else:
            self.var_resumen_opciones.set(
                "Incluidos: " + " · ".join(resumen)
                + ". La muestra se actualiza con cada cambio."
            )
            self.lbl_resumen_opciones.configure(foreground="#637983")

    def _restablecer_opciones_valor(self) -> None:
        for grupo in self.var_opciones.values():
            for variable in grupo.values():
                variable.set(True)
        self._sincronizar_opciones_visuales()
        self._actualizar_vista_previa_ahora()
        self._estado("Se restablecieron todos los valores disponibles.")

    def _seleccionar_opciones_grupo(self, clave: str, seleccion: bool) -> None:
        for variable in self.var_opciones[clave].values():
            variable.set(seleccion)
        self._sincronizar_opciones_visuales()
        self._actualizar_vista_previa_ahora()

    def _construir_vista_previa(self, padre: ttk.Frame) -> None:
        cabecera = ttk.Frame(padre)
        cabecera.pack(fill="x", pady=(0, 8))
        ttk.Label(cabecera, text="Así se verá tu sábana", style="Titulo.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            cabecera,
            text="Muestra en vivo · primeras 5 filas · no guarda archivos",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(2, 0))
        ttk.Button(
            cabecera,
            text="Actualizar",
            command=self._vista_previa,
        ).pack(side="right", anchor="n")

        resumen = ttk.LabelFrame(padre, text="Resumen de la muestra", padding=(10, 6))
        resumen.pack(fill="x", pady=(0, 8))
        self.lbl_preview = ttk.Label(
            resumen,
            text="Preparando datos de ejemplo…",
            style="Subtitulo.TLabel",
            wraplength=520,
        )
        self.lbl_preview.pack(anchor="w")
        resumen.bind("<Configure>", self._ajustar_ancho_resumen_previo)

        marco = ttk.Frame(padre)
        marco.pack(fill="both", expand=True)
        marco.rowconfigure(0, weight=1)
        marco.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(marco, show="headings", height=8)
        self.tree.grid(row=0, column=0, sticky="nsew")

        barra_vertical = ttk.Scrollbar(
            marco, orient="vertical", command=self.tree.yview
        )
        barra_horizontal = ttk.Scrollbar(
            marco, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set,
        )
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")

        campos_exportados = ttk.LabelFrame(
            padre, text="Campos que se exportarán", padding=(10, 7)
        )
        campos_exportados.pack(fill="x", pady=(8, 0))
        self.lbl_campos_preview = ttk.Label(
            campos_exportados,
            text="",
            style="Hint.TLabel",
            wraplength=520,
            justify="left",
        )
        self.lbl_campos_preview.pack(anchor="w")
        campos_exportados.bind(
            "<Configure>", self._ajustar_ancho_campos_previo
        )

        nota = ttk.LabelFrame(padre, text="Formato", padding=(10, 7))
        nota.pack(fill="x", pady=(8, 0))
        self.lbl_formato_preview = ttk.Label(
            nota, text="CSV · UTF-8 con BOM · delimitador ;", style="Hint.TLabel"
        )
        self.lbl_formato_preview.pack(anchor="w")

    def _ajustar_ancho_resumen_previo(self, evento) -> None:
        self.lbl_preview.configure(wraplength=max(220, evento.width - 24))

    def _ajustar_ancho_campos_previo(self, evento) -> None:
        self.lbl_campos_preview.configure(wraplength=max(220, evento.width - 24))

    def _construir_acciones(self) -> None:
        marco = ttk.Frame(self, padding=(16, 8, 16, 8))
        marco.pack(fill="x")

        ttk.Button(
            marco,
            text="Vista previa",
            command=self._vista_previa,
        ).pack(side="left")
        ttk.Button(
            marco,
            text="Generar archivo",
            style="Accion.TButton",
            command=self._generar_archivo,
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            marco,
            text="Restablecer",
            command=self._restablecer,
        ).pack(side="left", padx=(8, 0))

        self.btn_carpeta = ttk.Button(
            marco,
            text="Abrir carpeta",
            command=self._abrir_carpeta,
            state="disabled",
        )
        self.btn_carpeta.pack(side="right")
        ttk.Label(
            marco,
            textvariable=self.var_estado,
            style="Subtitulo.TLabel",
        ).pack(side="right", padx=(0, 12))

    # ------------------------------------------------------------------
    # Actualizaciones de estado de la interfaz
    # ------------------------------------------------------------------
    def _centrar_ventana(self) -> None:
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = max(0, (self.winfo_screenwidth() - ancho) // 2)
        y = max(0, (self.winfo_screenheight() - alto) // 2)
        self.geometry(f"+{x}+{y}")

    def _actualizar_comunas(self, _evento=None) -> None:
        region = self.var_region.get()
        if region == TODAS_REGIONES:
            self.cmb_comuna.configure(
                values=(TODAS_COMUNAS,), state="disabled"
            )
            self.var_comuna.set(TODAS_COMUNAS)
            return

        comunas = REGIONES_POR_NOMBRE[region]
        valores = (TODAS_COMUNAS,) + tuple(comunas)
        self.cmb_comuna.configure(values=valores, state="readonly")
        if self.var_comuna.get() not in valores:
            self.var_comuna.set(TODAS_COMUNAS)

    def _actualizar_formato(self, _evento=None) -> None:
        es_csv = self.var_formato.get() == "CSV"
        self.cmb_delimitador.configure(
            state="readonly" if es_csv else "disabled"
        )
        self.chk_bom.configure(state="normal" if es_csv else "disabled")

        ruta = Path(self.var_salida.get().strip() or "datos_demo.csv")
        if es_csv and ruta.suffix.lower() == ".json":
            self.var_salida.set(str(ruta.with_suffix(".csv")))
        elif not es_csv and ruta.suffix.lower() == ".csv":
            self.var_salida.set(str(ruta.with_suffix(".json")))
        if hasattr(self, "lbl_formato_preview"):
            self.lbl_formato_preview.configure(
                text=(
                    "CSV · UTF-8 "
                    + ("con BOM" if self.var_bom.get() else "sin BOM")
                    + f" · delimitador {DELIMITADORES.get(self.var_delimitador.get(), ';')}"
                    if es_csv
                    else "JSON · UTF-8 · arreglo de objetos"
                )
            )

    def _actualizar_resumen_columnas(self) -> None:
        campos = tuple(
            clave for clave, variable in self.var_campos.items() if variable.get()
        )
        seleccionadas = len(campos)
        self.lbl_columnas.configure(
            text=f"{seleccionadas} de {len(CAMPOS_INFO)} campos incluidos."
        )
        coincidencia = next(
            (
                nombre
                for nombre, preset in PRESETS.items()
                if len(preset) == len(campos) and set(preset) == set(campos)
            ),
            None,
        )
        self.var_perfil.set(
            ETIQUETAS_PRESETS[coincidencia]
            if coincidencia
            else "Selección personalizada"
        )
        self._programar_vista_previa()

    def _mostrar_detalle_campo(self, campo) -> None:
        self.lbl_detalle_campo.configure(
            text=f"{campo.etiqueta}: {campo.descripcion}"
        )

    def _limpiar_detalle_campo(self, _evento=None) -> None:
        self.lbl_detalle_campo.configure(
            text="Pasa sobre un campo o selecciónalo con el teclado para ver para qué sirve."
        )

    def _aplicar_perfil_elegido(self) -> None:
        nombre = next(
            (
                clave
                for clave, etiqueta in ETIQUETAS_PRESETS.items()
                if etiqueta == self.var_perfil.get()
            ),
            None,
        )
        if nombre is None:
            self._estado("Elige un perfil de la lista o selecciona los campos manualmente.")
            return
        self._aplicar_preset(nombre)

    def _filtrar_campos(self, *_args) -> None:
        consulta = self.var_busqueda_campos.get().strip().casefold()
        visibles_por_grupo = {nombre: 0 for nombre in self.marcos_grupo}
        campos_cliente = set(GRUPO_CLIENTES)
        campos_comercio = set(GRUPO_COMERCIO) | set(PRESETS["transacciones"])
        for info in CAMPOS_INFO:
            grupo = (
                "Personas y clientes"
                if info.clave in campos_cliente
                or info.clave not in campos_comercio
                else "Ventas, productos y pagos"
            )
            texto = " ".join(
                (info.etiqueta, info.clave, DESCRIPCIONES.get(info.clave, ""))
            ).casefold()
            check = self.chk_campos.get(info.clave)
            if check is None:
                continue
            if not consulta or consulta in texto:
                check.grid()
                visibles_por_grupo[grupo] += 1
            else:
                check.grid_remove()
        for nombre, marco in self.marcos_grupo.items():
            if visibles_por_grupo.get(nombre, 0):
                marco.grid()
            else:
                marco.grid_remove()

    def _conectar_actualizaciones(self) -> None:
        variables = (
            self.var_cantidad,
            self.var_semilla,
            self.var_region,
            self.var_comuna,
            self.var_formato_rut,
            self.var_dominio,
            self.var_fecha_desde,
            self.var_fecha_hasta,
            self.var_monto_min,
            self.var_monto_max,
            self.var_monto_paso,
            self.var_iva_pct,
            self.var_formato,
            self.var_delimitador,
            self.var_bom,
            *self.var_campos.values(),
            *(
                variable
                for grupo in self.var_opciones.values()
                for variable in grupo.values()
            ),
        )
        for variable in variables:
            variable.trace_add("write", self._programar_vista_previa)
        for grupo in self.var_opciones.values():
            for variable in grupo.values():
                variable.trace_add("write", self._sincronizar_opciones_visuales)
        self.var_semilla.trace_add("write", self._reiniciar_semilla_automatica)

    def _reiniciar_semilla_automatica(self, *_args) -> None:
        if not self.var_semilla.get().strip():
            self._semilla_lote_actual = None

    def _programar_vista_previa(self, *_args) -> None:
        if self._preview_after_id is not None:
            try:
                self.after_cancel(self._preview_after_id)
            except tk.TclError:
                pass
        self._preview_after_id = self.after(220, self._refrescar_vista_previa)

    def _actualizar_vista_previa_ahora(self) -> None:
        if self._preview_after_id is not None:
            try:
                self.after_cancel(self._preview_after_id)
            except tk.TclError:
                pass
            self._preview_after_id = None
        self._refrescar_vista_previa()

    def _refrescar_vista_previa(self) -> None:
        self._preview_after_id = None
        try:
            opciones = self._leer_opciones()
            registros, semilla = generar_lote(opciones)
        except (ValueError, GenerationError) as exc:
            for elemento in self.tree.get_children():
                self.tree.delete(elemento)
            self.tree.configure(columns=())
            vacios = [
                titulo
                for clave, titulo in (
                    ("estados_pago", "Estado de pago"),
                    ("tipos_cliente", "Tipo de cliente"),
                    ("tipos_documento_pago", "Tipo de documento"),
                    ("pasarelas_pago", "Medio de pago"),
                    ("canales_venta", "Canal de venta"),
                )
                if not any(
                    variable.get()
                    for variable in self.var_opciones[clave].values()
                )
            ]
            detalle = (
                "Selecciona al menos una opción en " + ", ".join(vacios)
                if vacios
                else str(exc)
            )
            mensaje = "Vista previa vacía · " + detalle + "."
            self.lbl_preview.configure(text=mensaje, foreground="#9A5A12")
            self._estado(mensaje)
            return

        self._semilla_lote_actual = semilla
        self._mostrar_registros(registros, opciones.campos, semilla)
        self._estado(
            f"Muestra lista · {len(opciones.campos)} campos · semilla {semilla}."
        )

    def _aplicar_preset(self, nombre: str) -> None:
        campos = set(campos_de_preset(nombre))
        for clave, variable in self.var_campos.items():
            variable.set(clave in campos)
        self._actualizar_resumen_columnas()
        self._estado(f"Preset aplicado: {ETIQUETAS_PRESETS[nombre]}.")

    def _seleccionar_todas(self) -> None:
        for variable in self.var_campos.values():
            variable.set(True)
        self._actualizar_resumen_columnas()

    def _seleccionar_ninguna(self) -> None:
        for variable in self.var_campos.values():
            variable.set(False)
        self._actualizar_resumen_columnas()

    def _estado(self, texto: str) -> None:
        self.var_estado.set(texto)

    # ------------------------------------------------------------------
    # Lectura y validación de la configuración
    # ------------------------------------------------------------------
    def _leer_entero(self, variable: tk.StringVar, nombre: str) -> int:
        texto = variable.get().strip()
        try:
            return int(texto)
        except ValueError as exc:
            raise ValueError(f"{nombre} debe ser un número entero.") from exc

    def _leer_fecha(self, variable: tk.StringVar, nombre: str) -> date:
        texto = variable.get().strip()
        try:
            return date.fromisoformat(texto)
        except ValueError as exc:
            raise ValueError(
                f"{nombre} debe tener el formato AAAA-MM-DD."
            ) from exc

    def _leer_opciones(self) -> OpcionesGeneracion:
        texto_semilla = self.var_semilla.get().strip()
        if texto_semilla:
            try:
                semilla = int(texto_semilla)
            except ValueError as exc:
                raise ValueError("La semilla debe ser un número entero.") from exc
        else:
            semilla = self._semilla_lote_actual

        region = self.var_region.get()
        region = None if region == TODAS_REGIONES else region
        comuna = self.var_comuna.get()
        comuna = None if comuna == TODAS_COMUNAS else comuna

        formato_rut = FORMATO_RUT_POR_ETIQUETA.get(
            self.var_formato_rut.get()
        )
        if formato_rut not in FORMATOS_RUT:
            raise ValueError("Seleccione un formato de RUT válido.")

        campos = tuple(
            info.clave
            for info in CAMPOS_INFO
            if self.var_campos[info.clave].get()
        )

        opciones = OpcionesGeneracion(
            cantidad=self._leer_entero(self.var_cantidad, "La cantidad"),
            semilla=semilla,
            campos=campos,
            formato_rut=formato_rut,
            region=region,
            comuna=comuna,
            fecha_desde=self._leer_fecha(
                self.var_fecha_desde, "La fecha desde"
            ),
            fecha_hasta=self._leer_fecha(
                self.var_fecha_hasta, "La fecha hasta"
            ),
            monto_min=self._leer_entero(
                self.var_monto_min, "El monto mínimo"
            ),
            monto_max=self._leer_entero(
                self.var_monto_max, "El monto máximo"
            ),
            monto_paso=self._leer_entero(
                self.var_monto_paso, "El múltiplo de monto"
            ),
            iva_pct=self._leer_entero(self.var_iva_pct, "El IVA del lote"),
            estados_pago=tuple(
                valor
                for valor, variable in self.var_opciones["estados_pago"].items()
                if variable.get()
            ),
            tipos_cliente=tuple(
                valor
                for valor, variable in self.var_opciones["tipos_cliente"].items()
                if variable.get()
            ),
            tipos_documento_pago=tuple(
                valor
                for valor, variable in self.var_opciones[
                    "tipos_documento_pago"
                ].items()
                if variable.get()
            ),
            pasarelas_pago=tuple(
                valor
                for valor, variable in self.var_opciones["pasarelas_pago"].items()
                if variable.get()
            ),
            canales_venta=tuple(
                valor
                for valor, variable in self.var_opciones["canales_venta"].items()
                if variable.get()
            ),
            dominio_correo=self.var_dominio.get().strip(),
        )
        opciones.validar()
        return opciones

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def _vista_previa(self) -> None:
        self._actualizar_vista_previa_ahora()

    def _mostrar_registros(
        self,
        registros: list[dict[str, object]],
        campos: tuple[str, ...],
        semilla: int,
    ) -> None:
        for elemento in self.tree.get_children():
            self.tree.delete(elemento)
        self.tree.configure(columns=campos)
        encabezados_cortos = {
            "fecha_hora_transaccion": "Fecha-hora",
            "cliente_interno": "Cliente ID",
            "idventa": "ID venta",
            "monto_total": "Total CLP",
            "tipo_documento_pago": "Doc. pago",
            "id_chipax": "ID Chipax",
            "pasarela_pago": "Pasarela",
            "identificador_tributario": "RUT cliente",
            "chipax_sale_note_folio": "Folio NV",
            "idpayment_sale": "ID pago",
        }

        for campo in campos:
            encabezado = encabezados_cortos.get(campo, ETIQUETAS[campo])
            self.tree.heading(campo, text=encabezado)
            ancho = max(105, min(150, len(encabezado) * 8 + 24))
            self.tree.column(
                campo, width=ancho, minwidth=95, anchor="w", stretch=False
            )

        for registro in registros[:5]:
            self.tree.insert(
                "",
                "end",
                values=[
                    "" if registro[campo] is None else str(registro[campo])
                    for campo in campos
                ],
            )

        visibles = min(5, len(registros))
        self.lbl_preview.configure(
            text=(
                f"{visibles} filas de muestra · lote de {len(registros)} registros · "
                f"{len(campos)} campos · semilla {semilla}."
            ),
            foreground="#526B78",
        )
        self.lbl_campos_preview.configure(
            text=" · ".join(ETIQUETAS[campo] for campo in campos)
        )

    def _generar_archivo(self) -> None:
        try:
            opciones = self._leer_opciones()
            texto_ruta = self.var_salida.get().strip()
            if not texto_ruta:
                raise ValueError("Indique una ruta de archivo de salida.")
            ruta = Path(texto_ruta).expanduser()
            extension = (
                ".csv" if self.var_formato.get() == "CSV" else ".json"
            )
            if ruta.suffix.lower() != extension:
                ruta = ruta.with_suffix(extension)
                self.var_salida.set(str(ruta))

            if ruta.exists() and ruta.is_dir():
                raise ValueError(f"La ruta de salida es una carpeta: {ruta}.")
            if not ruta.parent.exists():
                raise ValueError(
                    f"La carpeta de destino no existe: {ruta.parent}."
                )

            sobrescribir = False
            if ruta.exists():
                respuesta = messagebox.askyesno(
                    "Reemplazar archivo",
                    f"El archivo ya existe:\n\n{ruta}\n\n"
                    "¿Desea reemplazarlo?",
                    parent=self,
                )
                if not respuesta:
                    self._estado("Generación cancelada.")
                    return
                sobrescribir = True

            registros, semilla = generar_lote(opciones)
            self._semilla_lote_actual = semilla

            if self.var_formato.get() == "CSV":
                delimitador = DELIMITADORES.get(
                    self.var_delimitador.get(), ";"
                )
                destino = exportar_csv(
                    ruta,
                    registros,
                    sobrescribir=sobrescribir,
                    campos=opciones.campos,
                    delimitador=delimitador,
                    incluir_bom=self.var_bom.get(),
                )
            else:
                destino = exportar_json(
                    ruta,
                    registros,
                    sobrescribir=sobrescribir,
                    campos=opciones.campos,
                )
        except (ValueError, GenerationError, ExportError, OSError) as exc:
            self._mostrar_error(exc)
            return

        self.ultima_carpeta = ruta.parent.resolve()
        self.btn_carpeta.configure(state="normal")
        self._mostrar_registros(registros, opciones.campos, semilla)
        self._estado(
            f"Generado: {destino.name} ({len(registros)} registros)."
        )

        abrir = messagebox.askyesno(
            "Archivo generado",
            f"Se generaron {len(registros)} registros "
            f"con {len(opciones.campos)} columnas.\n\n"
            f"{destino.resolve()}\n\nSemilla: {semilla}\n\n"
            "¿Desea abrir la carpeta?",
            parent=self,
        )
        if abrir:
            self._abrir_carpeta()

    def _examinar(self) -> None:
        es_csv = self.var_formato.get() == "CSV"
        extension = ".csv" if es_csv else ".json"
        actual = Path(
            self.var_salida.get().strip() or f"datos_demo{extension}"
        ).expanduser()
        if actual.suffix.lower() != extension:
            actual = actual.with_suffix(extension)
        carpeta_inicial = (
            actual.parent if actual.parent.exists() else Path.cwd()
        )
        tipos = (
            [("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
            if es_csv
            else [("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        elegido = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar lote de datos",
            initialdir=str(carpeta_inicial),
            initialfile=actual.name,
            defaultextension=extension,
            filetypes=tipos,
        )
        if elegido:
            self.var_salida.set(elegido)
            self._estado("Ruta de salida actualizada.")

    def _abrir_carpeta(self) -> None:
        if self.ultima_carpeta is None:
            return
        try:
            if sys.platform == "win32":
                os.startfile(str(self.ultima_carpeta))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(self.ultima_carpeta)])
            else:
                subprocess.Popen(["xdg-open", str(self.ultima_carpeta)])
        except OSError as exc:
            self._mostrar_error(
                f"No se pudo abrir la carpeta: {exc}"
            )

    def _restablecer(self) -> None:
        self.var_cantidad.set("25")
        self._semilla_lote_actual = None
        self.var_semilla.set("")
        self.var_region.set(TODAS_REGIONES)
        self.var_comuna.set(TODAS_COMUNAS)
        self.var_formato_rut.set(
            ETIQUETAS_FORMATO_RUT[FORMATO_RUT_CON_PUNTOS]
        )
        self.var_dominio.set(DOMINIO_CORREO)
        self.var_fecha_desde.set(FECHA_MINIMA.isoformat())
        self.var_fecha_hasta.set(FECHA_MAXIMA.isoformat())
        self.var_monto_min.set(str(MONTO_MINIMO))
        self.var_monto_max.set(str(MONTO_MAXIMO))
        self.var_monto_paso.set(str(PASO_MONTO))
        self.var_iva_pct.set("19")
        for grupo in self.var_opciones.values():
            for variable in grupo.values():
                variable.set(True)
        self.var_formato.set("CSV")
        self.var_delimitador.set("Punto y coma (;)")
        self.var_bom.set(True)
        self.var_salida.set(str(Path.cwd() / "sabana_ventas.csv"))
        self._aplicar_preset("sabana_ventas")

        self.ultima_carpeta = None
        self.btn_carpeta.configure(state="disabled")
        self._actualizar_comunas()
        self._actualizar_formato()
        self._actualizar_resumen_columnas()
        self.config_tabs.select(self.tab_datos)
        for elemento in self.tree.get_children():
            self.tree.delete(elemento)
        self.tree.configure(columns=())
        self.lbl_preview.configure(text="Aún no hay una vista previa.")
        self._estado("Configuración restablecida.")

    def _mostrar_error(self, exc: Exception) -> None:
        mensaje = str(exc) or exc.__class__.__name__
        self._estado(f"Error: {mensaje}")
        messagebox.showerror("DatosDemoCL", mensaje, parent=self)


def ejecutar() -> int:
    """Abre la ventana principal y devuelve un código de salida."""
    try:
        aplicacion = Aplicacion()
    except tk.TclError as exc:
        print(
            f"Error: no se pudo abrir la interfaz gráfica: {exc}",
            file=sys.stderr,
        )
        return 1
    aplicacion.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar())
