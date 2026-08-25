# DonLoader — Prompts visuales sincronizados

DonLoader es un descargador multimedia portable para escritorio y Android.
La interfaz debe ser simple, oscura, plana y rápida. La versión funcional actual
es v1.3.1.

Reglas para todos los prompts:

- No usar glassmorphism, blur, degradados, sombras fuertes ni fondos decorativos.
- No inventar tareas, tamaños, velocidades ni resoluciones en estados vacíos.
- Mantener el límite de tres descargas simultáneas, FFmpeg, aria2c, SAF,
  actualizaciones y descargas en segundo plano.
- MP3 muestra bitrate. MP4/MKV requieren el flujo Analizar antes de mostrar
  calidades reales; si la metadata no informa alturas, mostrar Mejor disponible.

## 1. Base visual

Prompt:

Diseña DonLoader con fondo #101216, superficies planas #181C22 y #20262F,
texto principal #F3F5F7, texto secundario #9AA4B2 y coral #FF6B5B para la
acción principal. Usa bordes #2B333E, radios de 8 a 12 px y tipografía del
sistema. Verde #43C995, ámbar #F2B866 y #079C5E son exclusivamente estados.
La composición debe sentirse sobria, clara y ligera, sin blur, degradados,
glassmorphism ni sombras pesadas.

## 2. Escritorio: dos paneles

Prompt:

Diseña una ventana redimensionable de DonLoader cercana a 960x640, con mínimo
usable 820x560. Usa dos paneles: a la izquierda Nueva descarga con URL, botón
Pegar, formato segmentado MP3/MP4/MKV, carpeta de destino y acción principal; a
la derecha Cola de descargas con tarjetas compactas y scroll. El encabezado
muestra DonLoader y un pill pequeño del estado de yt-dlp. El estado vacío solo
dice que la cola está vacía y cómo empezar. Añade Limpiar completadas. Sin datos
de ejemplo.

## 3. Flujo de video

Prompt:

Para MP4 y MKV muestra un botón Analizar junto al formulario. Después de pulsarlo,
indica que la metadata se consulta en segundo plano y muestra únicamente las
alturas reales disponibles ordenadas de mayor a menor: por ejemplo 1080p, 720p,
480p. Selecciona la mayor por defecto. No analices mientras el usuario escribe,
invalida el resultado si cambia la URL y muestra un error inline si falla.
Si no hay alturas, muestra Mejor disponible. MP3 solo muestra 128/192/256/320 kbps.

## 4. Android

Prompt:

Diseña la misma experiencia en una LazyColumn de una sola columna para teléfono
pequeño y pantalla ancha. Encabezado compacto con marca y estado del motor,
campo URL con Pegar, selector de formato, Analizar para video, selector de
calidad real, fila de carpeta y botón Añadir a la cola. Las tarjetas muestran
miniatura pequeña, formato y calidad, progreso, velocidad, ETA, cancelar y
reintentar. Mantén el diálogo de actualización y bloquea nuevas descargas
mientras yt-dlp se actualiza.

## 5. Tarjetas y estados

Prompt:

Cada tarjeta debe tener una superficie plana #181C22, borde de un píxel y
separación compacta. Mostrar título truncado, MP3 · 192k o MP4 · 720p, estado,
barra fina, velocidad y ETA. El progreso activo es coral, completado verde,
advertencias ámbar y errores #079C5E. Una tarea fallida ofrece reintentar; una
completada puede eliminarse con Limpiar completadas.
