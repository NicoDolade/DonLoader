# DonLoader - Aplicación Portable y Optimizada

**DonLoader** es una aplicación de escritorio para Windows diseñada para descargar videos y audio de internet (usando la potencia de `yt-dlp` y `FFmpeg`) a la máxima velocidad permitida por tu conexión de red. 

Se compila en un único archivo ejecutable portable (`DonLoader.exe`) e independiente, lo que significa que no requiere instalación de dependencias, Python ni configuraciones complejas para el usuario final.

---

## 🚀 Características Principales

1. **Portabilidad Absoluta:** Un único archivo `.exe` que incluye internamente el intérprete de Python, las librerías necesarias y los binarios estáticos de **FFmpeg** y **FFprobe**.
2. **Cola de Descargas en Paralelo (Queue Manager):** Permite encolar múltiples descargas de forma ilimitada. El programa ejecuta un máximo de 3 descargas simultáneamente, manteniendo las demás en espera ("En cola...") y arrancándolas automáticamente a medida que finalizan las activas.
3. **Creación Automática de Subcarpetas:** Para cada descarga, el programa crea una subcarpeta con el título sanitizado del video/audio dentro del directorio de destino seleccionado, guardando allí el archivo para mantener tu disco organizado.
4. **Auto-actualización Interactiva con Auto-reinicio:** Al iniciar, busca silenciosamente nuevas versiones de la librería `yt-dlp` en PyPI. Si encuentra una, muestra una interfaz modal flotante con barra de progreso, descarga la actualización en segundo plano e inicia automáticamente un auto-reinicio (`os.execv`) para que surta efecto de inmediato.
5. **Optimización de Red TCP y DNS:** Al iniciarse (con privilegios de Administrador), la aplicación vacía automáticamente la caché de DNS (`ipconfig /flushdns`) y configura la optimización global de Windows para paquetes TCP (`netsh int tcp set global autotuninglevel=normal`).
6. **Descarga Ultra-Rápida:** Fuerza a `yt-dlp` a descargar en paralelo utilizando **8 hilos simultáneos** y fragmentos de 10 MB para exprimir al máximo tu ancho de banda de red.
7. **Diseño Visual Premium:** Interfaz gráfica moderna en Tkinter basada en la paleta de colores oscuros **Catppuccin Mocha**, con un panel inferior scrollable e interactivo para visualizar el estado y progreso individual de cada descarga de la cola, y una barra inferior limpia.
8. **Icono Squircle con Transparencia:** Icono personalizado de bordes redondeados, integrado en la barra de tareas de Windows y en la barra de título de la aplicación.

---

## 🛠️ Modos de Ejecución

La aplicación soporta tres flujos de trabajo según las necesidades del usuario:

### A. Modo Interactivo (Doble Clic)
Si abres la aplicación directamente haciendo doble clic en `DonLoader.exe`:
- Muestra una pantalla de inicio donde puedes pegar la URL del video.
- Permite seleccionar el formato de salida (**MP3**, **MP4** o **MKV**).
- Permite ajustar la calidad de conversión de audio (128, 192, 256 o 320 kbps) si eliges MP3.
- Permite examinar tu equipo para definir la carpeta de destino (por defecto, la carpeta de descargas del usuario).
- Muestra la barra inferior con la versión cargada (ej: `DonLoader v1.2.0`).
- Al hacer clic en Descargar, la URL se añade a la cola visual en tiempo real en la mitad inferior de la pantalla y el campo de texto se vacía inmediatamente, permitiendo seguir añadiendo más descargas al instante sin interrupciones.

### B. Modo Directo (Integrado / Parámetros)
Si ejecutas la aplicación pasando el argumento de la URL:
```powershell
.\DonLoader.exe -u "https://www.youtube.com/watch?v=Ejemplo"
```
- Salta directamente a la pantalla de descarga mostrando el progreso de forma visual.
- Al completarse la descarga con éxito, la aplicación **se cierra automáticamente** tras 1.5 segundos.

### C. Modo Consola (CLI Puro)
Si deseas ejecutar la descarga de forma silenciosa dentro de un script o terminal:
```powershell
.\DonLoader.exe -u "https://www.youtube.com/watch?v=Ejemplo" --no-gui
```
- No abre ninguna ventana de interfaz gráfica.
- Muestra la barra de progreso Unicode en la propia consola.

---

## 🏗️ Cómo Compilar desde el Código Fuente

Si deseas realizar modificaciones en el código fuente (`app.py`) y volver a compilar tu propio ejecutable, sigue estos pasos:

1. Asegúrate de tener Python instalado y las dependencias del compilador:
   ```powershell
   pip install pyinstaller yt-dlp pillow requests
   ```
2. Asegúrate de que los binarios estáticos de `ffmpeg.exe` y `ffprobe.exe` se encuentren dentro de la subcarpeta `bin/`.
3. Ejecuta la compilación con PyInstaller usando el archivo de configuración `.spec` provisto:
   ```powershell
   python -m PyInstaller --clean DonLoader.spec
   ```
4. El ejecutable compilado estará listo en la carpeta `dist/DonLoader.exe`.
