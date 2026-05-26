# Downloader - Aplicación Portable y Optimizada

**Downloader** es una aplicación de escritorio para Windows diseñada para descargar videos y audio de internet (usando la potencia de `yt-dlp` y `FFmpeg`) a la máxima velocidad permitida por tu conexión de red. 

Se compila en un único archivo ejecutable portable (`Downloader.exe`) e independiente, lo que significa que no requiere instalación de dependencias, Python ni configuraciones complejas para el usuario final.

---

## 🚀 Características Principales

1. **Portabilidad Absoluta:** Un único archivo `.exe` que incluye internamente el intérprete de Python, las librerías necesarias (`yt-dlp`, `requests`) y los binarios estáticos de **FFmpeg** y **FFprobe**.
2. **Optimización de Red TCP y DNS:** Al iniciarse (con privilegios de Administrador), la aplicación vacía automáticamente la caché de DNS (`ipconfig /flushdns`) y configura la optimización global de Windows para paquetes TCP (`netsh int tcp set global autotuninglevel=normal`).
3. **Descarga Ultra-Rápida:** Fuerza a `yt-dlp` a descargar en paralelo utilizando **8 hilos simultáneos** y fragmentos de 10 MB para exprimir al máximo tu ancho de banda de red.
4. **Diseño Visual Premium:** Interfaz gráfica moderna en Tkinter basada en la paleta de colores oscuros **Catppuccin Mocha**, con barra de progreso fluida e interactiva, velocidad real de transferencia en MB/s y cálculo estimado de tiempo (ETA).
5. **Icono Squircle con Transparencia:** Icono personalizado de bordes redondeados flotante, integrado a la perfección en la barra de tareas de Windows y en la barra de título de la aplicación.

---

## 🛠️ Modos de Ejecución

La aplicación soporta tres flujos de trabajo según las necesidades del usuario:

### A. Modo Interactivo (Doble Clic)
Si abres la aplicación directamente haciendo doble clic en `Downloader.exe`:
- Muestra una pantalla de inicio donde puedes pegar la URL del video.
- Permite seleccionar el formato de salida (**MP3**, **MP4** o **MKV**).
- Permite ajustar la calidad de conversión de audio (128, 192, 256 o 320 kbps) si eliges MP3.
- Permite examinar tu equipo para definir la carpeta de destino (por defecto, la carpeta de descargas del usuario).
- Al finalizar con éxito, la aplicación **permanece abierta** mostrando una pantalla de éxito con la opción de descargar otro video o cerrar.

### B. Modo Directo (Integrado / Parámetros)
Si ejecutas la aplicación pasando el argumento de la URL:
```powershell
.\Downloader.exe -u "https://www.youtube.com/watch?v=Ejemplo"
```
- Salta directamente a la pantalla de descarga mostrando el progreso de forma visual.
- Al completarse la descarga con éxito, la aplicación **se cierra automáticamente** tras 1.5 segundos.

### C. Modo Consola (CLI Puro)
Si deseas ejecutar la descarga de forma silenciosa dentro de un script o terminal:
```powershell
.\Downloader.exe -u "https://www.youtube.com/watch?v=Ejemplo" --no-gui
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
   python -m PyInstaller --clean Downloader.spec
   ```
4. El ejecutable compilado estará listo en la carpeta `dist/Downloader.exe`.
