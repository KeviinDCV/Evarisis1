# -*- coding: utf-8 -*-
"""Genera la plantilla de config.ini para las PC CLIENTE de la LAN.

POR QUE EXISTE (V6.9.93)
------------------------
Hasta ahora el config que se copiaba a dist/ era el del SERVIDOR de desarrollo:
host=127.0.0.1, usuario=root, password vacio. Un cliente que ejecutara el .exe
tal cual intentaba conectarse a SU PROPIA maquina y fallaba en silencio, hasta
que alguien editaba el fichero a mano en cada PC.

Este script parte del config.ini real —para no desincronizarse de su
estructura— y cambia SOLO lo que distingue a un cliente:

  · host            -> la PC servidor, no 127.0.0.1
  · usuario/password-> la cuenta de minimo privilegio, no root
  · usar_modelo_relacional = false
        El modelo relacional resincroniza haciendo TRUNCATE de cuatro tablas.
        Con dos usuarios a la vez, uno puede quedarse leyendo tablas vacias sin
        ningun error. Que resincronice SOLO el servidor.
  · la IA apunta al SERVIDOR, no a la propia maquina
        El esquema es "una PC lo sirve todo": MySQL y LM Studio corren los dos
        en el servidor y los clientes los usan por la LAN. Si el base_url
        quedara en 127.0.0.1, cada cliente buscaria un LM Studio que no tiene:
        ~2 s perdidos por llamada, ~3 min extra por PDF de 50 casos, en
        silencio. Los interruptores quedan ESCRITOS, no implicitos.

Las contrasenas NO se escriben aqui: quedan como marcador para que las ponga
quien administra el servidor.

    python build_tools\\generar_config_cliente.py
"""
import io
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVIDOR = "192.168.2.172"          # la PC que corre MySQL
MARCADOR = "<<<PON_AQUI_LA_CONTRASENA>>>"

CABECERA = f"""# =====================================================================
#  config.ini — PC CLIENTE (LAN del hospital)
#  Generado por build_tools/generar_config_cliente.py — V6.9.93
# =====================================================================
#
#  Este fichero va AL LADO de GestorOncologia.exe. Es el que manda: el que
#  viaja empaquetado dentro del .exe se ignora.
#
#  ANTES DE REPARTIRLO:
#    1. Pon la contrasena real donde dice {MARCADOR}
#    2. Elige el usuario segun el rol de esa PC:
#         huv_consulta -> solo mira, filtra y exporta
#         huv_captura  -> ademas importa PDFs y corrige casos
#       (se crean con docs/mysql_multiusuario_LAN.sql)
#    3. Comprueba que la ruta de Tesseract existe en esa PC.
#
#  NO subas este fichero al repositorio una vez tenga la contrasena.
# =====================================================================

"""


def main():
    origen = os.path.join(RAIZ, "config", "config.ini")
    if not os.path.isfile(origen):
        print("ERROR: no encuentro config/config.ini")
        return 1

    lineas = io.open(origen, encoding="utf-8").read().splitlines()
    salida, seccion = [], ""
    # lo que se sobreescribe, por seccion
    CAMBIOS = {
        "database": {
            "host": SERVIDOR,
            "usuario": "huv_consulta",
            "password": MARCADOR,
            "usar_modelo_relacional": "false",
        },
        "llm": {
            # V6.9.93 — el esquema es "una PC lo sirve todo": esa misma maquina
            # corre MySQL y LM Studio, y los clientes usan ambos por la LAN.
            # Por eso la IA va ENCENDIDA en el cliente y apuntando al servidor.
            # La guarda de core/red_local.py acepta esta IP por ser privada, y
            # sigue rechazando cualquier destino publico.
            "usar_ia_polaridad": "true",
            "usar_consenso_polaridad": "true",
            "provider": "lm_studio",
            "base_url": f"http://{SERVIDOR}:1234/v1",
        },
        "lmstudio": {
            "endpoint": f"http://{SERVIDOR}:1234/v1",
            "enabled": "true",
        },
    }
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
                salida.append(f"{clave} = {CAMBIOS[seccion][clave]}")
                continue
        salida.append(ln)

    # las claves que el config de origen no tenia se anaden igualmente
    texto = "\n".join(salida)
    for sec, kv in CAMBIOS.items():
        faltan = set(kv) - vistos[sec]
        if not faltan:
            continue
        marca = f"[{sec}]"
        i = texto.lower().find(marca)
        if i < 0:
            texto += f"\n\n{marca}\n" + "\n".join(f"{k} = {kv[k]}" for k in sorted(faltan))
            continue
        j = texto.find("\n", i) + 1
        extra = "".join(f"{k} = {kv[k]}\n" for k in sorted(faltan))
        texto = texto[:j] + extra + texto[j:]

    destino = os.path.join(RAIZ, "docs", "config.ini.cliente")
    io.open(destino, "w", encoding="utf-8").write(CABECERA + texto + "\n")
    print("plantilla de cliente -> docs/config.ini.cliente")
    print("   host = %s   usuario = huv_consulta   password = (marcador)" % SERVIDOR)
    print("   usar_modelo_relacional = false   ·   IA -> http://%s:1234/v1" % SERVIDOR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
