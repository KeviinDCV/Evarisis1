# -*- coding: utf-8 -*-
"""UN SOLO COMANDO: deja listo el instalador para PCs que SOLO CONSULTAN.

    python build_tools\\preparar_solo_visualizacion.py

Escenario: los demas equipos instalan y MIRAN los datos. No importan PDFs, no
analizan, no corrigen. Eso simplifica todo:

  · Solo hace falta UNA cuenta de MySQL, y de solo lectura (SELECT).
  · NO hace falta LM Studio en red, ni el puerto 1234, ni Tesseract: la IA y el
    OCR son cosa de la importacion, que estos equipos no hacen.
  · La contrasena se genera sola y se hornea en el instalador. Nadie tiene que
    inventarla, teclearla ni recordarla.

QUE HACE, EN ORDEN
------------------
 1. Genera una contrasena aleatoria fuerte.
 2. Crea el usuario `huv_consulta` en MySQL con permiso SELECT y solo desde la
    subred local.
 3. Anade la regla de firewall para el puerto 3306 (perfil Privada).
 4. Genera el config.ini del cliente, con la IA APAGADA.
 5. Construye el instalador.

Todo es reversible: al final imprime como deshacerlo.
"""
import configparser
import io
import os
import secrets
import string
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)

USUARIO = "huv_consulta"
BD = "huv_oncologia"
PUERTO = "3306"


def ip_lan():
    """La IP privada de esta maquina (la que veran los clientes)."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    finally:
        s.close()


def subred(ip):
    return ".".join(ip.split(".")[:3]) + ".%"


def clave_fuerte(n=24):
    # sin comillas ni barras: viajan por SQL y por un .ini
    alfabeto = string.ascii_letters + string.digits + "-_.+="
    return "".join(secrets.choice(alfabeto) for _ in range(n))


def paso(n, txt):
    print("\n[%d] %s" % (n, txt))


def main():
    ip = ip_lan()
    host_lan = subred(ip)
    print("=" * 70)
    print("  ONCONOVA — preparar equipos de SOLO CONSULTA")
    print("=" * 70)
    print("  servidor (esta PC): %s" % ip)
    print("  clientes desde    : %s" % host_lan)

    # ---------------------------------------------------------------
    paso(1, "Generando contrasena…")
    pwd = clave_fuerte()
    print("    lista (no se muestra: va directa al instalador)")

    # ---------------------------------------------------------------
    paso(2, "Creando el usuario de solo lectura en MySQL…")
    from core.db_adapter import get_connection
    try:
        cn = get_connection()
        cur = cn.cursor()
        cur.execute("DROP USER IF EXISTS %s@%s", (USUARIO, host_lan))
        cur.execute("CREATE USER %s@%s IDENTIFIED BY %s", (USUARIO, host_lan, pwd))
        # GRANT no admite parametros para el nombre de BD: se interpola, pero
        # todos los valores son constantes del propio script.
        cur.execute("GRANT SELECT ON `%s`.* TO %%s@%%s" % BD, (USUARIO, host_lan))
        cur.execute("FLUSH PRIVILEGES")
        cn.commit()
        print("    %s@%s  ->  SELECT sobre %s" % (USUARIO, host_lan, BD))
    except Exception as e:
        print("    ERROR: %s" % e)
        print("    (¿esta MySQL en marcha? ¿root sigue sin contrasena?)")
        return 1

    # ---------------------------------------------------------------
    paso(3, "Abriendo el puerto %s en el firewall (perfil Privada)…" % PUERTO)
    ps = (
        "$n='ONCONOVA MySQL';"
        "if (-not (Get-NetFirewallRule -DisplayName $n -ErrorAction SilentlyContinue)) {"
        "  New-NetFirewallRule -DisplayName $n -Direction Inbound -LocalPort %s"
        "    -Protocol TCP -Action Allow -Profile Private | Out-Null; 'creada'"
        "} else { 'ya existia' }" % PUERTO
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print("    regla %s" % (r.stdout or "").strip())
    else:
        print("    NO se pudo (hace falta ejecutar como administrador).")
        print("    Hazlo a mano en una consola de admin:")
        print("      New-NetFirewallRule -DisplayName 'ONCONOVA MySQL' -Direction Inbound "
              "-LocalPort %s -Protocol TCP -Action Allow -Profile Private" % PUERTO)

    # ---------------------------------------------------------------
    paso(4, "Escribiendo los datos del despliegue…")
    cfg = configparser.ConfigParser()
    cfg["servidor"] = {"ip": ip}
    cfg["base_datos"] = {"usuario": USUARIO, "password": pwd,
                         "base_datos": BD, "puerto": PUERTO}
    # SIN IA: estos equipos solo consultan, no importan nada
    cfg["ia"] = {"activa": "false", "puerto": "1234"}
    destino = os.path.join(RAIZ, "build_tools", "despliegue.ini")
    with io.open(destino, "w", encoding="utf-8") as f:
        f.write("# Generado por preparar_solo_visualizacion.py — NO subir al repositorio\n")
        cfg.write(f)
    print("    build_tools\\despliegue.ini  (IA apagada: solo consulta)")

    # ---------------------------------------------------------------
    paso(5, "Construyendo el instalador…")
    r = subprocess.run([sys.executable, os.path.join("build_tools", "construir_instalador.py")],
                       capture_output=True, text=True)
    print((r.stdout or "").rstrip())
    if r.returncode != 0:
        print((r.stderr or "")[-800:])
        return 1

    print()
    print("=" * 70)
    print("  YA ESTA. Copia ese .exe a cada PC y ejecutalo. No hay que tocar nada mas.")
    print("=" * 70)
    print("  Esas PCs podran VER, filtrar y exportar. No podran importar ni")
    print("  modificar: la cuenta solo tiene permiso de lectura.")
    print()
    print("  Para deshacerlo todo:")
    print("    mysql -u root -e \"DROP USER '%s'@'%s';\"" % (USUARIO, host_lan))
    print("    Remove-NetFirewallRule -DisplayName 'ONCONOVA MySQL'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
