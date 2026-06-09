# -*- coding: utf-8 -*-
"""Valida es_diagnostico_no_valido() contra los 2073: detecta FALSOS POSITIVOS
(diagnosticos reales marcados como no-validos = regresion)."""
import sys
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core import database_manager as dm
import core.normalizador_diagnosticos as nd, core.normalizador_organos as no
from core.extractor_diagnostico_ia import es_diagnostico_no_valido

NO_ONCO = {
    "NEGATIVO PARA MALIGNIDAD", "MUESTRA NO REPRESENTATIVA / NO DIAGNOSTICA",
    "HALLAZGO HISTOLOGICO NORMAL / NO PATOLOGICO", "RESULTADO IHQ (SIN DIAGNOSTICO ESPECIFICO)",
    "ESTUDIO IHQ (SIN DIAGNOSTICO ESPECIFICO)", "GLIOSIS / LESION REACTIVA SNC",
    "RECHAZO DE TRASPLANTE", "MALFORMACION DEL DESARROLLO / HETEROTOPIA SNC",
    "PROCESO INFLAMATORIO / INFECCIOSO (NO NEOPLASICO)", "HALLAZGO NO NEOPLASICO / NEGATIVO (OTRO)",
    "ESTUDIO DE MEDULA OSEA (MORFOLOGIA)", "MUESTRA INSUFICIENTE / LIMITADA (OTRO)",
    "SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)", "ENFERMEDAD DE HIRSCHSPRUNG / CELULAS GANGLIONARES",
    "OTRO / NO CATEGORIZADO", "SIN DATO",
}
df = dm.get_all_records_as_dataframe()
dc = "Diagnostico Principal"; co = no.elegir_columna_organo(df.columns)
org = df[co].apply(no.normalizar_organo) if co is not None else None

flagged = 0
falsos_pos = []   # flagged PERO categoriza a un diagnostico ONCOLOGICO real
flagged_list = []
for i in range(len(df)):
    dx = str(df[dc].iloc[i])
    if es_diagnostico_no_valido(dx):
        flagged += 1
        cat = nd.categorizar_diagnostico_con_organo(dx, org.iloc[i] if org is not None else None)
        flagged_list.append((dx[:55], cat))
        if cat not in NO_ONCO:  # categoriza a algo oncologico => POSIBLE falso positivo
            falsos_pos.append((dx[:70], cat))

print(f"Total casos: {len(df)}")
print(f"Marcados como NO-validos (dispararian IA): {flagged}")
print(f"FALSOS POSITIVOS (marcado pero categoriza ONCOLOGICO): {len(falsos_pos)}")
for dx, cat in falsos_pos[:40]:
    print(f"   !! [{cat}]  {dx!r}")
print()
print("--- muestra de marcados (deben ser todos no-diagnosticos) ---")
from collections import Counter
catc = Counter(c for _, c in flagged_list)
for c, n in catc.most_common():
    print(f"   {n:3d}  -> {c}")
