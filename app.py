import os
import sys
import threading
import argparse
import subprocess
import urllib.request
import json
import zipfile
import shutil
import re
import tkinter as tk
from tkinter import filedialog

# Cargar versión actualizada de yt-dlp si existe
def check_and_load_yt_dlp_update():
    try:
        if sys.platform == 'win32':
            base_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'DonLoader')
        else:
            base_dir = os.path.join(os.path.expanduser('~'), '.donloader')
        updates_dir = os.path.join(base_dir, 'updates')
        if os.path.exists(os.path.join(updates_dir, 'yt_dlp')):
            sys.path.insert(0, updates_dir)
    except Exception:
        pass

check_and_load_yt_dlp_update()

import yt_dlp

# Versión de la aplicación (SemVer)
APP_VERSION = "v1.3.1"

# Identidad visual DonLoader: oscura, sobria y con un único acento expresivo.
BG_COLOR = "#101216"
SURFACE_COLOR = "#181C22"
SURFACE_ELEVATED = "#20262F"
BORDER_COLOR = "#2B333E"
TEXT_PRIMARY = "#F3F5F7"
TEXT_SECONDARY = "#9AA4B2"
ACCENT_PRIMARY = "#FF6B5B"
ACCENT_BLUE = "#7FA8FF"       # Estado informativo del motor
ACCENT_GREEN = "#43C995"      # Éxito
ACCENT_RED = "#079C5E"        # Error
ACCENT_AMBER = "#F2B866"      # Actualización / advertencia


def extract_video_heights(info):
    """Devuelve alturas de video únicas, ordenadas de mayor a menor.

    yt-dlp puede devolver formatos de audio, video progresivo y streams
    separados. Los formatos sin altura conocida no se presentan como una
    resolución numérica para no prometer una calidad que no conocemos.
    """
    heights = set()
    for media_format in (info.get("formats") or []):
        vcodec = media_format.get("vcodec")
        if vcodec is not None and str(vcodec).lower() == "none":
            continue
        try:
            height = int(media_format.get("height") or 0)
        except (TypeError, ValueError):
            height = 0
        if height > 0:
            heights.add(height)

    # Algunos extractores informan la altura solo en el objeto principal.
    if not heights:
        try:
            top_level_height = int(info.get("height") or 0)
        except (TypeError, ValueError):
            top_level_height = 0
        if top_level_height > 0:
            heights.add(top_level_height)

    return sorted(heights, reverse=True)


def build_video_format_selector(media_format, video_quality=None):
    """Construye una selección de yt-dlp que nunca supere la altura elegida."""
    if video_quality is None:
        if media_format == "mp4":
            return "bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/b"
        return "bv*+ba/b"

    try:
        height = int(video_quality)
    except (TypeError, ValueError):
        return build_video_format_selector(media_format, None)

    # El primer grupo prefiere streams compatibles con el contenedor elegido.
    # El segundo permite formatos separados de cualquier extensión cuando el
    # sitio no ofrece MP4 a esa altura. El fallback worst mantiene el límite.
    if media_format == "mp4":
        return (
            f"bv*[height<={height}][ext=mp4]+ba[ext=m4a]"
            f"/bv*[height<={height}]+ba/b[height<={height}]"
            f"/wv*[height<={height}]+ba/w[height<={height}]"
        )
    return f"bv*[height<={height}]+ba/b[height<={height}]/wv*[height<={height}]+ba/w[height<={height}]"


def positive_int(value):
    """Tipo de argparse para alturas de video mayores que cero."""
    try:
        parsed = int(value)
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError("debe ser un número entero") from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError("debe ser mayor que cero")
    return parsed

def sanitize_filename(name):
    """Sanitiza el nombre eliminando caracteres no permitidos en rutas de Windows."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def optimize_network():
    """Ejecuta optimizaciones globales de red en Windows."""
    if sys.platform == 'win32':
        try:
            # Vaciar caché de DNS
            subprocess.run(["ipconfig", "/flushdns"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL, 
                           creationflags=0x08000000)
            # Forzar TCP Auto-Tuning a normal
            subprocess.run(["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL, 
                           creationflags=0x08000000)
        except Exception:
            pass

def update_yt_dlp_worker(app_instance):
    """Hilo secundario para buscar y descargar actualizaciones de yt-dlp con auto-reinicio."""
    try:
        # Obtener versión actual de yt_dlp
        current_version_str = getattr(yt_dlp, '__version__', '0.0.0')
        
        # Obtener rutas
        if sys.platform == 'win32':
            base_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'DonLoader')
        else:
            base_dir = os.path.join(os.path.expanduser('~'), '.donloader')
        updates_dir = os.path.join(base_dir, 'updates')
        os.makedirs(updates_dir, exist_ok=True)
        
        version_file = os.path.join(updates_dir, 'version.txt')
        local_version_str = '0.0.0'
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    local_version_str = f.read().strip()
            except Exception:
                pass
                
        # Consultar PyPI
        app_instance.set_update_status("Buscando...")
        url = "https://pypi.org/pypi/yt-dlp/json"
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': f'Mozilla/5.0 DonLoader/{APP_VERSION}'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        latest_version_str = data['info']['version']
        
        # Comparar versiones usando tuplas de enteros
        def parse_ver(v_str):
            clean_str = ''.join(c if c.isdigit() or c == '.' else '' for c in v_str)
            parts = clean_str.split('.')
            return tuple(int(x) for x in parts if x.isdigit())
            
        current_ver = parse_ver(current_version_str)
        local_ver = parse_ver(local_version_str)
        latest_ver = parse_ver(latest_version_str)
        
        effective_ver = max(current_ver, local_ver)
        
        if latest_ver > effective_ver:
            app_instance.set_update_status("Actualizando...")
            app_instance.show_update_dialog(latest_version_str, data, updates_dir, version_file)
        else:
            app_instance.set_update_status("Al día")
            
    except Exception:
        app_instance.set_update_status("Sin actualizaciones")

def get_downloads_folder():
    """Retorna la ruta de la carpeta de descargas del usuario."""
    return os.path.join(os.path.expanduser('~'), 'Downloads')

def get_ffmpeg_path():
    """Encuentra el ejecutable ffmpeg.exe empaquetado o en desarrollo."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Intenta buscar en la subcarpeta bin del directorio base
    ffmpeg_path = os.path.join(base_path, "bin", "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
        
    # Intenta buscar en el directorio superior para el entorno de desarrollo del plugin
    ffmpeg_path = os.path.join(os.path.dirname(base_path), "bin", "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
        
    return "ffmpeg.exe"

class ModernButton(tk.Button):
    """Botón personalizado plano y con animaciones de hover."""
    def __init__(self, master, **kwargs):
        self.normal_bg = kwargs.get("bg", ACCENT_BLUE)
        self.hover_bg = kwargs.get("hover_bg")
        self.normal_fg = kwargs.get("fg", "#11111b")
        
        # Eliminar kwargs personalizados antes de inicializar la superclase
        kwargs.pop("hover_bg", None)
        
        # Si no se define hover_bg, calcular uno armónico
        if not self.hover_bg:
            if self.normal_bg == ACCENT_BLUE:
                self.hover_bg = "#9DBBFF"
            elif self.normal_bg == ACCENT_GREEN:
                self.hover_bg = "#66DDAA"
            elif self.normal_bg == ACCENT_RED:
                self.hover_bg = "#FF8A8A"
            elif self.normal_bg == SURFACE_COLOR:
                self.hover_bg = BORDER_COLOR
            elif self.normal_bg == ACCENT_PRIMARY:
                self.hover_bg = "#FF8477"
            else:
                self.hover_bg = self.normal_bg
        
        super().__init__(master, relief="flat", activebackground=self.hover_bg, 
                         activeforeground=self.normal_fg, cursor="hand2", **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, e):
        self.config(bg=self.hover_bg)
        
    def on_leave(self, e):
        self.config(bg=self.normal_bg)

class ScrollableFrame(tk.Frame):
    """Contenedor scrollable vertical para las tareas de descarga."""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.canvas_frame, width=event.width)

class DownloadTask:
    """Tarjeta visual y ejecución de una descarga individual."""
    def __init__(self, app_instance, container, task_id, url, media_format, quality,
                 output_dir, video_quality=None):
        self.app = app_instance
        self.container = container
        self.id = task_id
        self.url = url
        self.media_format = media_format
        self.quality = quality
        self.video_quality = video_quality
        self.output_dir = output_dir

        self.status = "En cola"
        self.progress_percent = 0
        self.title = "Analizando enlace..."
        self.download_thread = None

        self.frame = tk.Frame(
            self.container,
            bg=SURFACE_COLOR,
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=BORDER_COLOR,
        )
        self.frame.pack(fill="x", pady=(0, 10), padx=2)

        self.header_frame = tk.Frame(self.frame, bg=SURFACE_COLOR)
        self.header_frame.pack(fill="x", padx=12, pady=(10, 5))

        quality_text = self._quality_text()
        self.format_label = tk.Label(
            self.header_frame,
            text=self.media_format.upper(),
            font=("Segoe UI", 8, "bold"),
            fg=TEXT_PRIMARY,
            bg=SURFACE_ELEVATED,
            padx=7,
            pady=3,
        )
        self.format_label.pack(side="left", padx=(0, 8))

        self.title_label = tk.Label(
            self.header_frame,
            text=self.title,
            font=("Segoe UI", 10, "bold"),
            fg=TEXT_PRIMARY,
            bg=SURFACE_COLOR,
            anchor="w",
            justify="left",
        )
        self.title_label.pack(side="left", fill="x", expand=True)

        self.status_label = tk.Label(
            self.header_frame,
            text=self.status,
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_SECONDARY,
            bg=SURFACE_COLOR,
            anchor="e",
        )
        self.status_label.pack(side="right", padx=(8, 0))

        self.canvas = tk.Canvas(self.frame, height=6, bg=SURFACE_ELEVATED, highlightthickness=0)
        self.canvas.pack(fill="x", padx=12, pady=(2, 7))
        self.progress_rect = self.canvas.create_rectangle(0, 0, 0, 6, fill=ACCENT_PRIMARY, width=0)

        self.meta_frame = tk.Frame(self.frame, bg=SURFACE_COLOR)
        self.meta_frame.pack(fill="x", padx=12, pady=(0, 10))

        self.info_label = tk.Label(
            self.meta_frame,
            text="Esperando en cola...",
            font=("Segoe UI", 8),
            fg=TEXT_SECONDARY,
            bg=SURFACE_COLOR,
            anchor="w",
        )
        self.info_label.pack(side="left", fill="x", expand=True)

        self.quality_label = tk.Label(
            self.meta_frame,
            text=quality_text,
            font=("Segoe UI", 8, "bold"),
            fg=TEXT_SECONDARY,
            bg=SURFACE_COLOR,
            anchor="e",
        )
        self.quality_label.pack(side="right", padx=(8, 0))

        self.canvas.bind("<Configure>", self._draw_progress)

    def _quality_text(self):
        if self.media_format == "mp3":
            return f"MP3 · {self.quality} kbps"
        if self.video_quality is None:
            return f"{self.media_format.upper()} · Mejor disponible"
        return f"{self.media_format.upper()} · {self.video_quality}p"

    def _draw_progress(self, event=None):
        canvas_width = self.canvas.winfo_width()
        target_width = int((self.progress_percent / 100.0) * canvas_width)
        self.canvas.coords(self.progress_rect, 0, 0, target_width, 6)

    def set_status(self, status, color=TEXT_SECONDARY):
        self.status = status
        self.status_label.config(text=status, fg=color)
        if status == "Completado":
            self.canvas.itemconfig(self.progress_rect, fill=ACCENT_GREEN)
        elif status in ("Descargando...", "Analizando..."):
            self.canvas.itemconfig(self.progress_rect, fill=ACCENT_PRIMARY)

    def set_info(self, info_text):
        self.info_label.config(text=info_text)

    def set_title(self, title):
        self.title = title
        display_title = title if len(title) <= 64 else title[:61] + "..."
        self.title_label.config(text=display_title)

    def update_progress(self, percent, info_text):
        self.progress_percent = percent
        self._draw_progress()
        self.set_info(info_text)

    def destroy(self):
        self.frame.destroy()

    def start(self):
        """Arranca el hilo de ejecución para esta tarea de descarga."""
        self.set_status("Analizando...", ACCENT_BLUE)
        self.set_info("Analizando URL del video...")
        self.download_thread = threading.Thread(target=self.run, daemon=True)
        self.download_thread.start()

    def progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            speed = d.get("speed")
            eta = d.get("eta")

            if total:
                percent = (downloaded / total) * 100
                downloaded_mb = downloaded / 1024 / 1024
                total_mb = total / 1024 / 1024
                speed_mb = speed / 1024 / 1024 if speed else 0
                eta_val = int(eta) if eta is not None else 0
                info_text = (
                    f"{downloaded_mb:.1f} MB de {total_mb:.1f} MB · "
                    f"{speed_mb:.2f} MB/s · ETA {eta_val}s"
                )
                self.app.root.after(0, lambda: self.update_progress(percent, info_text))
            else:
                downloaded_mb = downloaded / 1024 / 1024
                speed_mb = speed / 1024 / 1024 if speed else 0
                info_text = f"{downloaded_mb:.1f} MB · {speed_mb:.2f} MB/s"
                self.app.root.after(0, lambda: self.update_progress(0, info_text))

        elif d["status"] == "finished":
            self.app.root.after(
                0,
                lambda: self.update_progress(100, "Procesando con FFmpeg..."),
            )

    def run(self):
        try:
            ffmpeg_path = get_ffmpeg_path()
            if not os.path.exists(ffmpeg_path):
                self.app.root.after(0, lambda: self.set_status("Error FFmpeg", ACCENT_RED))
                self.app.root.after(
                    0,
                    lambda: self.set_info("No se encontró FFmpeg en la ruta empaquetada."),
                )
                self.app.on_task_finished(self, success=False)
                return

            ydl_opts_info = {
                "ffmpeg_location": ffmpeg_path,
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }
            title = "Video de Internet"
            try:
                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                    info = ydl.extract_info(self.url, download=False)
                    if "title" in info:
                        title = info["title"]
            except Exception:
                pass

            self.app.root.after(0, lambda: self.set_title(title))
            self.app.root.after(0, lambda: self.set_status("Descargando...", ACCENT_PRIMARY))

            sanitized_title = sanitize_filename(title)
            task_output_dir = os.path.join(self.output_dir, sanitized_title)
            os.makedirs(task_output_dir, exist_ok=True)

            ydl_opts = {
                "ffmpeg_location": ffmpeg_path,
                "outtmpl": os.path.join(task_output_dir, "%(title)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "progress_hooks": [self.progress_hook],
                "concurrent_fragment_downloads": 8,
                "http_chunk_size": 10485760,
            }

            if self.media_format == "mp3":
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": self.quality,
                    }],
                })
            elif self.media_format in ["mp4", "mkv"]:
                ydl_opts.update({
                    "format": build_video_format_selector(self.media_format, self.video_quality),
                    "merge_output_format": self.media_format,
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.app.root.after(0, lambda: self.set_status("Completado", ACCENT_GREEN))
            self.app.root.after(0, lambda: self.set_info(f"Guardado en: {task_output_dir}"))
            self.app.on_task_finished(self, success=True)

        except Exception as e:
            error_str = str(e)
            if len(error_str) > 100:
                error_str = error_str[:97] + "..."
            self.app.root.after(0, lambda: self.set_status("Error", ACCENT_RED))
            self.app.root.after(0, lambda: self.set_info(error_str))
            self.app.on_task_finished(self, success=False)

class DonLoaderApp:
    """Clase principal de la interfaz gráfica en Tkinter para DonLoader."""
    def __init__(self, root, url=None, media_format="mp3", output_dir=None,
                 quality="192", direct_mode=False, video_quality=None):
        self.root = root
        self.root.title("DonLoader")
        self.root.geometry("960x640")
        self.root.minsize(820, 560)
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(True, True)

        self.direct_mode = direct_mode
        self.initial_url = url
        self.media_format = media_format
        self.output_dir = output_dir or get_downloads_folder()
        self.quality = quality
        self.video_quality = video_quality

        self.tasks = []
        self._next_task_id = 0
        self._analysis_token = 0
        self.analysis_state = "idle"
        self.analyzed_url = ""
        self.available_video_heights = []

        self.root.attributes("-topmost", True)
        self.root.after(1000, lambda: self.root.attributes("-topmost", False))

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=0, minsize=340)
        self.root.grid_columnconfigure(1, weight=1)

        # Encabezado compacto: identidad y estado del motor.
        self.header_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(20, 14))
        self.header_frame.grid_columnconfigure(1, weight=1)

        logo = tk.Label(
            self.header_frame,
            text="↓",
            font=("Segoe UI", 17, "bold"),
            fg=BG_COLOR,
            bg=ACCENT_PRIMARY,
            width=2,
            pady=2,
        )
        logo.grid(row=0, column=0, rowspan=2, padx=(0, 10))

        tk.Label(
            self.header_frame,
            text="DonLoader",
            font=("Segoe UI", 16, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_COLOR,
            anchor="w",
        ).grid(row=0, column=1, sticky="w")
        tk.Label(
            self.header_frame,
            text="Descargas rápidas, simples y bajo control",
            font=("Segoe UI", 8),
            fg=TEXT_SECONDARY,
            bg=BG_COLOR,
            anchor="w",
        ).grid(row=1, column=1, sticky="w")

        status_pill = tk.Frame(self.header_frame, bg=SURFACE_COLOR, padx=10, pady=6)
        status_pill.grid(row=0, column=2, rowspan=2, sticky="e")
        self.engine_status_dot = tk.Label(
            status_pill, text="●", font=("Segoe UI", 8), fg=ACCENT_AMBER, bg=SURFACE_COLOR
        )
        self.engine_status_dot.pack(side="left", padx=(0, 5))
        self.update_status_label = tk.Label(
            status_pill,
            text="Buscando motor...",
            font=("Segoe UI", 8, "bold"),
            fg=ACCENT_AMBER,
            bg=SURFACE_COLOR,
        )
        self.update_status_label.pack(side="left")

        # Área principal de dos paneles.
        self.content_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=24, pady=(0, 14))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=0, minsize=320)
        self.content_frame.grid_columnconfigure(1, weight=1)

        self.input_frame = tk.Frame(
            self.content_frame,
            bg=SURFACE_COLOR,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
        )
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        self.queue_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        self.queue_frame.grid(row=0, column=1, sticky="nsew")
        self.queue_frame.grid_rowconfigure(1, weight=1)
        self.queue_frame.grid_columnconfigure(0, weight=1)

        queue_header = tk.Frame(self.queue_frame, bg=BG_COLOR)
        queue_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        queue_header.grid_columnconfigure(0, weight=1)
        self.queue_count_label = tk.Label(
            queue_header,
            text="Cola de descargas · 0",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_COLOR,
            anchor="w",
        )
        self.queue_count_label.grid(row=0, column=0, sticky="w")
        self.clear_completed_btn = ModernButton(
            queue_header,
            text="Limpiar completadas",
            font=("Segoe UI", 8, "bold"),
            bg=BG_COLOR,
            hover_bg=SURFACE_ELEVATED,
            fg=TEXT_SECONDARY,
            command=self.clear_completed,
            state=tk.DISABLED,
        )
        self.clear_completed_btn.grid(row=0, column=1, sticky="e")

        self.scroll_frame = ScrollableFrame(self.queue_frame, bg=BG_COLOR)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.empty_queue_frame = tk.Frame(self.scroll_frame.scrollable_frame, bg=SURFACE_COLOR,
                                          highlightthickness=1, highlightbackground=BORDER_COLOR)
        tk.Label(
            self.empty_queue_frame,
            text="↓",
            font=("Segoe UI", 24, "bold"),
            fg=ACCENT_PRIMARY,
            bg=SURFACE_COLOR,
        ).pack(pady=(32, 4))
        tk.Label(
            self.empty_queue_frame,
            text="Sin descargas todavía",
            font=("Segoe UI", 11, "bold"),
            fg=TEXT_PRIMARY,
            bg=SURFACE_COLOR,
        ).pack()
        tk.Label(
            self.empty_queue_frame,
            text="Pegá un enlace a la izquierda para empezar.",
            font=("Segoe UI", 8),
            fg=TEXT_SECONDARY,
            bg=SURFACE_COLOR,
        ).pack(pady=(4, 32))

        self.footer_frame = tk.Frame(self.root, bg=SURFACE_COLOR, height=28)
        self.footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.footer_frame.grid_propagate(False)
        self.version_label = tk.Label(
            self.footer_frame,
            text=f"DonLoader {APP_VERSION}",
            font=("Segoe UI", 8),
            fg=TEXT_SECONDARY,
            bg=SURFACE_COLOR,
        )
        self.version_label.pack(side="left", padx=18, pady=6)

        self.set_icon()
        self.show_input_view()
        self.update_queue_state()

        if self.direct_mode:
            self.input_frame.grid_remove()
            self.queue_frame.grid_configure(column=0, columnspan=2)

        threading.Thread(target=update_yt_dlp_worker, args=(self,), daemon=True).start()

        if self.direct_mode and self.initial_url:
            self.url_entry.insert(0, self.initial_url)
            self.on_start_click()

    def set_icon(self):
        """Establece el icono de la ventana y de la barra de tareas en Windows."""
        if sys.platform == 'win32':
            try:
                import ctypes
                myappid = 'nico.donloader.portable.1.1'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass
                
            try:
                if getattr(sys, 'frozen', False):
                    base_path = sys._MEIPASS
                else:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                
                icon_path = os.path.join(base_path, "icon.ico")
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            except Exception:
                pass

    def set_update_status(self, message):
        """Actualiza de forma segura el estado del motor desde hilos secundarios."""
        def update_label():
            if message in ("Al día", "Sin actualizaciones"):
                color = ACCENT_GREEN
            elif "Error" in message:
                color = ACCENT_RED
            elif "Actual" in message or "Buscando" in message:
                color = ACCENT_AMBER
            else:
                color = TEXT_SECONDARY
            self.update_status_label.config(text=message, fg=color)
            self.engine_status_dot.config(fg=color)

        self.root.after(0, update_label)

    def show_update_dialog(self, version, data, updates_dir, version_file):
        """Muestra una modal de actualización, descarga la actualización y reinicia la app."""
        self.root.after(0, lambda: self._create_update_dialog(version, data, updates_dir, version_file))

    def _create_update_dialog(self, version, data, updates_dir, version_file):
        dialog = tk.Toplevel(self.root, bg=BG_COLOR)
        dialog.title("Actualización de DonLoader")
        dialog.geometry("380x160")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar respecto a root
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        dialog.geometry(f"+{root_x + 110}+{root_y + 150}")
        
        label_title = tk.Label(dialog, text="Actualización Crítica disponible", font=("Segoe UI", 12, "bold"), fg=ACCENT_BLUE, bg=BG_COLOR)
        label_title.pack(pady=(15, 5))
        
        label_desc = tk.Label(dialog, text=f"Descargando e instalando yt-dlp v{version}...", font=("Segoe UI", 9), fg=TEXT_PRIMARY, bg=BG_COLOR)
        label_desc.pack(pady=5)
        
        canvas = tk.Canvas(dialog, width=320, height=10, bg=SURFACE_COLOR, highlightthickness=0)
        canvas.pack(pady=10)
        progress_bar = canvas.create_rectangle(0, 0, 0, 10, fill=ACCENT_GREEN, width=0)
        
        def run_update_process():
            try:
                wheel_url = None
                for u in data['urls']:
                    if u.get('packagetype') == 'bdist_wheel':
                        wheel_url = u.get('url')
                        break
                if not wheel_url:
                    for u in data['urls']:
                        if u.get('url', '').endswith('.whl'):
                            wheel_url = u.get('url')
                            break
                            
                if not wheel_url:
                    dialog.destroy()
                    self.set_update_status("Error al actualizar")
                    return
                
                temp_zip_path = os.path.join(updates_dir, 'temp_update.zip')
                
                canvas.coords(progress_bar, 0, 0, 80, 10)
                dialog.update()
                
                req = urllib.request.Request(wheel_url, headers={'User-Agent': f'DonLoader/{APP_VERSION}'})
                with urllib.request.urlopen(req) as dl_response:
                    with open(temp_zip_path, 'wb') as out_file:
                        shutil.copyfileobj(dl_response, out_file)
                
                canvas.coords(progress_bar, 0, 0, 180, 10)
                label_desc.config(text="Instalando componentes...")
                dialog.update()
                
                temp_extract_dir = os.path.join(updates_dir, 'temp_extract')
                if os.path.exists(temp_extract_dir):
                    shutil.rmtree(temp_extract_dir, ignore_errors=True)
                os.makedirs(temp_extract_dir, exist_ok=True)
                
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    for file_info in zip_ref.infolist():
                        if file_info.filename.startswith('yt_dlp/'):
                            zip_ref.extract(file_info, temp_extract_dir)
                
                canvas.coords(progress_bar, 0, 0, 260, 10)
                dialog.update()
                
                target_yt_dlp_dir = os.path.join(updates_dir, 'yt_dlp')
                if os.path.exists(target_yt_dlp_dir):
                    shutil.rmtree(target_yt_dlp_dir, ignore_errors=True)
                    
                extracted_yt_dlp_dir = os.path.join(temp_extract_dir, 'yt_dlp')
                if os.path.exists(extracted_yt_dlp_dir):
                    shutil.move(extracted_yt_dlp_dir, target_yt_dlp_dir)
                    
                with open(version_file, 'w', encoding='utf-8') as f:
                    f.write(version)
                    
                if os.path.exists(temp_zip_path):
                    os.remove(temp_zip_path)
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
                
                canvas.coords(progress_bar, 0, 0, 320, 10)
                label_desc.config(text="¡Completado! Reiniciando DonLoader...", fg=ACCENT_GREEN)
                dialog.update()
                
                dialog.after(1500, self._perform_restart)
                
            except Exception as e:
                label_desc.config(text=f"Error al actualizar: {str(e)}", fg=ACCENT_RED)
                dialog.after(3000, dialog.destroy)
                self.set_update_status("Sin actualizaciones")
                
        threading.Thread(target=run_update_process, daemon=True).start()

    def _perform_restart(self):
        try:
            if getattr(sys, 'frozen', False):
                os.execv(sys.executable, sys.argv)
            else:
                os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception:
            sys.exit(0)

    def show_input_view(self):
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        form = tk.Frame(self.input_frame, bg=SURFACE_COLOR)
        form.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            form, text="Nueva descarga", font=("Segoe UI", 15, "bold"),
            fg=TEXT_PRIMARY, bg=SURFACE_COLOR, anchor="w"
        ).pack(anchor="w")
        tk.Label(
            form, text="Elegí el formato y ajustá la calidad antes de encolar.",
            font=("Segoe UI", 8), fg=TEXT_SECONDARY, bg=SURFACE_COLOR, anchor="w"
        ).pack(anchor="w", pady=(3, 20))

        tk.Label(
            form, text="ENLACE", font=("Segoe UI", 8, "bold"),
            fg=TEXT_SECONDARY, bg=SURFACE_COLOR, anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        url_row = tk.Frame(form, bg=SURFACE_COLOR)
        url_row.pack(fill="x")
        self.url_entry = tk.Entry(
            url_row,
            font=("Segoe UI", 10),
            bg=SURFACE_ELEVATED,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat",
            highlightthickness=1,
            highlightcolor=ACCENT_PRIMARY,
            highlightbackground=BORDER_COLOR,
        )
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=7)
        self.url_entry.bind("<KeyRelease>", lambda event: self.on_url_changed())

        self.paste_btn = ModernButton(
            url_row, text="Pegar", font=("Segoe UI", 8, "bold"),
            bg=SURFACE_ELEVATED, hover_bg=BORDER_COLOR, fg=TEXT_PRIMARY,
            command=self.paste_url,
        )
        self.paste_btn.pack(side="left", padx=(7, 0), ipady=4)
        self.analyze_btn = ModernButton(
            url_row, text="Analizar", font=("Segoe UI", 8, "bold"),
            bg=SURFACE_ELEVATED, hover_bg=BORDER_COLOR, fg=TEXT_PRIMARY,
            command=self.analyze_url,
        )
        self.analyze_btn.pack(side="left", padx=(7, 0), ipady=4)

        self.url_error_label = tk.Label(
            form, text="", font=("Segoe UI", 8), fg=ACCENT_RED,
            bg=SURFACE_COLOR, anchor="w", justify="left"
        )
        self.url_error_label.pack(fill="x", pady=(5, 0))

        tk.Label(
            form, text="FORMATO", font=("Segoe UI", 8, "bold"),
            fg=TEXT_SECONDARY, bg=SURFACE_COLOR, anchor="w"
        ).pack(anchor="w", pady=(20, 5))
        self.fmt_var = tk.StringVar(value=self.media_format)
        format_row = tk.Frame(form, bg=SURFACE_COLOR)
        format_row.pack(fill="x")
        self.format_buttons = {}
        for fmt in ("mp3", "mp4", "mkv"):
            button = ModernButton(
                format_row, text=fmt.upper(), font=("Segoe UI", 9, "bold"),
                bg=SURFACE_ELEVATED, hover_bg=BORDER_COLOR, fg=TEXT_PRIMARY,
                command=lambda selected=fmt: self.set_format(selected),
            )
            button.pack(side="left", fill="x", expand=True, padx=(0, 5))
            self.format_buttons[fmt] = button

        self.audio_quality_frame = tk.Frame(form, bg=SURFACE_COLOR)
        tk.Label(
            self.audio_quality_frame, text="CALIDAD DE AUDIO", font=("Segoe UI", 8, "bold"),
            fg=TEXT_SECONDARY, bg=SURFACE_COLOR, anchor="w"
        ).pack(anchor="w", pady=(18, 5))
        self.q_var = tk.StringVar(value=self.quality)
        self.q_menu = tk.OptionMenu(self.audio_quality_frame, self.q_var, "128", "192", "256", "320")
        self.q_menu.config(
            font=("Segoe UI", 9), bg=SURFACE_ELEVATED, fg=TEXT_PRIMARY,
            activebackground=BORDER_COLOR, activeforeground=TEXT_PRIMARY,
            relief="flat", highlightthickness=0, bd=0,
        )
        self.q_menu["menu"].config(
            bg=SURFACE_ELEVATED, fg=TEXT_PRIMARY,
            activebackground=ACCENT_PRIMARY, activeforeground=BG_COLOR,
        )
        self.q_menu.pack(anchor="w", fill="x")

        self.video_quality_frame = tk.Frame(form, bg=SURFACE_COLOR)
        tk.Label(
            self.video_quality_frame, text="CALIDAD DE VIDEO", font=("Segoe UI", 8, "bold"),
            fg=TEXT_SECONDARY, bg=SURFACE_COLOR, anchor="w"
        ).pack(anchor="w", pady=(18, 5))
        self.video_quality_var = tk.StringVar(value="")
        self.video_quality_menu = tk.OptionMenu(
            self.video_quality_frame, self.video_quality_var, "Analizá un enlace"
        )
        self.video_quality_menu.config(
            font=("Segoe UI", 9), bg=SURFACE_ELEVATED, fg=TEXT_PRIMARY,
            activebackground=BORDER_COLOR, activeforeground=TEXT_PRIMARY,
            relief="flat", highlightthickness=0, bd=0, state=tk.DISABLED,
        )
        self.video_quality_menu["menu"].config(
            bg=SURFACE_ELEVATED, fg=TEXT_PRIMARY,
            activebackground=ACCENT_PRIMARY, activeforeground=BG_COLOR,
        )
        self.video_quality_menu.pack(anchor="w", fill="x")
        self.video_quality_status = tk.Label(
            self.video_quality_frame, text="Pulsá Analizar para consultar las resoluciones.",
            font=("Segoe UI", 8), fg=TEXT_SECONDARY, bg=SURFACE_COLOR, anchor="w"
        )
        self.video_quality_status.pack(fill="x", pady=(5, 0))

        folder_label = tk.Label(
            form, text="CARPETA DE DESTINO", font=("Segoe UI", 8, "bold"),
            fg=TEXT_SECONDARY, bg=SURFACE_COLOR, anchor="w"
        )
        folder_label.pack(anchor="w", pady=(20, 5))
        folder_row = tk.Frame(form, bg=SURFACE_COLOR)
        folder_row.pack(fill="x")
        self.folder_entry = tk.Entry(
            folder_row, font=("Segoe UI", 8), bg=SURFACE_ELEVATED,
            fg=TEXT_SECONDARY, relief="flat", highlightthickness=1,
            highlightbackground=BORDER_COLOR, highlightcolor=BORDER_COLOR,
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.folder_entry.insert(0, self.output_dir)
        self.folder_entry.config(state="readonly")
        ModernButton(
            folder_row, text="Cambiar", font=("Segoe UI", 8, "bold"),
            bg=SURFACE_ELEVATED, hover_bg=BORDER_COLOR, fg=TEXT_PRIMARY,
            command=self.browse_folder,
        ).pack(side="left", padx=(7, 0), ipady=4)

        self.download_btn = ModernButton(
            form, text="Añadir a la cola", font=("Segoe UI", 10, "bold"),
            bg=ACCENT_PRIMARY, hover_bg="#FF8477", fg=BG_COLOR,
            command=self.on_start_click,
        )
        self.download_btn.pack(fill="x", side="bottom", ipady=8, pady=(20, 0))

        self.set_format(self.media_format)

    def paste_url(self):
        try:
            clipboard_text = self.root.clipboard_get().strip()
        except tk.TclError:
            clipboard_text = ""
        if clipboard_text:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text)
            self.on_url_changed()
        self.url_entry.focus_set()

    def on_url_changed(self):
        self._invalidate_video_analysis()
        self.url_error_label.config(text="")
        self._update_control_state()

    def set_format(self, media_format):
        if media_format not in ("mp3", "mp4", "mkv"):
            return
        self.fmt_var.set(media_format)
        for fmt, button in self.format_buttons.items():
            selected = fmt == media_format
            button.config(
                bg=ACCENT_PRIMARY if selected else SURFACE_ELEVATED,
                fg=BG_COLOR if selected else TEXT_PRIMARY,
            )
            button.normal_bg = ACCENT_PRIMARY if selected else SURFACE_ELEVATED

        if media_format == "mp3":
            self.video_quality_frame.pack_forget()
            self.audio_quality_frame.pack(fill="x")
            self._invalidate_video_analysis()
        else:
            self.audio_quality_frame.pack_forget()
            self.video_quality_frame.pack(fill="x")
            if self.analyzed_url != self.url_entry.get().strip():
                self._invalidate_video_analysis()
        self._update_control_state()

    def toggle_quality_menu(self):
        """Compatibilidad con el nombre utilizado por versiones anteriores."""
        self.set_format(self.fmt_var.get())

    def _invalidate_video_analysis(self):
        self._analysis_token += 1
        self.analysis_state = "idle"
        self.analyzed_url = ""
        self.available_video_heights = []
        if not hasattr(self, "video_quality_var"):
            return
        self.video_quality_var.set("")
        menu = self.video_quality_menu["menu"]
        menu.delete(0, "end")
        menu.add_command(label="Analizá un enlace", command=lambda: None)
        self.video_quality_status.config(text="Pulsá Analizar para consultar las resoluciones.", fg=TEXT_SECONDARY)
        self.video_quality_menu.config(state=tk.DISABLED)

    def _update_control_state(self):
        if not hasattr(self, "url_entry"):
            return
        url = self.url_entry.get().strip()
        is_video = self.fmt_var.get() in ("mp4", "mkv")
        analyzed = self.analysis_state == "ready" and self.analyzed_url == url
        analyzing = self.analysis_state == "loading"

        if is_video:
            self.analyze_btn.config(
                state=tk.DISABLED if analyzing or not url else tk.NORMAL,
                text="Analizando..." if analyzing else "Analizar",
            )
            self.video_quality_menu.config(state=tk.NORMAL if analyzed else tk.DISABLED)
            can_download = bool(url) and (self.direct_mode or analyzed)
        else:
            self.analyze_btn.config(state=tk.DISABLED, text="Solo video")
            can_download = bool(url)

        self.download_btn.config(state=tk.NORMAL if can_download else tk.DISABLED)

    def analyze_url(self):
        url = self.url_entry.get().strip()
        if not url:
            self.url_error_label.config(text="Pegá una URL antes de analizar.")
            return
        if self.fmt_var.get() not in ("mp4", "mkv"):
            return

        self._analysis_token += 1
        token = self._analysis_token
        self.analysis_state = "loading"
        self.analyzed_url = ""
        self.available_video_heights = []
        self.url_error_label.config(text="")
        self.video_quality_status.config(text="Consultando resoluciones...", fg=ACCENT_AMBER)
        self._update_control_state()

        threading.Thread(
            target=self._analyze_url_worker,
            args=(url, token),
            daemon=True,
        ).start()

    def _analyze_url_worker(self, url, token):
        try:
            ydl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            heights = extract_video_heights(info)
            self.root.after(0, lambda: self._finish_video_analysis(url, token, heights))
        except Exception as error:
            message = str(error).strip() or "No se pudo consultar el enlace."
            if len(message) > 140:
                message = message[:137] + "..."
            self.root.after(0, lambda: self._fail_video_analysis(url, token, message))

    def _finish_video_analysis(self, url, token, heights):
        if token != self._analysis_token or url != self.url_entry.get().strip():
            return

        self.analysis_state = "ready"
        self.analyzed_url = url
        self.available_video_heights = heights
        menu = self.video_quality_menu["menu"]
        menu.delete(0, "end")

        if heights:
            for height in heights:
                menu.add_command(
                    label=f"{height}p",
                    command=lambda value=str(height): self.video_quality_var.set(value),
                )
            self.video_quality_var.set(str(heights[0]))
            self.video_quality_status.config(
                text=f"{len(heights)} resoluciones disponibles.", fg=ACCENT_GREEN
            )
        else:
            menu.add_command(label="Mejor disponible", command=lambda: self.video_quality_var.set("best"))
            self.video_quality_var.set("best")
            self.video_quality_status.config(
                text="El sitio no informa resoluciones; se usará la mejor disponible.",
                fg=ACCENT_AMBER,
            )

        self.video_quality_menu.config(state=tk.NORMAL)
        self._update_control_state()

    def _fail_video_analysis(self, url, token, message):
        if token != self._analysis_token or url != self.url_entry.get().strip():
            return
        self.analysis_state = "error"
        self.analyzed_url = ""
        self.video_quality_status.config(text="No se pudieron consultar las resoluciones.", fg=ACCENT_RED)
        self.url_error_label.config(text=message)
        self._update_control_state()

    def _selected_video_quality(self):
        value = self.video_quality_var.get().strip()
        if not value or value == "best":
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def browse_folder(self):
        """Abre un diálogo interactivo para elegir la carpeta de destino."""
        selected = filedialog.askdirectory(initialdir=self.output_dir, title="Seleccionar Carpeta de Destino")
        if selected:
            self.output_dir = os.path.abspath(selected)
            self.folder_entry.config(state="normal")
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, self.output_dir)
            self.folder_entry.config(state="readonly")

    def on_start_click(self):
        """Valida e inicia el proceso de descarga, agregándolo a la cola."""
        url = self.url_entry.get().strip()
        if not url:
            self.url_error_label.config(text="Pegá una URL válida para continuar.")
            return

        media_format = self.fmt_var.get()
        if media_format in ("mp4", "mkv") and not self.direct_mode:
            if self.analysis_state != "ready" or self.analyzed_url != url:
                self.url_error_label.config(text="Analizá el enlace para elegir una calidad de video.")
                return

        task_id = self._next_task_id
        self._next_task_id += 1
        selected_video_quality = self.video_quality if self.direct_mode else self._selected_video_quality()
        task = DownloadTask(
            self,
            self.scroll_frame.scrollable_frame,
            task_id,
            url,
            media_format,
            self.q_var.get(),
            self.output_dir,
            video_quality=selected_video_quality if media_format in ("mp4", "mkv") else None,
        )
        self.tasks.append(task)
        self.url_entry.delete(0, tk.END)
        self._invalidate_video_analysis()
        self.url_error_label.config(text="")
        self.update_queue_state()
        self.process_queue()

    def update_queue_state(self):
        active_count = len(self.tasks)
        self.queue_count_label.config(text=f"Cola de descargas · {active_count}")
        has_completed = any(task.status == "Completado" for task in self.tasks)
        self.clear_completed_btn.config(state=tk.NORMAL if has_completed else tk.DISABLED)
        if self.tasks:
            self.empty_queue_frame.pack_forget()
        else:
            self.empty_queue_frame.pack(fill="x", padx=2, pady=2)

    def clear_completed(self):
        remaining = []
        for task in self.tasks:
            if task.status == "Completado":
                task.destroy()
            else:
                remaining.append(task)
        self.tasks = remaining
        self.update_queue_state()

    def process_queue(self):
        """Gestiona el inicio de las tareas respetando el límite de 3 concurrentes."""
        active_tasks = [t for t in self.tasks if t.status in ["Analizando...", "Descargando..."]]
        if len(active_tasks) < 3:
            queued_tasks = [t for t in self.tasks if t.status == "En cola"]
            if queued_tasks:
                queued_tasks[0].start()
                self.root.after(100, self.process_queue)

    def on_task_finished(self, task, success):
        """Callback llamado al terminar una descarga para procesar el resto de la cola."""
        self.root.after(0, self.update_queue_state)
        if self.direct_mode:
            active = [t for t in self.tasks if t.status in ["En cola", "Analizando...", "Descargando..."]]
            if not active:
                self.root.after(1500, self.root.destroy)
        else:
            self.root.after(100, self.process_queue)

def cli_progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        speed = d.get('speed')
        eta = d.get('eta')
        
        if total:
            percent = (downloaded / total) * 100
            bar_len = 30
            filled = int(round(bar_len * downloaded / float(total)))
            bar = '█' * filled + '░' * (bar_len - filled)
            
            speed_str = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "-- MB/s"
            eta_str = f"{int(eta)}s" if eta is not None else "--s"
            sys.stdout.write(f"\rProgreso: |{bar}| {percent:.1f}% | Velocidad: {speed_str} | ETA: {eta_str}    ")
            sys.stdout.flush()
        else:
            sys.stdout.write(f"\rDescargando: {downloaded / 1024 / 1024:.2f} MB descargados...    ")
            sys.stdout.flush()
    elif d['status'] == 'finished':
        sys.stdout.write("\nDescarga completada. Procesando archivos con FFmpeg...\n")
        sys.stdout.flush()

def run_cli_download(url, media_format, output_dir, quality, video_quality=None):
    """Ejecuta la descarga directamente por consola (CLI)."""
    optimize_network()
    ffmpeg_path = get_ffmpeg_path()
    if not os.path.exists(ffmpeg_path):
        print(f"Error: FFmpeg no se encontró en {ffmpeg_path}.")
        sys.exit(1)
        
    # Obtener el título y crear una subcarpeta para el archivo
    ydl_opts_info = {
        'ffmpeg_location': ffmpeg_path,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    title = "Video de Internet"
    try:
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'title' in info:
                title = info['title']
    except Exception:
        pass
        
    sanitized_title = sanitize_filename(title)
    task_output_dir = os.path.join(output_dir, sanitized_title)
    os.makedirs(task_output_dir, exist_ok=True)
    
    ydl_opts = {
        'ffmpeg_location': ffmpeg_path,
        'outtmpl': os.path.join(task_output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [cli_progress_hook],
        'concurrent_fragment_downloads': 8,
        'http_chunk_size': 10485760,
    }
    
    if media_format == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
        })
    elif media_format in ['mp4', 'mkv']:
        ydl_opts.update({
            'format': build_video_format_selector(media_format, video_quality),
            'merge_output_format': media_format,
        })
        
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Analizando URL: {url}...")
            ydl.download([url])
        print(f"¡Descarga e integración completadas exitosamente en: {task_output_dir}!")
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
        sys.exit(1)

def build_argument_parser():
    parser = argparse.ArgumentParser(description="DonLoader - Descargador Multimedia Optimizado y Portable")
    parser.add_argument("-u", "--url", default=None, help="URL del video/audio a descargar")
    parser.add_argument("-f", "--format", choices=["mp3", "mp4", "mkv"], default="mp3", help="Formato de salida")
    parser.add_argument("-o", "--output", default=None, help="Carpeta de destino")
    parser.add_argument("-q", "--quality", default="192", choices=["128", "192", "256", "320"], help="Calidad de audio para MP3")
    parser.add_argument(
        "--video-quality",
        type=positive_int,
        default=None,
        help="Altura máxima del video en píxeles (ej. 720)",
    )
    parser.add_argument("--no-gui", action="store_true", help="Usar solo la interfaz por línea de comandos")
    return parser


def main():
    parser = build_argument_parser()
    
    args = parser.parse_args()
    
    if args.no_gui:
        if not args.url:
            print("Error: Se requiere una URL (parámetro -u) cuando se ejecuta con --no-gui.")
            sys.exit(1)
        run_cli_download(
            args.url,
            args.format,
            args.output or get_downloads_folder(),
            args.quality,
            args.video_quality,
        )
    else:
        # Optimizar red antes de iniciar
        optimize_network()
        
        # Inicializar Tkinter
        root = tk.Tk()
        direct_mode = (args.url is not None)
        app = DonLoaderApp(
            root,
            url=args.url,
            media_format=args.format,
            output_dir=args.output,
            quality=args.quality,
            direct_mode=direct_mode,
            video_quality=args.video_quality,
        )
        root.mainloop()

if __name__ == "__main__":
    main()
