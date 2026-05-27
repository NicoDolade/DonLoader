import os
import sys
import threading
import argparse
import subprocess
import urllib.request
import json
import zipfile
import shutil
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
APP_VERSION = "v1.1.0"

# Paleta de colores Catppuccin Mocha
BG_COLOR = "#1e1e2e"          # Base
SURFACE_COLOR = "#313244"     # Surface0
BORDER_COLOR = "#45475a"      # Surface1
TEXT_PRIMARY = "#cdd6f4"      # Text
TEXT_SECONDARY = "#a6adc8"    # Subtext0
ACCENT_BLUE = "#89b4fa"       # Blue (Progreso / Botones primarios)
ACCENT_GREEN = "#a6e3a1"      # Green (Éxito)
ACCENT_RED = "#f38ba8"        # Red (Error)

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
    """Hilo secundario para buscar y descargar actualizaciones de yt-dlp."""
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
        app_instance.set_update_status("Buscando actus...")
        url = "https://pypi.org/pypi/yt-dlp/json"
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) DonLoader/1.1.0'}
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
            app_instance.set_update_status(f"Descargando yt-dlp v{latest_version_str}...")
            
            # Buscar el archivo .whl
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
                app_instance.set_update_status("Error: No compatible")
                return
                
            temp_zip_path = os.path.join(updates_dir, 'temp_update.zip')
            
            with urllib.request.urlopen(wheel_url, timeout=30) as dl_response:
                with open(temp_zip_path, 'wb') as out_file:
                    shutil.copyfileobj(dl_response, out_file)
                    
            app_instance.set_update_status("Instalando actualización...")
            temp_extract_dir = os.path.join(updates_dir, 'temp_extract')
            if os.path.exists(temp_extract_dir):
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
            os.makedirs(temp_extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename.startswith('yt_dlp/'):
                        zip_ref.extract(file_info, temp_extract_dir)
                        
            target_yt_dlp_dir = os.path.join(updates_dir, 'yt_dlp')
            if os.path.exists(target_yt_dlp_dir):
                shutil.rmtree(target_yt_dlp_dir, ignore_errors=True)
                
            extracted_yt_dlp_dir = os.path.join(temp_extract_dir, 'yt_dlp')
            if os.path.exists(extracted_yt_dlp_dir):
                shutil.move(extracted_yt_dlp_dir, target_yt_dlp_dir)
                
            with open(version_file, 'w', encoding='utf-8') as f:
                f.write(latest_version_str)
                
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
            shutil.rmtree(temp_extract_dir, ignore_errors=True)
            
            app_instance.set_update_status("Actualizado. Reiniciar app.")
        else:
            app_instance.set_update_status("yt-dlp al día")
            
    except Exception:
        app_instance.set_update_status("Error al actualizar")

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

class DownloaderApp:
    """Clase principal de la interfaz gráfica en Tkinter."""
    def __init__(self, root, url=None, media_format="mp3", output_dir=None, quality="192", direct_mode=False):
        self.root = root
        self.root.title("DonLoader")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.direct_mode = direct_mode
        self.url = url
        self.media_format = media_format
        self.output_dir = output_dir or get_downloads_folder()
        self.quality = quality
        
        # Atributos de ventana
        self.root.attributes("-topmost", True)
        self.root.after(1000, lambda: self.root.attributes("-topmost", False))
        
        # Variables de estado
        self.progress_percent = 0
        self.status_text = "Conectando..."
        self.speed_text = "Calculando..."
        self.video_title = "Analizando enlace..."
        self.is_finished = False
        self.error_msg = None
        self.download_thread = None
        
        # Marcos principales
        self.input_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.progress_frame = tk.Frame(self.root, bg=BG_COLOR)
        
        # Footer / Barra de estado inferior
        self.footer_frame = tk.Frame(self.root, bg="#11111b", height=30)
        self.footer_frame.pack(side="bottom", fill="x")
        self.footer_frame.pack_propagate(False)
        
        yt_dlp_version = getattr(yt_dlp, '__version__', 'n/a')
        self.version_label = tk.Label(self.footer_frame, text=f"DonLoader {APP_VERSION}  |  yt-dlp {yt_dlp_version}",
                                      font=("Segoe UI", 8), fg="#a6adc8", bg="#11111b")
        self.version_label.pack(side="left", padx=15, pady=5)
        
        self.update_status_label = tk.Label(self.footer_frame, text="Buscando actus...", font=("Segoe UI", 8),
                                            fg=ACCENT_BLUE, bg="#11111b")
        self.update_status_label.pack(side="right", padx=15, pady=5)
        
        # Configurar icono de la aplicación (barra de tareas y ventana)
        self.set_icon()
        
        # Iniciar hilo de búsqueda de actualizaciones de yt-dlp
        threading.Thread(target=update_yt_dlp_worker, args=(self,), daemon=True).start()
        
        if self.direct_mode:
            self.show_progress_view()
            self.start_download()
        else:
            self.show_input_view()

    def set_icon(self):
        """Establece el icono de la ventana y de la barra de tareas en Windows."""
        if sys.platform == 'win32':
            # Configurar AppUserModelID para que Windows muestre el icono en la barra de tareas
            try:
                import ctypes
                myappid = 'nico.donloader.portable.1.1'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass
                
            # Cargar el icono bitmap de la ventana
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

    def show_input_view(self):
        self.progress_frame.pack_forget()
        self.root.geometry("520x450")
        self.input_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Limpiar widgets antiguos
        for widget in self.input_frame.winfo_children():
            widget.destroy()
            
        # Título principal
        title_label = tk.Label(self.input_frame, text="DonLoader", font=("Segoe UI", 20, "bold"), fg=ACCENT_BLUE, bg=BG_COLOR)
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Campo de entrada de URL
        url_label = tk.Label(self.input_frame, text="URL del Video / Audio", font=("Segoe UI", 10, "bold"), fg=TEXT_PRIMARY, bg=BG_COLOR)
        url_label.pack(anchor="w", pady=(0, 5))
        
        self.url_entry = tk.Entry(self.input_frame, font=("Segoe UI", 11), bg=SURFACE_COLOR, fg=TEXT_PRIMARY,
                                  insertbackground=TEXT_PRIMARY, relief="flat", highlightthickness=1, 
                                  highlightcolor=ACCENT_BLUE, highlightbackground=BORDER_COLOR)
        self.url_entry.pack(fill="x", ipady=6, pady=(0, 15))
        if self.url:
            self.url_entry.insert(0, self.url)
            
        # Contenedor de Formato y Calidad
        fmt_q_frame = tk.Frame(self.input_frame, bg=BG_COLOR)
        fmt_q_frame.pack(fill="x", pady=(0, 15))
        
        # Columna de Formato
        fmt_frame = tk.Frame(fmt_q_frame, bg=BG_COLOR)
        fmt_frame.pack(side="left", fill="both", expand=True)
        
        fmt_label = tk.Label(fmt_frame, text="Formato de Salida", font=("Segoe UI", 10, "bold"), fg=TEXT_PRIMARY, bg=BG_COLOR)
        fmt_label.pack(anchor="w", pady=(0, 5))
        
        self.fmt_var = tk.StringVar(value=self.media_format)
        fmt_option_frame = tk.Frame(fmt_frame, bg=BG_COLOR)
        fmt_option_frame.pack(anchor="w")
        
        for fmt in ["mp3", "mp4", "mkv"]:
            rb = tk.Radiobutton(fmt_option_frame, text=fmt.upper(), variable=self.fmt_var, value=fmt,
                                 font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_PRIMARY, activebackground=BG_COLOR,
                                 activeforeground=ACCENT_BLUE, selectcolor=SURFACE_COLOR, command=self.toggle_quality_menu)
            rb.pack(side="left", padx=(0, 15))
            
        # Columna de Calidad
        self.q_frame = tk.Frame(fmt_q_frame, bg=BG_COLOR)
        self.q_frame.pack(side="right", fill="both", expand=True)
        
        self.q_label = tk.Label(self.q_frame, text="Calidad de Audio (kbps)", font=("Segoe UI", 10, "bold"), fg=TEXT_PRIMARY, bg=BG_COLOR)
        self.q_label.pack(anchor="w", pady=(0, 5))
        
        self.q_var = tk.StringVar(value=self.quality)
        self.q_menu = tk.OptionMenu(self.q_frame, self.q_var, "128", "192", "256", "320")
        self.q_menu.config(font=("Segoe UI", 10), bg=SURFACE_COLOR, fg=TEXT_PRIMARY, activebackground=BORDER_COLOR,
                           activeforeground=TEXT_PRIMARY, relief="flat", highlightthickness=0)
        self.q_menu["menu"].config(bg=SURFACE_COLOR, fg=TEXT_PRIMARY, activebackground=ACCENT_BLUE, activeforeground=BG_COLOR)
        self.q_menu.pack(anchor="w")
        
        self.toggle_quality_menu()
        
        # Campo de Carpeta de Destino
        folder_label = tk.Label(self.input_frame, text="Carpeta de Destino", font=("Segoe UI", 10, "bold"), fg=TEXT_PRIMARY, bg=BG_COLOR)
        folder_label.pack(anchor="w", pady=(0, 5))
        
        folder_search_frame = tk.Frame(self.input_frame, bg=BG_COLOR)
        folder_search_frame.pack(fill="x", pady=(0, 25))
        
        self.folder_entry = tk.Entry(folder_search_frame, font=("Segoe UI", 10), bg=SURFACE_COLOR, fg=TEXT_SECONDARY,
                                     relief="flat", highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=BORDER_COLOR)
        self.folder_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.folder_entry.insert(0, self.output_dir)
        self.folder_entry.config(state="readonly")
        
        browse_btn = ModernButton(folder_search_frame, text="Examinar...", font=("Segoe UI", 9, "bold"),
                                  bg=SURFACE_COLOR, hover_bg=BORDER_COLOR, fg=TEXT_PRIMARY, command=self.browse_folder)
        browse_btn.pack(side="right", padx=(10, 0), ipady=3)
        
        # Botón de Descarga
        self.download_btn = ModernButton(self.input_frame, text="Iniciar Descarga", font=("Segoe UI", 11, "bold"),
                                         bg=ACCENT_BLUE, hover_bg="#a6e3a1", fg="#11111b", command=self.on_start_click)
        self.download_btn.pack(fill="x", ipady=8)

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
        """Valida e inicia el proceso de descarga."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor, ingresa una URL válida.")
            return
        
        self.url = url
        self.media_format = self.fmt_var.get()
        self.quality = self.q_var.get()
        
        self.show_progress_view()
        self.start_download()

    def show_progress_view(self):
        """Muestra la vista de progreso de la descarga."""
        self.input_frame.pack_forget()
        self.root.geometry("480x240")
        self.progress_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Limpiar marcos previos
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
            
        self.title_label = tk.Label(self.progress_frame, text=self.video_title, font=("Segoe UI", 11, "bold"),
                                    fg=TEXT_PRIMARY, bg=BG_COLOR, anchor="w", justify="left")
        self.title_label.pack(fill="x", pady=(10, 5))
        
        # Barra de progreso moderna con Canvas
        self.canvas = tk.Canvas(self.progress_frame, width=430, height=16, bg=SURFACE_COLOR, highlightthickness=0)
        self.canvas.pack(pady=5)
        self.progress_rect = self.canvas.create_rectangle(0, 0, 0, 16, fill=ACCENT_BLUE, width=0)
        
        self.status_label = tk.Label(self.progress_frame, text=self.status_text, font=("Segoe UI", 9),
                                     fg=TEXT_SECONDARY, bg=BG_COLOR, anchor="w")
        self.status_label.pack(fill="x", pady=(2, 2))
        
        self.speed_label = tk.Label(self.progress_frame, text=self.speed_text, font=("Segoe UI", 9),
                                    fg=TEXT_SECONDARY, bg=BG_COLOR, anchor="w")
        self.speed_label.pack(fill="x", pady=(2, 10))
        
        self.control_frame = tk.Frame(self.progress_frame, bg=BG_COLOR)
        self.control_frame.pack(fill="x")
        
        # Resetear variables
        self.progress_percent = 0
        self.status_text = "Conectando..."
        self.speed_text = "Calculando velocidad..."
        self.video_title = "Analizando enlace..."
        self.is_finished = False
        self.error_msg = None

    def start_download(self):
        """Inicia el hilo de descarga en segundo plano."""
        self.download_thread = threading.Thread(target=self.run_download, daemon=True)
        self.download_thread.start()
        self.update_gui_loop()

    def progress_hook(self, d):
        """Hook de progreso para actualizar los datos en tiempo real."""
        if d['status'] == 'downloading':
            if 'info_dict' in d and 'title' in d['info_dict'] and self.video_title == "Analizando enlace...":
                self.video_title = d['info_dict']['title']
                
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            speed = d.get('speed')
            eta = d.get('eta')
            
            if total:
                self.progress_percent = (downloaded / total) * 100
                downloaded_mb = downloaded / 1024 / 1024
                total_mb = total / 1024 / 1024
                self.status_text = f"Descargando: {downloaded_mb:.1f} MB de {total_mb:.1f} MB ({self.progress_percent:.1f}%)"
                
                speed_mb = speed / 1024 / 1024 if speed else 0
                eta_val = int(eta) if eta is not None else 0
                self.speed_text = f"Velocidad: {speed_mb:.2f} MB/s | ETA: {eta_val}s"
            else:
                downloaded_mb = downloaded / 1024 / 1024
                self.status_text = f"Descargado: {downloaded_mb:.1f} MB (Tamaño desconocido)"
                self.speed_text = f"Velocidad: {speed / 1024 / 1024:.2f} MB/s" if speed else "Velocidad: -- MB/s"
                
        elif d['status'] == 'finished':
            self.progress_percent = 100
            self.status_text = "Descarga completa con éxito."
            self.speed_text = "Procesando / Convirtiendo audio o video con FFmpeg..."

    def run_download(self):
        """Método de ejecución de descarga ejecutado en un hilo secundario."""
        ffmpeg_path = get_ffmpeg_path()
        if not os.path.exists(ffmpeg_path):
            self.error_msg = f"Error: No se encontró FFmpeg en la ruta empaquetada."
            return
            
        os.makedirs(self.output_dir, exist_ok=True)
        
        ydl_opts = {
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook],
            
            # --- OPTIMIZACIONES MULTI-HILO ---
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
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                if 'title' in info:
                    self.video_title = info['title']
                ydl.download([self.url])
            self.is_finished = True
        except Exception as e:
            self.error_msg = str(e)

    def update_gui_loop(self):
        """Bucle principal de actualización de la interfaz gráfica."""
        if self.error_msg:
            self.title_label.config(text="Error de descarga", fg=ACCENT_RED)
            self.status_label.config(text=self.error_msg, fg=ACCENT_RED)
            self.speed_label.config(text="El proceso ha fallado.")
            self.show_error_controls()
            return
            
        display_title = self.video_title
        if len(display_title) > 42:
            display_title = display_title[:39] + "..."
        self.title_label.config(text=display_title)
        
        self.status_label.config(text=self.status_text)
        self.speed_label.config(text=self.speed_text)
        
        canvas_width = 430
        target_width = int((self.progress_percent / 100.0) * canvas_width)
        self.canvas.coords(self.progress_rect, 0, 0, target_width, 16)
        
        if self.is_finished:
            self.status_label.config(text="¡Proceso finalizado con éxito!", fg=ACCENT_GREEN)
            self.speed_label.config(text="Guardado en: " + self.output_dir)
            
            if self.direct_mode:
                self.root.after(1500, self.root.destroy)
            else:
                self.show_success_controls()
        else:
            self.root.after(100, self.update_gui_loop)

    def show_success_controls(self):
        """Muestra los controles cuando la descarga se completa con éxito."""
        for w in self.control_frame.winfo_children():
            w.destroy()
        
        self.root.geometry("480x260")
        
        another_btn = ModernButton(self.control_frame, text="Descargar Otro", font=("Segoe UI", 9, "bold"),
                                   bg=ACCENT_BLUE, hover_bg="#a6e3a1", fg="#11111b", command=self.reset_to_input)
        another_btn.pack(side="right", padx=5)
        
        close_btn = ModernButton(self.control_frame, text="Cerrar", font=("Segoe UI", 9, "bold"),
                                 bg=SURFACE_COLOR, hover_bg=BORDER_COLOR, fg=TEXT_PRIMARY, command=self.root.destroy)
        close_btn.pack(side="right", padx=5)

    def show_error_controls(self):
        """Muestra los controles de reintento en caso de error."""
        for w in self.control_frame.winfo_children():
            w.destroy()
            
        self.root.geometry("480x260")
        
        back_btn = ModernButton(self.control_frame, text="Volver a Intentar", font=("Segoe UI", 9, "bold"),
                                bg=ACCENT_RED, hover_bg=BORDER_COLOR, fg=TEXT_PRIMARY, command=self.reset_to_input)
        back_btn.pack(side="right", padx=5)
        
        close_btn = ModernButton(self.control_frame, text="Cerrar", font=("Segoe UI", 9, "bold"),
                                 bg=SURFACE_COLOR, hover_bg=BORDER_COLOR, fg=TEXT_PRIMARY, command=self.root.destroy)
        close_btn.pack(side="right", padx=5)

    def reset_to_input(self):
        """Retorna al panel de ingreso de URL."""
        self.show_input_view()

# Hook para la consola en modo sin interfaz (CLI)
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
        
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'ffmpeg_location': ffmpeg_path,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
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
        print("¡Descarga e integración de FFmpeg completada exitosamente!")
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
        app = DownloaderApp(root, url=args.url, media_format=args.format, 
                            output_dir=args.output, quality=args.quality, direct_mode=direct_mode)
        root.mainloop()

if __name__ == "__main__":
    main()
