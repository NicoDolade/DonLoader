# Resumen del Proyecto: Downloader Portable

Este documento presenta un resumen técnico simplificado del estado del proyecto **Downloader** y las tareas de compilación ejecutadas.

## 📝 Estado del Proyecto
El proyecto ha sido completado y empaquetado de manera exitosa. Todas las especificaciones acordadas han sido implementadas y probadas localmente en Windows.

## 📂 Archivos en el Directorio del Proyecto
- **`app.py`:** Código unificado que contiene la lógica de optimización del sistema, la GUI de Tkinter Catppuccin Mocha y la interacción con `yt-dlp` y `FFmpeg`.
- **`Downloader.spec`:** Especificación del empaquetador PyInstaller que maneja la incrustación de binarios locales, datos, metadatos y la solicitud de privilegios UAC.
- **`icon.ico`:** El icono del programa, procesado con bordes redondeados y transparencia real en los canales alfa externos.
- **`bin/`:** Subcarpeta que contiene `ffmpeg.exe` y `ffprobe.exe`.
- **`dist/Downloader.exe`:** El archivo ejecutable final compilado listo para su distribución.

## ⚙️ Parámetros Técnicos Clave
- **Hilos de descarga:** 8 hilos simultáneos por fragmento para exprimir la velocidad de red.
- **Formato soportado:** MP3 (calidades de 128 a 320 kbps), MP4 y MKV.
- **UAC:** Configurado como `requireAdministrator` en el manifiesto.
- **Ruta de extracción temporal:** `sys._MEIPASS` (donde se descomprimen automáticamente `ffmpeg.exe`, `ffprobe.exe` e `icon.ico` al arrancar).
