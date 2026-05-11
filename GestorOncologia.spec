# -*- mode: python ; coding: utf-8 -*-
# V6.9.1 - MySQL/MariaDB multi-usuario + segunda pasada deshabilitada
from PyInstaller.utils.hooks import collect_submodules

ttkbootstrap_modules = collect_submodules('ttkbootstrap')
matplotlib_modules = collect_submodules('matplotlib')
selenium_modules = collect_submodules('selenium')
numpy_modules = collect_submodules('numpy')

added_files = [
    ('imagenes', 'imagenes'),
    ('config', 'config'),
    ('core', 'core'),
    ('requirements.txt', '.'),
]

hiddenimports = [
    'numpy', 'pandas', 'tkinter', 'ttkbootstrap',
    'matplotlib.backends.backend_tkagg', 'seaborn',
    'pytesseract', 'fitz', 'PIL.Image',
    'selenium.webdriver', 'webdriver_manager.chrome',
    'openpyxl', 'dateutil', 'babel', 'holidays',
    'sqlite3', 'psutil', 'cryptography',
    # V6.9.0 - MySQL/MariaDB driver
    'pymysql', 'pymysql.cursors', 'pymysql.constants',
    'pymysql.constants.CLIENT', 'pymysql.constants.COMMAND',
    'pymysql.constants.FIELD_TYPE', 'pymysql.constants.SERVER_STATUS',
    'pymysql.protocol', 'pymysql.connections',
    # Modulos core del proyecto
    'core.calendario', 'core.database_manager',
    'core.db_adapter', 'core.diagnosticos_ia_db',
    'core.columnas_huv_ia', 'core.llm_client',
    'core.huv_web_automation', 'core.ocr_processing',
    'core.procesador_ihq', 'core.procesador_ihq_biomarcadores',
    'core.enhanced_export_system', 'core.enhanced_database_dashboard',
    'config.version_info',
] + ttkbootstrap_modules + matplotlib_modules + selenium_modules + numpy_modules

a = Analysis(
    ['ui.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GestorOncologia',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
