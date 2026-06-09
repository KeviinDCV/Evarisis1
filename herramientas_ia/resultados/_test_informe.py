# -*- coding: utf-8 -*-
"""Genera el informe estadistico con datos reales + renderiza pagina 1 a PNG
para verificar que el header y las tarjetas KPI ya NO se montan."""
import sys, traceback
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
STATUS = ROOT + r"\herramientas_ia\resultados\_test_informe_status.txt"

def log(m):
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(str(m) + "\n")

open(STATUS, "w").close()
try:
    from core import database_manager as dm
    from core.informe_estadistico import generar_informe_estadistico_pdf
    df = dm.get_all_records_as_dataframe()
    log(f"df_rows={len(df)}")
    out_pdf = ROOT + r"\herramientas_ia\resultados\_test_informe.pdf"
    generar_informe_estadistico_pdf(df, out_pdf)
    log("PDF_OK=" + out_pdf)
    import fitz
    doc = fitz.open(out_pdf)
    log(f"PAGINAS={doc.page_count}")
    for i in range(doc.page_count):
        pix = doc[i].get_pixmap(dpi=120)
        png = ROOT + rf"\herramientas_ia\resultados\_test_informe_p{i+1}.png"
        pix.save(png)
        log(f"PNG_OK_p{i+1}=" + png)
    doc.close()
    log("OK")
except Exception as e:
    log("ERROR=" + str(e))
    log(traceback.format_exc())
