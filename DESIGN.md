---
theme:
  colors:
    background: "#101216"
    surface: "#181C22"
    surfaceElevated: "#20262F"
    border: "#2B333E"
    text: "#F3F5F7"
    textMuted: "#9AA4B2"
    primary: "#079C5E"
    info: "#7FA8FF"
    success: "#43C995"
    warning: "#F2B866"
    error: "#079C5E"
  spacing:
    page: "24px desktop / 16px Android"
    panel: "18px"
    section: "16px"
    control: "8px"
    queueGap: "10px"
  border:
    radius: "8px controls / 10-12px cards"
    width: "1px"
  effects:
    blur: "none"
    shadow: "none"
    gradients: "none"
---

# Sistema visual de DonLoader

DonLoader usa una interfaz oscura, sobria y rápida de leer. El rediseño mejora la
jerarquía y el estado de cada descarga sin añadir decoración que ralentice el
renderizado o compita con el formulario.

## Principios

- Superficies planas, bordes de un píxel y radios contenidos.
- Un solo acento expresivo: #079C5E para acciones y progreso activo.
- Verde, ámbar y #079C5E se reservan para éxito, proceso/advertencia y error.
- Tipografía del sistema; no cargar fuentes, imágenes decorativas ni efectos pesados.
- Animaciones breves solo para foco, hover y transición de estado.
- Nunca mostrar una calidad de video fija como si fuera real: MP4/MKV muestran
  resoluciones después de Analizar, usando únicamente la metadata recibida.
- Un estado vacío debe ser honesto: no incluir tareas, tamaños o velocidades simuladas.

## Composición compartida

El encabezado muestra la marca DonLoader y un indicador compacto del motor
yt-dlp. La configuración agrupa URL, formato, calidad y carpeta de destino.
La cola muestra formato, calidad elegida, estado, progreso, velocidad y ETA.

El formato MP3 revela solo bitrate de audio. MP4 y MKV revelan Analizar y, al
terminar el análisis, un selector con las alturas disponibles ordenadas de mayor
a menor. Si no hay alturas, se ofrece Mejor disponible.

## Escritorio

- Ventana inicial aproximada de 960x640, redimensionable, mínimo 820x560.
- Dos paneles: configuración a la izquierda y cola a la derecha.
- El URL tiene Pegar, validación inline y Analizar solo para video.
- La acción principal permanece visible al pie del panel izquierdo.
- La cola usa tarjetas compactas y un botón Limpiar completadas.
- El modo directo oculta la configuración y conserva la cola, el límite de tres
  descargas y el cierre automático.

## Android

- Tema Material oscuro fijo; no se usan colores dinámicos del sistema.
- Una sola LazyColumn, con ancho máximo cómodo en pantallas grandes.
- El flujo es URL → formato → Analizar → calidad real → añadir a cola.
- El botón de descarga se deshabilita durante el análisis o la actualización del motor.
- Las tarjetas conservan miniaturas vía Coil y acciones de cancelar/reintentar.
- La carpeta de destino sigue siendo una fila secundaria y usa SAF.

## Estados

| Estado | Color | Uso |
| --- | --- | --- |
| Motor listo / completado | #43C995 | Confirmación sin llamar la atención |
| Analizando / actualizando | #F2B866 | Trabajo temporal o advertencia |
| Descargando / acción | #079C5E | Progreso y acción primaria |
| Error | #079C5E | Fallos, validación y reintento |
| Informativo | #7FA8FF | Estado del motor y datos auxiliares |

El texto principal usa #F3F5F7; el secundario #9AA4B2. El fondo es
#101216, las superficies #181C22 y las superficies elevadas #20262F.
