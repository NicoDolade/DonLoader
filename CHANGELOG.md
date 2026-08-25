# Changelog - DonLoader

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [Unreleased]

## [1.3.3] - 2026-08-25

### Añadido
- **Temas persistentes:** Se agregaron los temas Oscuro, Claro, Océano, Pizarra y Arena. El selector vive como un control compacto en el encabezado y la elección se conserva al reiniciar la aplicación en escritorio y Android. Todos mantienen `#079C5E` como acento de marca.

### Modificado
- **Flujo progresivo de descarga:** Al abrir DonLoader solo se muestran la URL y la carpeta de destino. Al pegar una URL aparece el formato; MP3 revela su bitrate y MP4/MKV revelan Analizar y las calidades reales. La carpeta elegida se conserva y el formulario vuelve a su estado inicial después de iniciar una descarga.
- **Acción principal:** El botón ahora se llama **Descargar** y solo aparece cuando la URL, el formato y la calidad requerida están listos. Al pulsarlo la tarea comienza automáticamente; las siguientes tareas siguen esperando en la cola interna de hasta tres descargas simultáneas.
- **Animaciones ligeras:** Se agregaron transiciones breves de aparición/ocultamiento, selección de formato y hover, sin blur, sombras ni efectos pesados.

## [1.3.2] - 2026-08-25

### Añadido
- **Descargas en segundo plano (Android):** El Foreground Service se inicia al encolar o reintentar una tarea y mantiene la descarga activa al minimizar la app o quitar su actividad de recientes. La notificación muestra el progreso global y el servicio se detiene únicamente cuando una cola que estuvo activa queda inactiva.

### Modificado
- **Acento principal:** Botones, formato seleccionado, foco y progreso activo ahora usan `#079C5E` en lugar del coral anterior.

## [1.3.1] - 2026-08-25

### Modificado
- **Color de estados:** Se reemplazó el rojo de errores y validaciones por `#079C5E` en escritorio, Android y el sistema visual documentado.

## [1.3.0] - 2026-08-20

### Añadido
- **Calidad real de video:** MP4/MKV consultan metadata con `yt-dlp` sin descargar, muestran alturas únicas disponibles y permiten elegir un límite máximo (`videoQuality`). Si no hay alturas, se usa `Mejor disponible`; el CLI incorpora `--video-quality`.
- **Flujo de análisis en Android:** Nuevo `VideoQualityState` con estados inactivo, analizando, listo y error; la selección se invalida al cambiar la URL y se conserva en cada tarea.
- **Limpieza de cola:** Escritorio y Android incorporan `Limpiar completadas`.

### Modificado
- **Rediseño visual:** Escritorio con dos paneles y Android con `LazyColumn`, tema oscuro fijo, superficies planas, coral como acción principal y estados semánticos. Se eliminaron blur, glassmorphism, degradados y controles de calidad ficticios.
- **Selector de formatos:** MP3 mantiene bitrate de audio; MP4/MKV priorizan el contenedor correspondiente y combinan video/audio mediante FFmpeg sin superar la resolución elegida.

## [1.2.9] - 2026-07-23

### Corregido
- **Acumulación de APKs en la caché interna (Android):** Se robusteció `AppUpdater.clearUpdateCache()` para borrar **todos** los `*.apk` que queden en la caché (no solo `update.apk` literal), incluye reintentos con backoff cuando el archivo está lockeado por el `PackageInstaller` de Android, y barre también archivos temporales huérfanos (`.part`, `.tmp`, `.temp`, `.download`, `.crdownload`) en todo el árbol de la caché. Se loguea en `logcat` el espacio total liberado.
- **Limpieza post-instalación inmediata:** Se registró un `BroadcastReceiver` en `DonLoaderApp` para `ACTION_MY_PACKAGE_REPLACED` que dispara `clearUpdateCache()` automáticamente al completarse la instalación de una actualización OTA. Resuelve el caso típico donde el `delete()` en `MainActivity.onCreate` fallaba porque el instalador aún tenía lock sobre el APK; el receiver corre cuando Android ya liberó el lock.

---

## [1.2.8] - 2026-07-23

### Añadido
- **Estado del Motor yt-dlp Visible y Bloqueante (Android):** Nuevo `EngineStatus` (`Unknown` / `Updating` / `UpToDate` / `Failed`) emitido por `DownloadManager` y observado por la UI. Mientras el motor se está actualizando:
  - Banner azul con spinner arriba del botón **Descargar** mostrando "Actualizando motor yt-dlp — Las descargas se habilitarán al terminar".
  - Botón **Descargar** deshabilitado y texto cambiado a "Esperando motor yt-dlp...".
  - No se inicia ningún `processDownload` nuevo hasta que el motor quede en `UpToDate`.
  - Si la actualización falla (sin red / rate-limit), banner rojo persistente con "Motor yt-dlp desactualizado" + botón **Reintentar** que dispara `refreshEngine()` manualmente.
- **`DownloadManager.refreshEngine()`:** Punto único de actualización del binario `yt-dlp` (canal `STABLE`). Reentrante: llamadas concurrentes se ignoran mientras hay una en curso. Reemplaza las dos llamadas duplicadas previas (`DonLoaderApp.updateYtDlpAsync` y el `updateYoutubeDL` inline de `retryDownload`).
- **`retryDownload` ahora espera al motor:** Si el motor no está al día al reintentar una tarea fallida, primero dispara `refreshEngine()` y aguarda con `_engineStatus.first { it !is EngineStatus.Updating }` antes de re-colar, garantizando que la re-descarga use yt-dlp fresco.

### Modificado
- **`DonLoaderApp` simplificado:** Se eliminó la corrutina `updateYtDlpAsync` propia. La inicialización nativa (YoutubeDL/FFmpeg/Aria2c) sigue en `DonLoaderApp.onCreate`, pero la actualización de yt-dlp la delega al singleton `DownloadManager` para que su estado sea observable y la UI pueda bloquear/reaccionar.

### Corregido
- **Carrera entre actualización de yt-dlp y primera descarga (raíz del HTTP 403):** Ya no es posible disparar una descarga con el `yt-dlp` bundled antes de que termine la actualización inicial; la UI bloquea el botón hasta `UpToDate` y muestra el progreso.

---

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
