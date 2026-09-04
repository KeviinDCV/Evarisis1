# -*- coding: utf-8 -*-
"""Actualización de la aplicación por la red, usando el propio MySQL como canal.

POR QUÉ ASÍ
-----------
Todos los equipos ya se conectan al mismo servidor MySQL, así que sirve de tablón de
anuncios sin montar nada nuevo: ni servidor web, ni servicio, ni carpetas compartidas
con sus permisos.

🛑 EN UNA BASE APARTE (`onconova_updates`), NO en `huv_oncologia`.
La base clínica ocupa ~100 MB y el instalador ~116 MB: metido dentro, cada `mysqldump`
pasaría de 81 MB a más de 200 por algo que no son datos de pacientes. Con la base
separada, el respaldo de siempre sigue funcionando igual y nunca la toca.

EL BINARIO VA TROCEADO
----------------------
`max_allowed_packet` en este servidor son 512 MB y cabría de una pieza, pero se trocea a
8 MB igualmente: permite barra de progreso, sobrevive a un `net_read_timeout` de 30 s en
un enlace lento, y no obliga a reservar 116 MB de memoria de golpe en las dos puntas.

SEGURIDAD
---------
Se descarga un ejecutable y se lanza, así que:
  · se verifica el SHA-256 ANTES de ejecutar nada; si no cuadra, se descarta;
  · NUNCA se instala solo: el usuario ve qué versión es, qué cambia, y decide;
  · solo se comprueba AL ARRANCAR. A media ejecución jamás: si alguien lleva dos horas
    de lote, un instalador saltando encima le destruye el trabajo.
Si el servidor no responde, se sigue sin actualizar y sin molestar: una actualización
nunca debe impedir trabajar.
"""
from __future__ import annotations

import hashlib
import logging
import os
import subprocess
import sys
import tempfile

BASE_ACTUALIZACIONES = 'onconova_updates'
TROZO = 8 * 1024 * 1024          # 8 MB


def _version_tupla(v):
    """'6.9.105' -> (6, 9, 105). Lo que no sea número cuenta como 0 y así una versión
    con sufijo raro nunca se considera «más nueva» por accidente."""
    partes = []
    for p in str(v or '').strip().split('.'):
        try:
            partes.append(int(p))
        except ValueError:
            partes.append(0)
    while len(partes) < 3:
        partes.append(0)
    return tuple(partes[:3])


def es_mas_nueva(candidata, actual) -> bool:
    return _version_tupla(candidata) > _version_tupla(actual)


def _conectar(cfg):
    """Conexión a la base de actualizaciones, reutilizando las credenciales del cliente.

    🛑 `db_adapter._load_config()` devuelve las claves en ESPAÑOL: `usuario`, `puerto`,
    `base_datos`. Usando los nombres ingleses el usuario salía vacío y pymysql caía al
    usuario del sistema operativo -> "Access denied for user 'kechavarro'". Y como este
    módulo falla en silencio a propósito, el error no se habría visto nunca en
    producción: solo se cazó con una prueba de punta a punta. Se aceptan ambos nombres.
    """
    import pymysql
    return pymysql.connect(
        host=cfg.get('host') or '127.0.0.1',
        port=int(cfg.get('puerto') or cfg.get('port') or 3306),
        user=cfg.get('usuario') or cfg.get('user') or '',
        password=cfg.get('password') or cfg.get('clave') or '',
        database=BASE_ACTUALIZACIONES,
        charset=cfg.get('charset') or 'utf8mb4',
        connect_timeout=6,
    )


def consultar_ultima(cfg, version_actual):
    """¿Hay una versión más nueva publicada? Devuelve el dict de la versión o None.

    Nunca lanza: si el servidor no responde, o la base de actualizaciones no existe
    todavía, se devuelve None y la aplicación arranca con normalidad.
    """
    try:
        cn = _conectar(cfg)
    except Exception as e:
        logging.info("Actualizador: sin canal de actualizaciones (%s)", e)
        return None
    try:
        cur = cn.cursor()
        cur.execute(
            "SELECT version, fecha, notas, bytes, sha256, nombre_archivo "
            "FROM versiones ORDER BY fecha DESC LIMIT 1")
        fila = cur.fetchone()
        if not fila:
            return None
        info = dict(zip(('version', 'fecha', 'notas', 'bytes', 'sha256',
                         'nombre_archivo'), fila))
        if not es_mas_nueva(info['version'], version_actual):
            return None
        logging.info("Actualizador: hay versión %s (tenemos %s)",
                     info['version'], version_actual)
        return info
    except Exception as e:
        logging.info("Actualizador: no se pudo consultar (%s)", e)
        return None
    finally:
        try:
            cn.close()
        except Exception:
            pass


def descargar(cfg, info, progreso=None):
    """Trae el instalador a disco y VERIFICA su SHA-256.

    `progreso` recibe (bytes_hechos, bytes_totales) para pintar una barra.
    Devuelve la ruta del archivo, o None si algo falló. Si el hash no cuadra el archivo
    se borra: se está a punto de EJECUTARLO, así que ante la duda no se ejecuta nada.
    """
    destino = os.path.join(tempfile.gettempdir(),
                           info.get('nombre_archivo')
                           or ('ONCONOVA_%s_setup.exe' % info['version']))
    try:
        cn = _conectar(cfg)
    except Exception as e:
        logging.warning("Actualizador: no se pudo conectar para descargar (%s)", e)
        return None
    try:
        cur = cn.cursor()
        cur.execute("SELECT n, datos FROM partes WHERE version=%s ORDER BY n",
                    (info['version'],))
        h = hashlib.sha256()
        hechos = 0
        total = int(info.get('bytes') or 0)
        with open(destino, 'wb') as fh:
            while True:
                fila = cur.fetchone()
                if not fila:
                    break
                datos = fila[1]
                fh.write(datos)
                h.update(datos)
                hechos += len(datos)
                if progreso:
                    try:
                        progreso(hechos, total)
                    except Exception:
                        pass
        if info.get('sha256') and h.hexdigest().lower() != str(info['sha256']).lower():
            logging.error("Actualizador: el SHA-256 NO cuadra. Se descarta el archivo.")
            try:
                os.remove(destino)
            except Exception:
                pass
            return None
        logging.info("Actualizador: descargado %s (%d bytes, hash verificado)",
                     destino, hechos)
        return destino
    except Exception as e:
        logging.error("Actualizador: fallo descargando (%s)", e)
        return None
    finally:
        try:
            cn.close()
        except Exception:
            pass


def lanzar_instalador(ruta):
    """Arranca el instalador y devuelve True si se lanzó.

    Quien llama debe CERRAR la aplicación acto seguido: el instalador no puede
    sustituir un .exe que sigue en ejecución.
    """
    try:
        if os.name == 'nt':
            os.startfile(ruta)          # noqa: S606 - lo eligió el usuario
        else:
            subprocess.Popen([ruta])
        return True
    except Exception as e:
        logging.error("Actualizador: no se pudo lanzar el instalador (%s)", e)
        return False
