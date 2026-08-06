# -*- coding: utf-8 -*-
"""Genera version_exe.txt, el recurso de version que PyInstaller incrusta en el .exe.

POR QUE EXISTE (V6.9.93)
------------------------
El binario salia con FileVersion, ProductVersion, CompanyName y FileDescription
VACIOS, porque el EXE() del .spec no definia `version=`. Windows lo presenta
entonces como "Editor: desconocido", y SmartScreen trata peor a un ejecutable
sin metadatos. No sustituye a la firma Authenticode —eso hay que comprarlo—,
pero es lo unico de ese frente que se arregla sin gastar un peso.

El numero NO se escribe a mano: se lee de config/version_info.py, que es la
fuente de verdad de la version del programa. Asi el .exe no puede quedarse
diciendo 6.9.0 cuando el programa va por la 6.9.92, que es justo lo que pasaba.

Lo invoca COMPILADOR.bat en el paso 6. Tambien se puede ejecutar suelto:
    python build_tools\\generar_version_exe.py
"""
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from config.version_info import VERSION_INFO  # noqa: E402

VERSION = str(VERSION_INFO.get("version", "0.0.0")).strip()
NOMBRE = str(VERSION_INFO.get("version_name", "")).strip()

# VSVersionInfo exige una tupla de CUATRO enteros. "6.9.92" -> (6, 9, 92, 0)
nums = [int(x) for x in re.findall(r"\d+", VERSION)][:4]
while len(nums) < 4:
    nums.append(0)
TUPLA = ", ".join(str(n) for n in nums)

# 0c0a = espanol (Espana, alfabetizacion internacional); 04b0 = Unicode
PLANTILLA = """# -*- coding: utf-8 -*-
# GENERADO por build_tools/generar_version_exe.py — NO editar a mano.
# La version sale de config/version_info.py.
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({tupla}),
    prodvers=({tupla}),
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '0c0a04b0',
        [StringStruct('CompanyName', 'Hospital Universitario del Valle - Area de Oncologia Quirurgica'),
         StringStruct('FileDescription', 'ONCONOVA - Gestor Oncologico HUV'),
         StringStruct('FileVersion', '{version}'),
         StringStruct('InternalName', 'GestorOncologia'),
         StringStruct('LegalCopyright', 'Hospital Universitario del Valle Evaristo Garcia E.S.E.'),
         StringStruct('OriginalFilename', 'GestorOncologia.exe'),
         StringStruct('ProductName', 'ONCONOVA Gestor Oncologico'),
         StringStruct('ProductVersion', '{version}'),
         StringStruct('Comments', '{nombre}')])
    ]),
    VarFileInfo([VarStruct('Translation', [0x0c0a, 1200])])
  ]
)
"""

destino = os.path.join(RAIZ, "version_exe.txt")
io.open(destino, "w", encoding="utf-8").write(
    PLANTILLA.format(tupla=TUPLA, version=VERSION, nombre=NOMBRE.replace("'", ""))
)
print("version_exe.txt -> %s  (filevers %s)" % (VERSION, TUPLA))
