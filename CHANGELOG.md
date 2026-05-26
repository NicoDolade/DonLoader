# Changelog - Downloader

Todos los cambios notables en este proyecto serán documentados en este archivo.

---

## [1.0.0] - 2026-05-26

### Añadido
- **Código unificado:** Consolidación de la interfaz de usuario de Tkinter y de la lógica de descarga en un único script principal `app.py`.
- **Modos de ejecución:** Soporte para modo interactivo (doble clic), modo directo (con parámetros de interfaz) y modo consola pura (`--no-gui`).
- **Optimizaciones de red:**
  - Limpieza de DNS (`ipconfig /flushdns`) al inicio del programa.
  - Activación de TCP Auto-Tuning en modo `normal` mediante comandos de netsh.
  - Descarga multi-hilo en parallel (8 hilos de descarga simultánea en `yt-dlp` en bloques de 10 MB).
- **Temática Catppuccin Mocha:** Interfaz gráfica oscura premium utilizando la paleta de colores oficial de Catppuccin Mocha (Base, Surface, Text, Accent Blue, Green, Red).
- **Icono Squircle Personalizado:** Icono con diseño de Inteligencia Artificial de bordes redondeados y transparencia real en los bordes, aplicado al archivo `.exe`, la barra de título de la ventana y en la barra de tareas de Windows.
- **Empaquetado estático:** Inclusión interna automática de los ejecutables de FFmpeg y FFprobe para asegurar la conversión de audio a MP3 y fusión de pistas de video/audio sin dependencias del sistema.
- **Flujo de UAC:** Configuración del manifest del ejecutable para requerir permisos de administrador de forma obligatoria durante el arranque.
