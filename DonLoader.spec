# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Definir la ruta de los binarios locales
ffmpeg_bin = os.path.join('bin', 'ffmpeg.exe')
ffprobe_bin = os.path.join('bin', 'ffprobe.exe')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[
        (ffmpeg_bin, 'bin'),    # Copia ffmpeg.exe dentro del exe a la subcarpeta 'bin'
        (ffprobe_bin, 'bin')    # Copia ffprobe.exe dentro del exe a la subcarpeta 'bin'
    ],
    datas=[('icon.ico', '.')], # Empaqueta el archivo de icono para usarlo a nivel de ventana en ejecución
    hiddenimports=['yt_dlp'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DonLoader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # Sin consola detrás de la ventana de Tkinter
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,         # Fuerza la solicitud de privilegios de Administrador (UAC) en Windows
    icon='icon.ico',        # Icono personalizado para el ejecutable
)
