# -*- coding: utf-8 -*-
"""Diagnostico: por que estos dx caen en OTRO / NO CATEGORIZADO."""
import sys, json
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.normalizador_diagnosticos import (
    categorizar_diagnostico, normalizar_texto, stripear_preambulos,
)

pruebas = [
    "TUMOR NEUROENDOCRINO\nGRADO HISTOLÓGICO: BIEN DIFERENCIADO G2",
    "TUMOR DEL ESTROMA DE LOS CORDONES SEXUALES :FIBROTECOMA OVARICO CON CALCIFICACIONES",
    "Tumor de células de Leydig (Tumor del hilio ovárico)",
    "ENFERMEDAD NODULAR TIROIDEA",
    "HISTIOCITOSIS DE CÉLULAS DE LANGERHANS",
    "TUMOR FIBOSO SOLITARIO",
    "pineoblastoma (WHO grado 4)",
    "COMPROMISO POR TUMOR DE WILMS ( COMPONENTE BLASTÉMICO)",
    "NEGATIVA PARA MALIGNIDAD",
    "QUERATOSIS ACTINICA (Piel de antebrazo izquierdo proximal...)",
]
res = []
for p in pruebas:
    t_norm = normalizar_texto(p)
    t_strip = stripear_preambulos(t_norm)
    cat = categorizar_diagnostico(p)
    res.append({"dx": p[:60], "norm": t_norm[:80], "strip": t_strip[:80], "cat": cat})
with open(ROOT + r"\herramientas_ia\resultados\_test_categoria.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
for r in res:
    print(f"[{r['cat']}]  <-  {r['dx']!r}")
    print(f"     strip={r['strip']!r}")
