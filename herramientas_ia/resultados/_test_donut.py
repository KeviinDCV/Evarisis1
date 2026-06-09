# -*- coding: utf-8 -*-
import sys
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.informe_estadistico import _donut
# 8 categorias -> 6 grandes + OTROS = 7 porciones (ranks 1..7), como el caso real
data = {
    "CARCINOMA METASTASICO": 67, "LESION BENIGNA / HIPERPLASIA": 35,
    "ADENOCARCINOMA COLORRECTAL": 33, "LINFOMA NO HODGKIN B": 31,
    "GLIOMA / ASTROCITOMA": 23, "CARCINOMA DE PROSTATA": 21,
    "MELANOMA": 12, "TUMOR NEUROENDOCRINO": 9,
}
_donut(data, "Hombres (prueba #)", ROOT + r"\herramientas_ia\resultados\_test_donut.png", numerar=True)
print("OK")
