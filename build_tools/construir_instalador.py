# -*- coding: utf-8 -*-
"""Construye el instalador de Windows de ONCONOVA.

    python build_tools\\construir_instalador.py

QUE HACE
--------
 1. Lee build_tools\\despliegue.ini (la IP del servidor y las credenciales).
    Si no existe, lo crea a partir del .ejemplo y se PARA, para que nadie
    construya un instalador con una contrasena de mentira sin enterarse.
 2. Genera el config.ini que ira DENTRO del instalador, ya relleno: servidor,
    usuario, contrasena y endpoint de LM Studio. Eso es lo que evita que haya
    que editar nada en la PC de destino.
 3. Llama a Inno Setup (ISCC.exe) para empaquetarlo todo.

RESULTADO: dist_instalador\\ONCONOVA_<version>_<rol>_setup.exe

QUE NO HACE
-----------
No firma el instalador. Sin certificado Authenticode, Windows seguira
avisando con SmartScreen en cada PC nueva. Eso hay que comprarlo.
"""
import configparser
import io
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

BUILD = os.path.join(RAIZ, "build_tools")
SALIDA = os.path.join(RAIZ, "dist_instalador")
DESPLIEGUE = os.path.join(BUILD, "despliegue.ini")
EJEMPLO = os.path.join(BUILD, "despliegue.ini.ejemplo")

ISCC_POSIBLES = [
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
]


def encontrar_iscc():
    for p in ISCC_POSIBLES:
        if os.path.isfile(p):
            return p
    return None


def leer_despliegue():
    if not os.path.isfile(DESPLIEGUE):
        shutil.copyfile(EJEMPLO, DESPLIEGUE)
        print("=" * 70)
        print("Se ha creado build_tools\\despliegue.ini a partir del ejemplo.")
        print("ABRELO, pon la contrasena real y vuelve a ejecutar este script.")
        print("=" * 70)
        return None
    cfg = configparser.ConfigParser(inline_comment_prefixes=("#", ";"))
    cfg.read(DESPLIEGUE, encoding="utf-8")
    pwd = cfg.get("base_datos", "password", fallback="").strip()
    if not pwd or "PON_AQUI" in pwd:
        print("ERROR: la contrasena de build_tools\\despliegue.ini sigue sin rellenar.")
        print("       No se construye un instalador con una credencial de mentira.")
        return None
    return cfg


def generar_config(cfg):
    """El config.ini que se instalara en la PC cliente, ya relleno."""
    origen = os.path.join(RAIZ, "config", "config.ini")
    ip = cfg.get("servidor", "ip").strip()
    usuario = cfg.get("base_datos", "usuario").strip()
    pwd = cfg.get("base_datos", "password").strip()
    bd = cfg.get("base_datos", "base_datos", fallback="huv_oncologia").strip()
    puerto = cfg.get("base_datos", "puerto", fallback="3306").strip()
    ia = cfg.getboolean("ia", "activa", fallback=True)
    puerto_ia = cfg.get("ia", "puerto", fallback="1234").strip()

    CAMBIOS = {
        "database": {
            "tipo": "mysql", "host": ip, "puerto": puerto, "usuario": usuario,
            "password": pwd, "base_datos": bd,
            # que resincronice el modelo relacional SOLO el servidor: con dos
            # clientes, el TRUNCATE de la resincronizacion puede dejar a uno
            # leyendo tablas vacias sin ningun error
            "usar_modelo_relacional": "false",
        },
        "llm": {
            "provider": "lm_studio",
            "base_url": "http://%s:%s/v1" % (ip, puerto_ia),
            "usar_ia_polaridad": "true" if ia else "false",
            "usar_consenso_polaridad": "true" if ia else "false",
        },
        "lmstudio": {
            "endpoint": "http://%s:%s/v1" % (ip, puerto_ia),
            "enabled": "true" if ia else "false",
        },
    }

    lineas = io.open(origen, encoding="utf-8").read().splitlines()
    salida, seccion = [], ""
    vistos = {s: set() for s in CAMBIOS}
    for ln in lineas:
        s = ln.strip()
        if s.startswith("[") and s.endswith("]"):
            seccion = s[1:-1].strip().lower()
            salida.append(ln)
            continue
        if seccion in CAMBIOS and "=" in s and not s.startswith(("#", ";")):
            clave = s.split("=", 1)[0].strip().lower()
            if clave in CAMBIOS[seccion]:
                vistos[seccion].add(clave)
                salida.append("%s = %s" % (clave, CAMBIOS[seccion][clave]))
                continue
        salida.append(ln)

    texto = "\n".join(salida)
    for sec, kv in CAMBIOS.items():
        faltan = set(kv) - vistos[sec]
        if not faltan:
            continue
        i = texto.lower().find("[%s]" % sec)
        extra = "".join("%s = %s\n" % (k, kv[k]) for k in sorted(faltan))
        if i < 0:
            texto += "\n\n[%s]\n%s" % (sec, extra)
        else:
            j = texto.find("\n", i) + 1
            texto = texto[:j] + extra + texto[j:]

    cabecera = (
        "# =====================================================================\n"
        "#  config.ini — escrito por el INSTALADOR de ONCONOVA\n"
        "#  Servidor: %s   ·   Usuario: %s\n"
        "# =====================================================================\n"
        "#  No hace falta tocar nada: ya viene configurado.\n"
        "#  Si la IP del servidor cambiara, es la unica linea que habria que\n"
        "#  corregir aqui (host, en la seccion [database]).\n"
        "# =====================================================================\n\n"
        % (ip, usuario)
    )
    os.makedirs(SALIDA, exist_ok=True)
    destino = os.path.join(SALIDA, "config_generado.ini")
    io.open(destino, "w", encoding="utf-8").write(cabecera + texto + "\n")
    return destino, ip, usuario, puerto


def main():
    cfg = leer_despliegue()
    if cfg is None:
        return 1

    exe = os.path.join(RAIZ, "dist", "GestorOncologia.exe")
    if not os.path.isfile(exe):
        print("ERROR: falta dist\\GestorOncologia.exe — compila primero:")
        print("       venv0\\Scripts\\python.exe -m PyInstaller --clean --noconfirm GestorOncologia.spec")
        return 1

    iscc = encontrar_iscc()
    if not iscc:
        print("ERROR: no encuentro ISCC.exe (Inno Setup 6).")
        return 1

    from config.version_info import VERSION_INFO
    version = str(VERSION_INFO.get("version", "0.0.0")).strip()

    destino, ip, usuario, puerto = generar_config(cfg)
    rol = "captura" if "captura" in usuario else "consulta"
    print("config generado    : %s" % os.path.relpath(destino, RAIZ))
    print("servidor           : %s:%s   usuario: %s" % (ip, puerto, usuario))
    print("version            : %s   rol: %s" % (version, rol))
    print("compilando instalador con Inno Setup...")

    cmd = [
        iscc,
        "/DMiVersion=%s" % version,
        "/DMiRaiz=%s" % RAIZ,
        "/DMiSalida=%s" % SALIDA,
        "/DMiRol=%s" % rol,
        "/DMiServidorIp=%s" % ip,
        "/DMiPuertoBD=%s" % puerto,
        os.path.join(BUILD, "onconova.iss"),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR de Inno Setup:")
        print((r.stdout or "")[-2500:])
        print((r.stderr or "")[-1500:])
        return 1

    salida_exe = os.path.join(SALIDA, "ONCONOVA_%s_%s_setup.exe" % (version, rol))
    if os.path.isfile(salida_exe):
        mb = os.path.getsize(salida_exe) / (1024.0 * 1024.0)
        print()
        print("LISTO -> %s  (%.1f MB)" % (os.path.relpath(salida_exe, RAIZ), mb))
        print()
        print("Se instala en C:\\ONCONOVA, crea accesos directos y deja el")
        print("config ya relleno. El usuario solo tiene que ejecutarlo.")
        print("OJO: no esta firmado, asi que SmartScreen avisara en cada PC nueva.")
    else:
        print("Inno Setup termino sin error pero no encuentro el .exe de salida.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
