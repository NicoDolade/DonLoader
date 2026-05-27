# Changelog - DonLoader

Todos los cambios notables en este proyecto serán documentados en este archivo.

---

## [1.2.0] - 2026-05-27

### Añadido
- **Cola de múltiples descargas en paralelo (Queue Manager):** Soporte para añadir múltiples URLs a descargar de forma simultánea. Se procesan un máximo de 3 descargas concurrentes en paralelo y el resto permanecen en espera ("En cola...") hasta que se liberen hilos.
- **Creación de subcarpetas automática:** Cada archivo descargado se guarda automáticamente dentro de una subcarpeta con el nombre del título sanitizado del video en el directorio de destino seleccionado.
- **Diálogo modal de actualización con auto-reinicio:** Diálogo flotante modal (`tk.Toplevel`) con estética Catppuccin Mocha que muestra el progreso de actualización de `yt-dlp`. Al finalizar, el programa se reinicia a sí mismo inmediatamente mediante `os.execv()`.
- **Limpieza de Barra de Estado (Footer):** Pie de página optimizado que solo muestra la versión `DonLoader v1.2.0` y el estado de la actualización (`Buscando...`, `Al día` o `Actualizando...`), reduciendo ruidos visuales.

---

## [1.1.0] - 2026-05-26

### Añadido
- **Auto-actualización asíncrona:** Búsqueda en segundo plano de actualizaciones para la librería `yt-dlp` desde PyPI, con descarga automática, extracción y carga dinámica en el siguiente inicio (`sys.path.insert`).
- **Barra de Estado (Footer):** Franja inferior en la GUI que muestra la versión del programa, la versión actual de la librería descargadora y el estado de la búsqueda de actualizaciones en tiempo real.
- **Workflow de GitHub Actions:** Archivo de integración continua `.github/workflows/build.yml` configurado en Windows para compilar y publicar de forma automatizada los ejecutables `DonLoader.exe` al subir tags de versión.
- **Regla de Sincronización:** Documentación formalizada de que todo cambio debe actualizar el Changelog, el Summary y el archivo de contexto del asistente.

### Modificado
- **Renombrado General:** Cambiado el nombre de toda la aplicación y proyecto de "Downloader" a "DonLoader".
- **Mejoras Visuales:** Refinado de las transiciones de botones con hovers y re-dimensionamiento de la ventana para acomodar el footer sin alterar la disposición de los campos de texto principales.

---

## [1.0.0] - 2026-05-26

### Añadido
- **Código unificado:** Consolidación de la interfaz de usuario de Tkinter y de la lógica de descarga en un único script principal `app.py`.
- **Modos de ejecución:** Soporte para modo interactivo (doble clic), modo directo (con parámetros de interfaz) y modo consola pura (`--no-gui`).
- **Optimizaciones de red:**
  - Limpieza de DNS (`ipconfig /flushdns`) al inicio del programa.
  - Activación de TCP Auto-Tuning en modo `normal` mediante comandos de netsh.
  - Descarga multi-hilo en paralelo (8 hilos de descarga simultánea en `yt-dlp` en bloques de 10 MB).
- **Temática Catppuccin Mocha:** Interfaz gráfica oscura premium utilizando la paleta de colores oficial de Catppuccin Mocha.
- **Icono Squircle Personalizado:** Icono de bordes redondeados y transparencia real en los bordes.
- **Empaquetado estático:** Inclusión interna automática de los ejecutables de FFmpeg y FFprobe.
- **Flujo de UAC:** Configuración del manifest del ejecutable para requerir permisos de administrador de forma obligatoria durante el arranque.
