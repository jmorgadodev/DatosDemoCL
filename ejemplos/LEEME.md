# Ejemplos ficticios

Estos archivos fueron generados por la propia herramienta.

## Lote por defecto

```powershell
python -m datosdemocl generar --cantidad 25 --formato csv --salida .\ejemplos\ejemplo_datos.csv --semilla 2026
python -m datosdemocl generar --cantidad 25 --formato json --salida .\ejemplos\ejemplo_datos.json --semilla 2026
```

Contienen 25 registros con las 9 columnas por defecto y siguen siendo idénticos
a los publicados en la versión 0.1.0.

## Lote con las 15 columnas

```powershell
python -m datosdemocl generar --cantidad 12 --formato csv --salida .\ejemplos\ejemplo_completo.csv --semilla 2026 --campos "id_prueba,nombre,apellido,nombre_completo,rut,correo,region,comuna,fecha_registro,fecha_nacimiento,edad,monto_clp,estado,categoria,descuento_pct" --dominio-correo ejemplo.test
```

## Lote personalizado

```powershell
python -m datosdemocl generar --cantidad 12 --formato csv --salida .\ejemplos\ejemplo_personalizado.csv --semilla 2026 --campos "rut,nombre,region,comuna,categoria,monto_clp" --formato-rut sin_puntos --region "Biobío" --dominio-correo ejemplo.test
```

Son datos inventados para QA. **No son datos de personas reales.** Los RUT son
matemáticamente válidos y podrían coincidir con RUT ya emitidos; no se
consultó el Registro Civil ni el SII. Consulte la advertencia del README
principal.
