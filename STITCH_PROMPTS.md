# DonLoader — Prompts visuales sincronizados

DonLoader es un descargador multimedia portable para escritorio y Android.
La interfaz debe ser simple, plana y rápida. El tema Oscuro actual es el
predeterminado, pero la app ofrece también Claro, Océano, Pizarra y Arena.
La versión funcional actual es v1.3.3.

Reglas para todos los prompts:

- No usar glassmorphism, blur, degradados, sombras fuertes ni fondos decorativos.
- No inventar tareas, tamaños, velocidades ni resoluciones en estados vacíos.
- Mantener un selector de tema pequeño en el encabezado; nunca agregar una
  pantalla de ajustes ni un control flotante intrusivo. Persistir la elección.
- Mantener el límite de tres descargas simultáneas, FFmpeg, aria2c, SAF,
  actualizaciones y descargas en segundo plano.
- MP3 muestra bitrate. MP4/MKV requieren el flujo Analizar antes de mostrar
  calidades reales; si la metadata no informa alturas, mostrar Mejor disponible.

## 1. Base visual

Prompt:

Diseña DonLoader con una paleta plana seleccionable: Oscuro usa fondo #101216,
superficies #181C22 y #20262F, texto #F3F5F7/#9AA4B2 y #079C5E para la acción
principal; Claro usa superficies blancas y fondos #F4F7F5; Océano, Pizarra y
Arena cambian los neutros sin cambiar el acento #079C5E. Usa bordes contenidos,
radios de 8 a 12 px y tipografía del sistema. La composición debe sentirse
sobria, clara y ligera, sin blur, degradados, glassmorphism ni sombras pesadas.

## 2. Escritorio: dos paneles

Prompt:

Diseña una ventana redimensionable de DonLoader cercana a 960x640, con mínimo
usable 820x560. Usa dos paneles: a la izquierda Nueva descarga con URL, botón
Pegar y carpeta de destino visibles al inicio. Cuando se pega una URL, revela el
formato segmentado MP3/MP4/MKV; al elegir formato revela bitrate de audio o el
flujo de análisis de video. Muestra **Descargar** solo cuando la selección está
completa y ocúltalo después de iniciar la tarea; la carpeta debe permanecer.
A la derecha usa Cola de descargas con tarjetas compactas y scroll. El encabezado
muestra DonLoader y un pill pequeño del estado de yt-dlp. El estado vacío solo
dice que la cola está vacía y cómo empezar. Añade Limpiar completadas. Sin datos
de ejemplo.

## 3. Flujo de video

Prompt:

Para MP4 y MKV muestra un botón Analizar junto al selector de calidad. Después de pulsarlo,
indica que la metadata se consulta en segundo plano y muestra únicamente las
alturas reales disponibles ordenadas de mayor a menor: por ejemplo 1080p, 720p,
480p. Selecciona la mayor por defecto. No analices mientras el usuario escribe,
invalida el resultado si cambia la URL y muestra un error inline si falla.
Si no hay alturas, muestra Mejor disponible. MP3 solo muestra 128/192/256/320 kbps.

## 4. Android

Prompt:

Diseña la misma experiencia en una LazyColumn de una sola columna para teléfono
pequeño y pantalla ancha. Al entrar muestra solo el campo URL con Pegar y la
fila de carpeta persistida. Al escribir una URL revela el selector de formato;
MP3 revela audio y MP4/MKV revelan Analizar y calidad real. Muestra el botón
**Descargar** únicamente cuando todo está listo y, después de pulsarlo, vuelve al
estado inicial sin ocultar la carpeta. Las tarjetas muestran miniatura pequeña,
formato y calidad, progreso, velocidad, ETA, cancelar y reintentar. Mantén el
diálogo de actualización y bloquea nuevas descargas mientras yt-dlp se actualiza.
Usa transiciones breves de fade/expand y cambios suaves de selección, sin efectos
pesados.

Incluye en el encabezado un icono pequeño de paleta que abre un menú con Oscuro,
Claro, Océano, Pizarra y Arena. El tema elegido debe mantenerse al reiniciar.

## 5. Tarjetas y estados

Prompt:

Cada tarjeta debe tener una superficie plana #181C22, borde de un píxel y
separación compacta. Mostrar título truncado, MP3 · 192k o MP4 · 720p, estado,
barra fina, velocidad y ETA. El progreso activo usa #079C5E, completado verde,
advertencias ámbar y errores #079C5E. Una tarea fallida ofrece reintentar; una
completada puede eliminarse con Limpiar completadas.
