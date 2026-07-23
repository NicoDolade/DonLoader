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
from tkinter import messagebox, filedialog

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
APP_VERSION = "v1.2.6"

# Paleta de colores Catppuccin Mocha
BG_COLOR = "#1e1e2e"          # Base
SURFACE_COLOR = "#313244"     # Surface0
BORDER_COLOR = "#45475a"      # Surface1
TEXT_PRIMARY = "#cdd6f4"      # Text
TEXT_SECONDARY = "#a6adc8"    # Subtext0
ACCENT_BLUE = "#89b4fa"       # Blue (Progreso / Botones primarios)
ACCENT_GREEN = "#a6e3a1"      # Green (Éxito)
ACCENT_RED = "#f38ba8"        # Red (Error)

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
                self.hover_bg = "#b4befe"      # Lavender
            elif self.normal_bg == ACCENT_GREEN:
                self.hover_bg = "#85e07d"      # Green claro
            elif self.normal_bg == ACCENT_RED:
                self.hover_bg = "#f5c2e7"      # Pink
            elif self.normal_bg == SURFACE_COLOR:
                self.hover_bg = "#45475a"      # Surface1
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
    """Clase que representa una tarjeta de tarea de descarga individual en la interfaz."""
    def __init__(self, app_instance, container, task_id, url, media_format, quality, output_dir):
        self.app = app_instance
        self.container = container
        self.id = task_id
        self.url = url
        self.media_format = media_format
        self.quality = quality
        self.output_dir = output_dir
        
        self.status = "En cola"
        self.progress_percent = 0
        self.title = "Analizando enlace..."
        self.speed_text = ""
        self.download_thread = None
        
        # Estructura visual de la tarjeta
        self.frame = tk.Frame(self.container, bg=SURFACE_COLOR, bd=1, relief="solid")
        self.frame.config(highlightbackground=BORDER_COLOR, highlightcolor=BORDER_COLOR)
        self.frame.pack(fill="x", pady=5, ipady=4, padx=5)
        
        # Fila 1: Título y Estado
        self.header_frame = tk.Frame(self.frame, bg=SURFACE_COLOR)
        self.header_frame.pack(fill="x", padx=10, pady=(4, 2))
        
        self.title_label = tk.Label(self.header_frame, text=self.title, font=("Segoe UI", 9, "bold"),
                                    fg=TEXT_PRIMARY, bg=SURFACE_COLOR, anchor="w", justify="left")
        self.title_label.pack(side="left", fill="x", expand=True)
        
        self.status_label = tk.Label(self.header_frame, text=self.status, font=("Segoe UI", 9, "bold"),
                                     fg=TEXT_SECONDARY, bg=SURFACE_COLOR, anchor="e")
        self.status_label.pack(side="right", padx=5)
        
        # Fila 2: Barra de progreso (Canvas)
        self.canvas = tk.Canvas(self.frame, height=8, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="x", padx=10, pady=3)
        self.progress_rect = self.canvas.create_rectangle(0, 0, 0, 8, fill=ACCENT_BLUE, width=0)
        
        # Fila 3: Detalles e información
        self.info_label = tk.Label(self.frame, text="Esperando en cola...", font=("Segoe UI", 8),
                                   fg=TEXT_SECONDARY, bg=SURFACE_COLOR, anchor="w")
        self.info_label.pack(fill="x", padx=10, pady=(1, 4))
        
        self.canvas.bind('<Configure>', self._draw_progress)
        
    def _draw_progress(self, event=None):
        canvas_width = self.canvas.winfo_width()
        target_width = int((self.progress_percent / 100.0) * canvas_width)
        self.canvas.coords(self.progress_rect, 0, 0, target_width, 8)
        
    def set_status(self, status, color=TEXT_SECONDARY):
        self.status = status
        self.status_label.config(text=status, fg=color)
        
    def set_info(self, info_text):
        self.info_label.config(text=info_text)
        
    def set_title(self, title):
        self.title = title
        display_title = title
        if len(display_title) > 55:
            display_title = display_title[:52] + "..."
        self.title_label.config(text=display_title)
        
    def update_progress(self, percent, info_text):
        self.progress_percent = percent
        self._draw_progress()
        self.set_info(info_text)
        
    def start(self):
        """Arranca el hilo de ejecución para esta tarea de descarga."""
        self.set_status("Analizando...", ACCENT_BLUE)
        self.set_info("Analizando URL del video...")
        self.download_thread = threading.Thread(target=self.run, daemon=True)
        self.download_thread.start()
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed')
            eta = d.get('eta')
            
            if total:
                percent = (downloaded / total) * 100
                downloaded_mb = downloaded / 1024 / 1024
                total_mb = total / 1024 / 1024
                speed_mb = speed / 1024 / 1024 if speed else 0
                eta_val = int(eta) if eta is not None else 0
                
                info_text = f"Descargado: {downloaded_mb:.1f} MB de {total_mb:.1f} MB | Vel: {speed_mb:.2f} MB/s | ETA: {eta_val}s"
                self.app.root.after(0, lambda: self.update_progress(percent, info_text))
            else:
                downloaded_mb = downloaded / 1024 / 1024
                speed_mb = speed / 1024 / 1024 if speed else 0
                info_text = f"Descargado: {downloaded_mb:.1f} MB | Vel: {speed_mb:.2f} MB/s"
                self.app.root.after(0, lambda: self.update_progress(0, info_text))
                
        elif d['status'] == 'finished':
            self.app.root.after(0, lambda: self.update_progress(100, "Procesando / Convirtiendo audio o video con FFmpeg..."))
            
    def run(self):
        try:
            ffmpeg_path = get_ffmpeg_path()
            if not os.path.exists(ffmpeg_path):
                self.app.root.after(0, lambda: self.set_status("Error FFmpeg", ACCENT_RED))
                self.app.root.after(0, lambda: self.set_info("No se encontró FFmpeg en la ruta empaquetada."))
                self.app.on_task_finished(self, success=False)
                return
                
            # Obtener el título antes del inicio de la descarga
            ydl_opts_info = {
                'ffmpeg_location': ffmpeg_path,
                'quiet': True,
                'no_warnings': True,
            }
            title = "Video de Internet"
            try:
                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                    info = ydl.extract_info(self.url, download=False)
                    if 'title' in info:
                        title = info['title']
            except Exception:
                pass
                
            self.app.root.after(0, lambda: self.set_title(title))
            self.app.root.after(0, lambda: self.set_status("Descargando...", ACCENT_BLUE))
            
            # Crear subcarpeta con el título del video sanitizado
            sanitized_title = sanitize_filename(title)
            task_output_dir = os.path.join(self.output_dir, sanitized_title)
            os.makedirs(task_output_dir, exist_ok=True)
            
            ydl_opts = {
                'ffmpeg_location': ffmpeg_path,
                'outtmpl': os.path.join(task_output_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self.progress_hook],
                'concurrent_fragment_downloads': 8,
                'http_chunk_size': 10485760,
            }
            
            if self.media_format == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': self.quality,
                    }],
                })
            elif self.media_format in ['mp4', 'mkv']:
                ydl_opts.update({
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': self.media_format,
                })
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
                
            self.app.root.after(0, lambda: self.set_status("Completado", ACCENT_GREEN))
            self.app.root.after(0, lambda: self.set_info(f"Guardado en: {task_output_dir}"))
            self.app.on_task_finished(self, success=True)
            
        except Exception as e:
            error_str = str(e)
            if len(error_str) > 80:
                error_str = error_str[:77] + "..."
            self.app.root.after(0, lambda: self.set_status("Error", ACCENT_RED))
            self.app.root.after(0, lambda: self.set_info(error_str))
            self.app.on_task_finished(self, success=False)

class DonLoaderApp:
    """Clase principal de la interfaz gráfica en Tkinter para DonLoader."""
    def __init__(self, root, url=None, media_format="mp3", output_dir=None, quality="192", direct_mode=False):
        self.root = root
        self.root.title("DonLoader")
        self.root.geometry("600x550")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.direct_mode = direct_mode
        self.initial_url = url
        self.media_format = media_format
        self.output_dir = output_dir or get_downloads_folder()
        self.quality = quality
        
        # Mantener las descargas
        self.tasks = []
        
        # Atributos de ventana
        self.root.attributes("-topmost", True)
        self.root.after(1000, lambda: self.root.attributes("-topmost", False))
        
        # Marcos principales
        self.input_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.input_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        self.queue_label_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.queue_label_frame.pack(fill="x", padx=30)
        
        lbl = tk.Label(self.queue_label_frame, text="Cola de Descargas", font=("Segoe UI", 12, "bold"), fg=TEXT_PRIMARY, bg=BG_COLOR)
        lbl.pack(anchor="w", pady=(10, 5))
        
        # ScrollableFrame para tareas
        self.scroll_frame = ScrollableFrame(self.root, bg=BG_COLOR)
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        
        # Footer
        self.footer_frame = tk.Frame(self.root, bg="#11111b", height=30)
        self.footer_frame.pack(side="bottom", fill="x")
        self.footer_frame.pack_propagate(False)
        
        self.version_label = tk.Label(self.footer_frame, text=f"DonLoader {APP_VERSION}",
                                      font=("Segoe UI", 8), fg="#a6adc8", bg="#11111b")
        self.version_label.pack(side="left", padx=15, pady=5)
        
        self.update_status_label = tk.Label(self.footer_frame, text="Buscando...", font=("Segoe UI", 8),
                                            fg=ACCENT_BLUE, bg="#11111b")
        self.update_status_label.pack(side="right", padx=15, pady=5)
        
        # Configurar icono de la aplicación (barra de tareas y ventana)
        self.set_icon()
        
        # Cargar los campos de control
        self.show_input_view()
        
        # Iniciar hilo de búsqueda de actualizaciones de yt-dlp
        threading.Thread(target=update_yt_dlp_worker, args=(self,), daemon=True).start()
        
        # Si se pasó una URL por parámetro, iniciar descarga automáticamente
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
        """Actualiza de forma segura el texto de estado en el footer desde hilos secundarios."""
        self.root.after(0, lambda: self.update_status_label.config(text=message))

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
        # Limpiar widgets antiguos
        for widget in self.input_frame.winfo_children():
            widget.destroy()
            
        # Título principal
        title_label = tk.Label(self.input_frame, text="DonLoader", font=("Segoe UI", 18, "bold"), fg=ACCENT_BLUE, bg=BG_COLOR)
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Campo de entrada de URL
        url_label = tk.Label(self.input_frame, text="URL del Video / Audio", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_COLOR)
        url_label.pack(anchor="w", pady=(0, 3))
        
        self.url_entry = tk.Entry(self.input_frame, font=("Segoe UI", 10), bg=SURFACE_COLOR, fg=TEXT_PRIMARY,
                                  insertbackground=TEXT_PRIMARY, relief="flat", highlightthickness=1, 
                                  highlightcolor=ACCENT_BLUE, highlightbackground=BORDER_COLOR)
        self.url_entry.pack(fill="x", ipady=5, pady=(0, 10))
            
        # Contenedor de Formato y Calidad
        fmt_q_frame = tk.Frame(self.input_frame, bg=BG_COLOR)
        fmt_q_frame.pack(fill="x", pady=(0, 10))
        
        # Columna de Formato
        fmt_frame = tk.Frame(fmt_q_frame, bg=BG_COLOR)
        fmt_frame.pack(side="left", fill="both", expand=True)
        
        fmt_label = tk.Label(fmt_frame, text="Formato de Salida", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_COLOR)
        fmt_label.pack(anchor="w", pady=(0, 3))
        
        self.fmt_var = tk.StringVar(value=self.media_format)
        fmt_option_frame = tk.Frame(fmt_frame, bg=BG_COLOR)
        fmt_option_frame.pack(anchor="w")
        
        for fmt in ["mp3", "mp4", "mkv"]:
            rb = tk.Radiobutton(fmt_option_frame, text=fmt.upper(), variable=self.fmt_var, value=fmt,
                                 font=("Segoe UI", 9), bg=BG_COLOR, fg=TEXT_PRIMARY, activebackground=BG_COLOR,
                                 activeforeground=ACCENT_BLUE, selectcolor=SURFACE_COLOR, command=self.toggle_quality_menu)
            rb.pack(side="left", padx=(0, 12))
            
        # Columna de Calidad
        self.q_frame = tk.Frame(fmt_q_frame, bg=BG_COLOR)
        self.q_frame.pack(side="right", fill="both", expand=True)
        
        self.q_label = tk.Label(self.q_frame, text="Calidad de Audio (kbps)", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_COLOR)
        self.q_label.pack(anchor="w", pady=(0, 3))
        
        self.q_var = tk.StringVar(value=self.quality)
        self.q_menu = tk.OptionMenu(self.q_frame, self.q_var, "128", "192", "256", "320")
        self.q_menu.config(font=("Segoe UI", 9), bg=SURFACE_COLOR, fg=TEXT_PRIMARY, activebackground=BORDER_COLOR,
                           activeforeground=TEXT_PRIMARY, relief="flat", highlightthickness=0)
        self.q_menu["menu"].config(bg=SURFACE_COLOR, fg=TEXT_PRIMARY, activebackground=ACCENT_BLUE, activeforeground=BG_COLOR)
        self.q_menu.pack(anchor="w")
        
        self.toggle_quality_menu()
        
        # Campo de Carpeta de Destino
        folder_label = tk.Label(self.input_frame, text="Carpeta de Destino", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_COLOR)
        folder_label.pack(anchor="w", pady=(0, 3))
        
        folder_search_frame = tk.Frame(self.input_frame, bg=BG_COLOR)
        folder_search_frame.pack(fill="x", pady=(0, 15))
        
        self.folder_entry = tk.Entry(folder_search_frame, font=("Segoe UI", 9), bg=SURFACE_COLOR, fg=TEXT_SECONDARY,
                                     relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=BORDER_COLOR)
        self.folder_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.folder_entry.insert(0, self.output_dir)
        self.folder_entry.config(state="readonly")
        
        browse_btn = ModernButton(folder_search_frame, text="Examinar...", font=("Segoe UI", 8, "bold"),
                                  bg=SURFACE_COLOR, hover_bg=BORDER_COLOR, fg=TEXT_PRIMARY, command=self.browse_folder)
        browse_btn.pack(side="right", padx=(10, 0), ipady=2)
        
        # Botón de Descarga
        self.download_btn = ModernButton(self.input_frame, text="Añadir a la Cola", font=("Segoe UI", 10, "bold"),
                                          bg=ACCENT_BLUE, hover_bg="#b4befe", fg="#11111b", command=self.on_start_click)
        self.download_btn.pack(fill="x", ipady=6)

    def toggle_quality_menu(self):
        """Activa o desactiva la selección de calidad de audio según el formato."""
        if self.fmt_var.get() == "mp3":
            self.q_menu.config(state="normal")
            self.q_label.config(fg=TEXT_PRIMARY)
        else:
            self.q_menu.config(state="disabled")
            self.q_label.config(fg=TEXT_SECONDARY)

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
            messagebox.showerror("Error", "Por favor, ingresa una URL válida.")
            return
        
        media_format = self.fmt_var.get()
        quality = self.q_var.get()
        
        # Crear la tarea
        task_id = len(self.tasks)
        task = DownloadTask(self, self.scroll_frame.scrollable_frame, task_id, url, media_format, quality, self.output_dir)
        self.tasks.append(task)
        
        # Limpiar el campo de entrada
        self.url_entry.delete(0, tk.END)
        
        # Procesar cola
        self.process_queue()

    def process_queue(self):
        """Gestiona el inicio de las tareas respetando el límite de 3 concurrentes."""
        active_tasks = [t for t in self.tasks if t.status in ["Analizando...", "Descargando..."]]
        if len(active_tasks) < 3:
            queued_tasks = [t for t in self.tasks if t.status == "En cola"]
            if queued_tasks:
                task_to_start = queued_tasks[0]
                task_to_start.start()
                # Recursión en el siguiente ciclo del main loop
                self.root.after(100, self.process_queue)

    def on_task_finished(self, task, success):
        """Callback llamado al terminar una descarga para procesar el resto de la cola."""
        if self.direct_mode:
            # En modo directo, si es la única tarea, cerrar después de 1.5s
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

def run_cli_download(url, media_format, output_dir, quality):
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
            'format': 'bestvideo+bestaudio/best',
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

def main():
    parser = argparse.ArgumentParser(description="DonLoader - Descargador Multimedia Optimizado y Portable")
    parser.add_argument("-u", "--url", default=None, help="URL del video/audio a descargar")
    parser.add_argument("-f", "--format", choices=["mp3", "mp4", "mkv"], default="mp3", help="Formato de salida")
    parser.add_argument("-o", "--output", default=None, help="Carpeta de destino")
    parser.add_argument("-q", "--quality", default="192", choices=["128", "192", "256", "320"], help="Calidad de audio para MP3")
    parser.add_argument("--no-gui", action="store_true", help="Usar solo la interfaz por línea de comandos")
    
    args = parser.parse_args()
    
    if args.no_gui:
        if not args.url:
            print("Error: Se requiere una URL (parámetro -u) cuando se ejecuta con --no-gui.")
            sys.exit(1)
        run_cli_download(args.url, args.format, args.output or get_downloads_folder(), args.quality)
    else:
        # Optimizar red antes de iniciar
        optimize_network()
        
        # Inicializar Tkinter
        root = tk.Tk()
        direct_mode = (args.url is not None)
        app = DonLoaderApp(root, url=args.url, media_format=args.format, 
                             output_dir=args.output, quality=args.quality, direct_mode=direct_mode)
        root.mainloop()

if __name__ == "__main__":
    main()
