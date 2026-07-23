# Changelog - DonLoader

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [1.2.7] - 2026-07-23

### Añadido
- **Reintento de Descargas Fallidas con Auto-Update de yt-dlp (Android):** Botón de reintento (ícono `Refresh`) en las tarjetas de la cola con estado `FALLIDO`. Al pulsarlo se fuerza sincrónicamente una actualización de `yt-dlp` (canal `STABLE`) antes de re-colar la tarea, resolviendo el error `HTTP 403 Forbidden` que YouTube devuelve cuando la versión bundled de yt-dlp quedó obsoleta o la actualización automática al iniciar la app no llegó a completarse antes de la primera descarga.

### Corregido
- **HTTP 403 Forbidden en YouTube (Android):** Se eliminó la condición de carrera en la que una descarga podía dispararse con el `yt-dlp` bundled antes de que la actualización automática de `DonLoaderApp.onCreate` finalizara. El usuario ahora puede recuperar la descarga fallida con un toque sin reinstalar la app.

---

## [1.2.6] - 2026-07-23

### Añadido
- **Foreground Service de Descargas (Android):** Se implementó `DownloadService`, un Foreground Service con notificación persistente que hospeda el `DownloadManager` desacoplado del ciclo de vida de la Activity. Las descargas nativas de `yt-dlp` ya no se cancelan al minimizar la app o cambiar a otra aplicación, y la notificación muestra el progreso global (cantidad activa + porcentaje promedio). Se agregaron los permisos `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_DATA_SYNC` y `POST_NOTIFICATIONS`, y la solicitud runtime en Android 13+.
- **Miniaturas de Video en la Cola (Android):** Se extendió `DownloadTask` con `thumbnailUrl` y se extrae la URL de miniatura desde `getInfo()` de yt-dlp durante la fase `EXTRAYENDO`. Las tarjetas de descarga muestran ahora la miniatura del video cargada con la librería Coil (`coil-compose`), con placeholder Catppuccin mientras carga o si falla.

### Modificado
- **`DownloadManager` como Singleton (Android):** Se convirtió `DownloadManager` en un singleton gestionado por el `Application` (`companion object` con `get(context)`) para que su `CoroutineScope` sobreviva independientemente del `ViewModel`/Activity. El `ViewModel` ahora solo observa el `StateFlow` expuesto.
- **Arranque del Servicio en el ViewModel (Android):** `MainScreenViewModel.init` ahora invoca `DownloadService.start(application)` para garantizar que el servicio esté activo apenas la UI compone por primera vez.

---

## [1.2.5] - 2026-05-27

### Añadido
- **Auto-Actualización de yt-dlp (Android):** Se implementó la actualización automática y asíncrona del binario nativo `yt-dlp` en segundo plano en cada inicio de la aplicación. Esto asegura que las firmas y extractores de YouTube y otras plataformas se mantengan siempre actualizados, evitando errores por obsolescencia del motor de descargas.

### Corregido
- **Filtro de Errores en UI (Android):** Se añadió un filtro inteligente para limpiar los mensajes de error mostrados en la interfaz. Ahora se omiten advertencias repetitivas de expiración ("older than 90 days", etc.) y logs nativos ruidosos para mostrar únicamente el mensaje de error final y evitar que se trunque la información en la pantalla.

---

## [1.2.4] - 2026-05-27

### Añadido
- **Limpieza Automática de Caché al Iniciar (Android):** Se implementó un sistema de limpieza en el arranque de la aplicación que borra automáticamente cualquier APK de actualización antiguo (`update.apk`) y archivos temporales de descargas huérfanas (`.part`), evitando que la app acumule espacio innecesario en el almacenamiento del celular.

### Corregido
- **Velocidad y ETA de Descarga (Android):** Corregido el bug que impedía ver la velocidad y el ETA de descarga. Se optimizó el analizador de expresiones regulares en `DownloadManager.kt` para ser insensible a mayúsculas/minúsculas y tolerar espacios, y se corrigió el bucle para conservar los últimos valores válidos obtenidos sin sobreescribirlos con cadenas vacías en líneas sin información de progreso.
- **Visualización en la UI (Android):** Se modificó la UI para renderizar de manera independiente la velocidad y el tiempo restante de descarga en la cola, adaptándose de forma elástica a la información provista por `yt-dlp` / `aria2c`.

---

## [1.2.3] - 2026-05-27

### Corregido
- **Versión Dinámica en el Footer (Android):** Se modificó la interfaz de usuario en `MainScreen.kt` para consultar dinámicamente la versión real instalada desde el `PackageManager` del sistema, solucionando el texto estático ("v1.2.0") que aparecía anteriormente en el pie de página.

---

## [1.2.2] - 2026-05-27

### Corregido
- **Esquinas del Icono en Android:** Eliminado por completo el reborde blanco residual de las esquinas del icono del launcher mediante un script de enmascarado optimizado (recorte con inset de 4px y radio de 51px), actualizando todas las densidades de mipmaps `.webp`.
- **Bucle Infinito de Actualizaciones:** Corregido el bucle infinito del actualizador en Android sincronizando la versión del manifiesto de Gradle (`versionName = "1.2.2"`, `versionCode = 2`) y la de la aplicación de escritorio en `app.py` con el tag de la release.

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
