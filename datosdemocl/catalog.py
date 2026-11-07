"""Catálogos locales de valores ficticios y pares región/comuna.

Los nombres y apellidos son listas de ejemplo, no personas. Las regiones y
comunas corresponden a geografía pública, pero el conjunto es reducido: no es
una cobertura exhaustiva de Chile y no se usa para validar existencia real.
"""

from __future__ import annotations

NOMBRES = (
    "Ana",
    "Antonia",
    "Benjamín",
    "Camila",
    "Cristóbal",
    "Daniel",
    "Daniela",
    "Diego",
    "Emilia",
    "Felipe",
    "Fernanda",
    "Florencia",
    "Gabriel",
    "Ignacio",
    "Isidora",
    "Javiera",
    "Joaquín",
    "Josefa",
    "Juan",
    "Maite",
    "Martina",
    "Matías",
    "Nicolás",
    "Paula",
    "Renata",
    "Sebastián",
    "Sofía",
    "Tomás",
    "Valentina",
    "Vicente",
)

APELLIDOS = (
    "Araya",
    "Bravo",
    "Cáceres",
    "Castillo",
    "Contreras",
    "Cortés",
    "Díaz",
    "Espinoza",
    "Fuentes",
    "González",
    "Hernández",
    "Jara",
    "Lagos",
    "Molina",
    "Muñoz",
    "Núñez",
    "Ortiz",
    "Paredes",
    "Pérez",
    "Rojas",
    "Sáez",
    "Salazar",
    "Sepúlveda",
    "Silva",
    "Soto",
    "Tapia",
    "Torres",
    "Valdés",
    "Vargas",
    "Vega",
)

# Catálogos inventados para demos de clientes y comercio; pueden coincidir
# accidentalmente con nombres comerciales existentes.
EMPRESAS_DEMO = (
    "Comercial Bruma Sur SpA",
    "Servicios Cordillera Demo Ltda.",
    "Distribuidora Río Claro Demo SpA",
    "Taller Nube Austral Ltda.",
    "Soluciones Puerto Norte Demo SpA",
    "Mercado Valle Verde Ltda.",
)

PRODUCTOS_DEMO = (
    ("SKU-DEMO-001", "Kit de bienvenida", "Accesorios"),
    ("SKU-DEMO-002", "Cuaderno de trabajo", "Papelería"),
    ("SKU-DEMO-003", "Servicio de instalación", "Servicios"),
    ("SKU-DEMO-004", "Pack de cables", "Tecnología"),
    ("SKU-DEMO-005", "Suscripción mensual", "Servicios"),
    ("SKU-DEMO-006", "Set de organización", "Hogar"),
    ("SKU-DEMO-007", "Lámpara de escritorio", "Hogar"),
    ("SKU-DEMO-008", "Adaptador multipuerto", "Tecnología"),
    ("SKU-DEMO-009", "Agenda anual", "Papelería"),
    ("SKU-DEMO-010", "Bolso reutilizable", "Accesorios"),
    ("SKU-DEMO-011", "Asesoría inicial", "Servicios"),
    ("SKU-DEMO-012", "Soporte extendido", "Servicios"),
)

# Subconjunto de 16 regiones y 45 comunas. Los nombres de región son
# abreviaturas de uso común, no denominaciones oficiales completas.
REGIONES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Arica y Parinacota", ("Arica", "Putre")),
    ("Tarapacá", ("Iquique", "Alto Hospicio")),
    ("Antofagasta", ("Antofagasta", "Calama", "Tocopilla")),
    ("Atacama", ("Copiapó", "Vallenar", "Caldera")),
    ("Coquimbo", ("La Serena", "Coquimbo", "Ovalle")),
    ("Valparaíso", ("Valparaíso", "Viña del Mar", "Quilpué", "San Antonio")),
    (
        "Metropolitana de Santiago",
        ("Santiago", "Puente Alto", "Maipú", "La Florida", "Las Condes"),
    ),
    ("O'Higgins", ("Rancagua", "San Fernando", "Santa Cruz")),
    ("Maule", ("Talca", "Curicó", "Linares")),
    ("Ñuble", ("Chillán", "San Carlos")),
    ("Biobío", ("Concepción", "Talcahuano", "Los Ángeles")),
    ("La Araucanía", ("Temuco", "Villarrica", "Angol")),
    ("Los Ríos", ("Valdivia", "La Unión")),
    ("Los Lagos", ("Puerto Montt", "Osorno", "Castro")),
    ("Aysén", ("Coyhaique", "Puerto Aysén")),
    ("Magallanes", ("Punta Arenas", "Puerto Natales")),
)
