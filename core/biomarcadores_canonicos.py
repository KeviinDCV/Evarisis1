# -*- coding: utf-8 -*-
"""Registro ÚNICO de columnas de biomarcador que son el mismo anticuerpo.

V6.9.79 — fase 3 del modelo relacional.

POR QUÉ EXISTE ESTE ARCHIVO
---------------------------
El esquema tiene columnas distintas para el MISMO anticuerpo escrito de otra
forma. `SMA` es la sigla inglesa de «actina de músculo liso»: son la misma
tinción, y aun así el esquema tiene cuatro columnas para ella. El informe elige
un nombre u otro sin criterio fijo, así que el valor caía en una columna y quien
lo buscaba miraba en la otra.

Eso no era un fallo de lectura sino de que la equivalencia estaba declarada
—cuando lo estaba— en CINCO tablas mantenidas a mano y desincronizadas entre sí:

    core/extractors/biomarker_extractor.py   (_ALIAS_PDF + name_mapping)
    core/unified_extractor.py                (mapeo a columnas)
    core/validation_checker.py               (MAPEO_BIOMARCADORES + equivalentes)
    herramientas_ia/auditor_sistema.py       (su propio mapeo)
    core/columnas_huv_ia.py                  (sus propios patrones)

La V6.4.24 arregló el extractor y nadie tocó el verificador: de ahí que 81 casos
salieran en rojo con el dato delante. Este módulo es el sitio ÚNICO donde se
declara la equivalencia; los demás la consultan.

QUÉ NO ENTRA AQUÍ
-----------------
Solo grupos comprobados contra el texto del informe. Dos anticuerpos con nombre
parecido NO son sinónimos: `ACTINA DE MÚSCULO LISO` (SMA) y `ACTINA MÚSCULO
ESPECÍFICA` (MSA/HHF35) son tinciones distintas —la segunda marca además la
esquelética y la cardíaca— y hay informes que **piden las dos en la misma
frase**. Fusionarlas destruiría información clínica.
"""

# alias -> canónica. La canónica es la forma que más usan los informes.
#
# Cada grupo lleva la evidencia que lo demuestra: la frase del informe donde el
# MISMO patólogo usa los dos nombres, o donde pide con un nombre y reporta con
# el otro. Sin esa evidencia, un grupo no se añade.
_SINONIMOS = {
    # ── Actina de músculo LISO (SMA) ─────────────────────────────────────
    # IHQ251122: «Sin marcación para desmina, ACTINA DE MÚSCULO LISO y S100.
    #             CD34 y SMA negativos» — mismo informe, mismo resultado.
    # IHQ250149: solicita «SMA», reporta «AML» negativo.
    # IHQ250488: solicita «AML», reporta «SMA» negativo.
    # IHQ250324: solicita «SMA», reporta «Actina de Músculo Liso» negativo.
    # IHQ250696: solicita «actina de músculo liso», reporta «SMA».
    # IHQ250903: solicita «Actina de Musculo Liso», reporta «SMA».
    # IHQ250997: solicita «AML», reporta «actina de músculo liso».
    "IHQ_ACTINA_MUSCULO_LISO": "IHQ_SMA",
    "IHQ_AML": "IHQ_SMA",
    "IHQ_ACTIN": "IHQ_SMA",

    # ── Actina músculo ESPECÍFICA (MSA / HHF35) — OTRO anticuerpo ────────
    # No se fusiona con el grupo de arriba. Prueba de que son distintos:
    # IHQ250123: «…myogenina, ACTINA DE MUSCULO LISO, ACTINA MUSCULO
    #             ESPECÍFICA, KI-67 y S100» — los dos en la misma petición.
    # IHQ250140: «positivas para ACTINA DE MÚSCULO ESPECIFICA, SMA y
    #             caldesmón» — los dos, con resultado propio cada uno.
    "IHQ_MSA": "IHQ_ACTINA_MUSCULO_ESPECIFICA",
}

# canónica -> todas las columnas del grupo (canónica primero)
_GRUPOS = {}
for _a, _c in _SINONIMOS.items():
    _GRUPOS.setdefault(_c, [_c]).append(_a)
_GRUPOS = {k: tuple(v) for k, v in _GRUPOS.items()}


def canonico(columna):
    """Columna canónica del grupo, o la propia si no tiene sinónimos.

    >>> canonico('IHQ_AML')
    'IHQ_SMA'
    >>> canonico('IHQ_HER2')
    'IHQ_HER2'
    """
    if not columna:
        return columna
    c = str(columna).strip().upper()
    return _SINONIMOS.get(c, c if c.startswith("IHQ_") else columna)


def grupo(columna):
    """Todas las columnas que son el mismo anticuerpo, la canónica primero.

    Devuelve una tupla de un solo elemento si la columna no tiene sinónimos,
    para poder recorrerla siempre igual.
    """
    return _GRUPOS.get(canonico(columna), (columna,))


def es_alias(columna):
    """True si la columna es un duplicado que ya no debe recibir escrituras."""
    return str(columna or "").strip().upper() in _SINONIMOS


def alias():
    """Columnas duplicadas del esquema (se conservan vacías por compatibilidad)."""
    return frozenset(_SINONIMOS)


def fusionar(valores):
    """Colapsa el grupo a un solo valor, con la regla que impone el dominio.

    `valores` es un iterable con lo que hay en cada columna del grupo. Un
    resultado real («POSITIVO») siempre gana a «NO MENCIONADO», que no es un
    hallazgo sino la marca de «se pidió y el informe no lo reporta». Si no hay
    ninguno real se conserva ese aviso, porque es el que pinta la fila en rojo
    y sigue siendo información de control de calidad.
    """
    vacios = ("", "N/A", "NA", "NAN", "NONE", "NULL", "NO APLICA",
              "NO ENCONTRADO", "-", "--")
    reales, avisos = [], []
    for v in valores:
        t = str(v or "").strip()
        if not t or t.upper() in vacios:
            continue
        (avisos if t.upper() == "NO MENCIONADO" else reales).append(t)
    if reales:
        return reales[0]
    return avisos[0] if avisos else ""
