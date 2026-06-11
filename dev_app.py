#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONCONOVA - Launcher de DESARROLLO con auto-recarga.

Abre la app y la VIGILA: cuando detecta que cambió cualquier archivo .py de
`core/`, `ui.py` o `config/config.ini`, REINICIA la app automáticamente para que
tome los cambios. Así NO hay que cerrar y abrir a mano cada vez.

USO (en vez de `python ui.py`):
    python dev_app.py

- Para detener todo: cierra la ventana de la app (o Ctrl+C en esta consola).
- Espera ~2 s tras un cambio antes de reiniciar (debounce), para no reiniciar a
  mitad de un guardado de archivo.
- NO uses esto en producción real; es solo para desarrollo/ajustes.
"""
import os
import sys
import time
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(ROOT, "ui.py")

# Usar el Python del ENTORNO VIRTUAL del proyecto (tiene tksheet y demás
# dependencias). Aunque lances `python dev_app.py` con el Python global, la app
# arranca con el venv correcto.
_venv_win = os.path.join(ROOT, "venv0", "Scripts", "python.exe")
_venv_nix = os.path.join(ROOT, "venv0", "bin", "python")
if os.path.isfile(_venv_win):
    PYTHON = _venv_win
elif os.path.isfile(_venv_nix):
    PYTHON = _venv_nix
else:
    PYTHON = sys.executable

WATCH_FILES = [
    os.path.join(ROOT, "ui.py"),
    os.path.join(ROOT, "config", "config.ini"),
]
WATCH_DIRS = [os.path.join(ROOT, "core")]

DEBOUNCE_SEG = 2.0   # esperar tras un cambio antes de reiniciar
POLL_SEG = 1.5       # cada cuánto revisar cambios


def _snapshot():
    """Devuelve {ruta: mtime} de todos los archivos vigilados."""
    mt = {}
    for f in WATCH_FILES:
        try:
            mt[f] = os.path.getmtime(f)
        except OSError:
            pass
    for d in WATCH_DIRS:
        for root, _dirs, files in os.walk(d):
            # ignorar caches/backups
            if "__pycache__" in root or "backup" in root.lower():
                continue
            for fn in files:
                if fn.endswith(".py"):
                    p = os.path.join(root, fn)
                    try:
                        mt[p] = os.path.getmtime(p)
                    except OSError:
                        pass
    return mt


def _cambios(antes, ahora):
    return [p for p in ahora if antes.get(p) != ahora.get(p)] + \
           [p for p in antes if p not in ahora]


def main():
    print("=" * 64)
    print("  ONCONOVA - MODO DESARROLLO (auto-recarga)")
    print("  La app se REINICIA sola cuando cambias codigo .py de core/ o ui.py")
    print("  Para detener: cierra la app, o Ctrl+C aqui.")
    print("=" * 64)

    try:
        while True:
            proc = subprocess.Popen([PYTHON, APP], cwd=ROOT)
            base = _snapshot()
            reiniciar = False

            while True:
                time.sleep(POLL_SEG)

                if proc.poll() is not None:
                    # La app se cerro por su cuenta (el usuario la cerro) -> salir.
                    print("\n[dev] La app se cerro. Fin del modo desarrollo.")
                    return

                ahora = _snapshot()
                cambiados = _cambios(base, ahora)
                if cambiados:
                    rel = [os.path.relpath(p, ROOT) for p in cambiados][:6]
                    print(f"\n[dev] Cambios: {rel}")
                    # debounce: esperar a que terminen de guardarse los archivos
                    time.sleep(DEBOUNCE_SEG)
                    print("[dev] Reiniciando la app para aplicar los cambios...\n")
                    reiniciar = True
                    break

            if reiniciar:
                try:
                    proc.terminate()
                    proc.wait(timeout=8)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
                time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[dev] Detenido por el usuario (Ctrl+C).")
        try:
            proc.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    main()
