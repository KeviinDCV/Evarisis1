# -*- coding: utf-8 -*-
"""Publica un instalador para que los equipos de la red lo vean y puedan actualizarse.

    python build_tools\\publicar_actualizacion.py                    # el ultimo instalador
    python build_tools\\publicar_actualizacion.py --archivo X.exe    # uno concreto
    python build_tools\\publicar_actualizacion.py --listar           # que hay publicado
    python build_tools\\publicar_actualizacion.py --borrar 6.9.103   # quitar una version

QUE HACE
--------
Trocea el instalador en pedazos de 8 MB y los guarda en la base `onconova_updates`, con
su SHA-256 y las notas de la version sacadas del CHANGELOG. Los clientes lo consultan al
arrancar (core/actualizador.py) y ofrecen instalarlo.

🛑 BASE APARTE, NO `huv_oncologia`. La base clinica ocupa ~100 MB y el instalador ~116:
metido dentro, cada `mysqldump` pasaria de 81 MB a mas de 200 por algo que no son datos
de pacientes. Asi el respaldo de siempre sigue igual de ligero y nunca la toca.

SE GUARDAN COMO MUCHO 2 VERSIONES. Cada una son ~116 MB; sin poda, publicar diez deja
1,1 GB de binarios muertos en el servidor.
"""
import argparse
import hashlib
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)

BASE = 'onconova_updates'
TROZO = 8 * 1024 * 1024
CONSERVAR = 2          # cuantas versiones se mantienen publicadas


def _cfg_servidor():
    """Credenciales del SERVIDOR (root), del config.ini local. No se imprimen nunca."""
    import configparser
    cp = configparser.ConfigParser(interpolation=None)
    cp.read(os.path.join('config', 'config.ini'), encoding='utf-8')
    d = cp['database'] if cp.has_section('database') else {}
    return {'host': d.get('host', '127.0.0.1'), 'port': int(d.get('port', 3306)),
            'user': d.get('user', 'root'), 'password': d.get('password', '')}


def _conectar(sin_base=False):
    import pymysql
    c = _cfg_servidor()
    return pymysql.connect(host=c['host'], port=c['port'], user=c['user'],
                           password=c['password'],
                           database=None if sin_base else BASE,
                           charset='utf8mb4')


def crear_esquema():
    cn = _conectar(sin_base=True)
    cur = cn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS %s "
                "DEFAULT CHARACTER SET utf8mb4" % BASE)
    cur.execute("USE %s" % BASE)
    cur.execute("""CREATE TABLE IF NOT EXISTS versiones (
        version        VARCHAR(20)  NOT NULL PRIMARY KEY,
        fecha          DATETIME     NOT NULL,
        notas          TEXT,
        bytes          BIGINT       NOT NULL,
        sha256         CHAR(64)     NOT NULL,
        nombre_archivo VARCHAR(200) NOT NULL
    ) ENGINE=InnoDB""")
    cur.execute("""CREATE TABLE IF NOT EXISTS partes (
        version VARCHAR(20) NOT NULL,
        n       INT         NOT NULL,
        datos   LONGBLOB    NOT NULL,
        PRIMARY KEY (version, n)
    ) ENGINE=InnoDB""")
    # El usuario de consulta necesita LEER, nada mas. Sin este GRANT los clientes no
    # ven las actualizaciones (y el fallo es silencioso, por diseno).
    #
    # 🛑 SE DESCUBREN LOS PATRONES DE HOST, NO SE SUPONEN. Aqui habia tres cuentas
    # distintas —huv_consulta@'%', @'localhost' y @'192.168.2.%'— y MySQL resuelve por
    # la coincidencia MAS ESPECIFICA: un equipo de la red entra por '192.168.2.%'.
    # Con los dos patrones fijos que habia antes, justo esa se quedaba sin permiso y los
    # clientes de la LAN —los unicos que importan aqui— no veian ninguna actualizacion.
    cur.execute("SELECT user, host FROM mysql.user WHERE user='huv_consulta'")
    cuentas = cur.fetchall()
    if not cuentas:
        print('   aviso: no existe el usuario huv_consulta; los clientes no veran nada')
    for u, h in cuentas:
        try:
            cur.execute("GRANT SELECT ON %s.* TO '%s'@'%s'" % (BASE, u, h))
            print('   permiso de lectura -> %s@%s' % (u, h))
        except Exception as e:
            print('   aviso: no se pudo dar SELECT a %s@%s (%s)' % (u, h, e))
    try:
        cur.execute("FLUSH PRIVILEGES")
    except Exception:
        pass
    cn.commit()
    cn.close()


def _notas_del_changelog(version):
    """Saca el bloque de esa version del CHANGELOG para mostrarlo en el aviso."""
    try:
        t = io.open(os.path.join('documentacion', 'CHANGELOG.md'),
                    encoding='utf-8').read()
    except Exception:
        return ''
    m = re.search(r'(?m)^##\s*\[%s[^\]]*\][^\n]*\n(.*?)(?=^##\s*\[|\Z)'
                  % re.escape(version), t, re.S)
    if not m:
        return ''
    cuerpo = m.group(1)
    lineas = []
    for ln in cuerpo.split('\n'):
        s = ln.strip()
        if not s or s.startswith('```') or s.startswith('---'):
            continue
        s = re.sub(r'[*_`#]', '', s)
        lineas.append(s)
        if len(lineas) >= 12:
            break
    return '\n'.join(lineas).strip()


def _ultimo_instalador():
    d = 'dist_instalador'
    if not os.path.isdir(d):
        return None
    ex = [os.path.join(d, f) for f in os.listdir(d)
          if f.lower().endswith('.exe') and f.upper().startswith('ONCONOVA')]
    return max(ex, key=os.path.getmtime) if ex else None


def publicar(ruta):
    from config.version_info import VERSION_INFO
    version = VERSION_INFO['version']
    m = re.search(r'(\d+\.\d+\.\d+)', os.path.basename(ruta))
    if m and m.group(1) != version:
        print('AVISO: el instalador dice %s y config/version_info.py dice %s.'
              % (m.group(1), version))
        print('       Se publica como %s (lo que diga el archivo).' % m.group(1))
        version = m.group(1)

    datos = open(ruta, 'rb').read()
    sha = hashlib.sha256(datos).hexdigest()
    print('archivo  : %s' % ruta)
    print('tamano   : %.1f MB' % (len(datos) / 1048576.0))
    print('sha256   : %s' % sha)
    print('version  : %s' % version)

    crear_esquema()
    cn = _conectar()
    cur = cn.cursor()
    cur.execute("DELETE FROM partes WHERE version=%s", (version,))
    cur.execute("DELETE FROM versiones WHERE version=%s", (version,))
    cur.execute(
        "INSERT INTO versiones (version, fecha, notas, bytes, sha256, nombre_archivo)"
        " VALUES (%s, NOW(), %s, %s, %s, %s)",
        (version, _notas_del_changelog(version), len(datos), sha,
         os.path.basename(ruta)))
    n = 0
    for i in range(0, len(datos), TROZO):
        cur.execute("INSERT INTO partes (version, n, datos) VALUES (%s,%s,%s)",
                    (version, n, datos[i:i + TROZO]))
        n += 1
        print('   subido %d/%d' % (n, (len(datos) + TROZO - 1) // TROZO), end='\r')
    cn.commit()
    print('\n   %d trozos guardados' % n)

    # poda: dejar solo las CONSERVAR mas recientes
    cur.execute("SELECT version FROM versiones ORDER BY fecha DESC")
    todas = [r[0] for r in cur.fetchall()]
    for v in todas[CONSERVAR:]:
        cur.execute("DELETE FROM partes WHERE version=%s", (v,))
        cur.execute("DELETE FROM versiones WHERE version=%s", (v,))
        print('   podada version antigua: %s' % v)
    cn.commit()
    cn.close()
    print('\nPUBLICADO. Los equipos lo veran al arrancar.')


def listar():
    try:
        cn = _conectar()
    except Exception as e:
        print('no hay nada publicado todavia (%s)' % e)
        return
    cur = cn.cursor()
    cur.execute("SELECT version, fecha, ROUND(bytes/1048576,1), nombre_archivo "
                "FROM versiones ORDER BY fecha DESC")
    filas = cur.fetchall()
    if not filas:
        print('no hay ninguna version publicada')
    else:
        print('%-10s %-20s %8s  %s' % ('VERSION', 'FECHA', 'MB', 'ARCHIVO'))
        for v, f, mb, a in filas:
            print('%-10s %-20s %8s  %s' % (v, f, mb, a))
    cn.close()


def borrar(version):
    cn = _conectar()
    cur = cn.cursor()
    cur.execute("DELETE FROM partes WHERE version=%s", (version,))
    cur.execute("DELETE FROM versiones WHERE version=%s", (version,))
    cn.commit()
    cn.close()
    print('borrada la version %s' % version)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--archivo')
    ap.add_argument('--listar', action='store_true')
    ap.add_argument('--borrar')
    a = ap.parse_args()
    if a.listar:
        listar()
    elif a.borrar:
        borrar(a.borrar)
    else:
        ruta = a.archivo or _ultimo_instalador()
        if not ruta or not os.path.exists(ruta):
            print('No encuentro el instalador. Usa --archivo RUTA')
            sys.exit(1)
        publicar(ruta)
