# -*- coding: utf-8 -*-
"""¿Este endpoint está DENTRO del hospital? — guarda única para los datos médicos.

POR QUÉ EXISTE (V6.9.93)
------------------------
Las capas de IA que ven texto de informes tenían cada una su propia guarda
anti-nube, y las dos comparaban contra una lista fija de loopback:

    _HOSTS_LOCALES = ('localhost', '127.0.0.1', '::1', '0.0.0.0')

Eso bastaba mientras el LLM corría en la misma máquina. Pero al montar el
esquema LAN —una sola PC sirviendo MySQL y LM Studio para todo el servicio— los
clientes tienen que apuntar a `http://192.168.2.172:1234/v1`, y esa lista lo
RECHAZABA: la IA quedaba silenciosamente apagada en cada PC cliente.

Ensanchar la guarda a «cualquier host» habría sido tirar la protección. Lo que
se hace aquí es distinto: se aceptan las direcciones **privadas** (RFC 1918 y
equivalentes IPv6), que por definición no son enrutables en internet, y se
sigue rechazando todo lo público. Un informe no puede salir del hospital por
error de configuración, pero sí puede viajar del portátil de la consulta al
servidor del despacho.

DECISIÓN DELIBERADA: para un host que NO sea loopback hay que escribir una IP,
no un nombre de máquina. Un nombre como `SERVIDOR` parece local, pero con un
dominio de búsqueda mal puesto puede resolver a cualquier sitio; comprobar el
literal deja la garantía en algo que se puede leer de un vistazo.

Rangos aceptados:
    127.0.0.0/8       loopback           ::1        loopback IPv6
    10.0.0.0/8        privada            fc00::/7   ULA IPv6
    172.16.0.0/12     privada            fe80::/10  link-local IPv6
    192.168.0.0/16    privada
    169.254.0.0/16    link-local
    0.0.0.0           "todas las interfaces"
"""
import ipaddress
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Nombres que siempre significan "esta misma máquina"
_NOMBRES_LOOPBACK = ("localhost", "localhost.localdomain", "ip6-localhost")


def host_dentro_del_hospital(host: Optional[str]) -> bool:
    """True si `host` es loopback o una dirección PRIVADA (no enrutable en internet)."""
    if not host:
        return False
    h = str(host).strip().lower().strip("[]")   # [::1] -> ::1
    if h in _NOMBRES_LOOPBACK:
        return True
    if h == "0.0.0.0":
        return True
    try:
        ip = ipaddress.ip_address(h)
    except ValueError:
        # No es una IP literal. Se rechaza a propósito: ver la nota de arriba.
        return False
    return bool(ip.is_loopback or ip.is_private or ip.is_link_local)


def endpoint_dentro_del_hospital(url: Optional[str]) -> bool:
    """True si la URL apunta a un host loopback o privado."""
    if not url:
        return False
    try:
        host = urlparse(str(url).strip()).hostname
    except Exception:
        return False
    return host_dentro_del_hospital(host)


def explicar_rechazo(url: Optional[str]) -> str:
    """Mensaje de log para cuando se rehúsa un endpoint. Dice QUÉ hacer."""
    try:
        host = urlparse(str(url or "").strip()).hostname or "(sin host)"
    except Exception:
        host = "(ilegible)"
    return (
        f"endpoint FUERA de la red del hospital ({host}): se rehúsa la llamada. "
        f"Los informes no pueden salir. Si el LLM está en otra PC del hospital, "
        f"escribe su IP privada (10.x, 172.16-31.x o 192.168.x), no un nombre de máquina."
    )
