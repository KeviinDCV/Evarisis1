# -*- coding: utf-8 -*-
"""Prueba SOLO con nemo (modelo actual): OCR de PDFs nuevos + extraccion nemo.
Guarda el OCR completo (ground-truth) y el JSON de nemo."""
import sys, os, json, time, traceback, urllib.request
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
OUT = ROOT + r"\herramientas_ia\resultados\_eval_nemo.json"

PDFS = [
    ROOT + r"\pdfs_patologia\IHQ251409.pdf",
    ROOT + r"\pdfs_patologia\IHQ251424.pdf",
]
MODEL = "mistralai/mistral-nemo-instruct-2407"

SYSTEM = """Eres un patologo experto extrayendo datos de un informe de inmunohistoquimica (IHQ) del Hospital Universitario del Valle.
Extrae UNICAMENTE lo que aparece en el texto. Si un dato no esta, usa "" (vacio). NO inventes ni infieras.
Responde SOLO con JSON valido con esta estructura exacta:
{
 "numero_caso": "",
 "organo": "",
 "tipo_estudio": "",
 "malignidad": "",
 "diagnostico_principal": "",
 "diagnostico_coloracion": "",
 "biomarcadores_solicitados": [],
 "biomarcadores": {}
}
- "malignidad": PRESENTE o AUSENTE segun el diagnostico.
- "biomarcadores": objeto nombre->resultado TAL CUAL el PDF (POSITIVO/NEGATIVO/porcentaje/score). Incluye TODOS los que aparezcan."""

def _parse_json(txt):
    try:
        return json.loads(txt)
    except Exception:
        pass
    a = txt.find("{"); b = txt.rfind("}")
    if a != -1 and b != -1 and b > a:
        try:
            return json.loads(txt[a:b + 1])
        except Exception:
            return None
    return None

def llm(ocr):
    user = SYSTEM + "\n\nINFORME (extrae los campos y responde SOLO con el JSON):\n" + ocr[:12000]
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": user}],
                       "temperature": 0, "max_tokens": 2500}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:1234/v1/chat/completions",
                                 data=body, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=900)
    d = json.load(r)
    return d["choices"][0]["message"]["content"], d.get("usage", {})

out = {"_estado": "iniciando", "_modelo": MODEL}
def save():
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
save()
try:
    from core.processors.ocr_processor import pdf_to_text_enhanced
    for pdf in PDFS:
        nm = os.path.splitext(os.path.basename(pdf))[0]
        ocr = pdf_to_text_enhanced(pdf)
        with open(ROOT + r"\herramientas_ia\resultados\_gt_" + nm + ".txt", "w", encoding="utf-8") as f:
            f.write(ocr)
        out[nm] = {"ocr_chars": len(ocr)}
        save()
        t0 = time.time()
        content, usage = llm(ocr)
        parsed = _parse_json(content)
        out[nm]["nemo"] = {"seg": round(time.time() - t0, 1), "usage": usage,
                           "parsed": parsed, "raw_si_fallo": None if parsed else content[:2500]}
        save()
    out["_estado"] = "completo"; save()
except Exception as e:
    out["_estado"] = "ERROR"; out["_error"] = str(e); out["_tb"] = traceback.format_exc(); save()
