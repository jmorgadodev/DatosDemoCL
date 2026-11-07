# Contribuir a DatosDemoCL

Gracias por ayudar a mejorar DatosDemoCL. El proyecto está escrito en Python,
usa la biblioteca estándar durante la ejecución y mantiene la generación de
datos local, sin red ni telemetría.

## Preparar el entorno

- Python 3.11 o superior.
- Tkinter para ejecutar y probar la GUI. En Windows normalmente viene con
  Python; en Linux puede requerir el paquete `python3-tk`.
- PyInstaller 6.13.0 sólo si vas a reconstruir el ejecutable de Windows:

```powershell
python -m pip install -r requirements-build.txt
```

No es necesario instalar el proyecto con `pip` para ejecutar el código fuente.

## Ejecutar las pruebas

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
```

Las pruebas de Tkinter se omiten si el entorno no puede abrir una ventana.
Antes de enviar un cambio, ejecuta la suite completa y añade pruebas para las
reglas de generación, validación o interacción que hayas modificado.

## Proponer cambios

1. Abre un issue para describir un error o una mejora de alcance significativo.
2. Crea una rama con un nombre breve, por ejemplo `fix/preview-empty-state`.
3. Mantén el cambio centrado en un solo propósito.
4. Actualiza README, changelog o decisiones técnicas si cambian las opciones,
   los campos, el comportamiento o el formato de salida.
5. Abre un pull request con el problema, la solución y el resultado de las
   pruebas.

Los reportes deben incluir la versión, Windows/Linux/macOS, versión de Python,
los pasos para reproducir y el resultado esperado. Usa datos ficticios en los
issues y pull requests; no adjuntes RUT, archivos ni información de clientes.

## Límites del proyecto

- No añadir conexiones de red, telemetría, servicios externos ni lectura de
  datos locales de terceros.
- No presentar RUT matemáticamente válidos como identidades necesariamente
  ficticias ni usar datos personales de clientes en pruebas.
- No afirmar que los ejemplos son anónimos o que son aptos para documentos
  tributarios.
- Mantener las dependencias de ejecución en la biblioteca estándar, salvo que
  un cambio aprobado justifique claramente lo contrario.
