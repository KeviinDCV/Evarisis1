# -*- coding: utf-8 -*-
"""Comparativa de extraccion IA: mistral-7b vs mistral-nemo.
Para cada PDF individual: OCR -> mismo prompt de extraccion -> cada modelo -> JSON.
Guardado incremental para monitoreo."""
import sys, os, json, time, traceback, urllib.request
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
OUT = ROOT + r"\herramientas_ia\resultados\_eval_ia.json"

PDFS = [
    ROOT + r"\pdfs_patologia\IHQ251391.pdf",
    ROOT + r"\pdfs_patologia\IHQ251411.pdf",
    ROOT + r"\pdfs_patologia\IHQ251420.pdf",
    ROOT + r"\pdfs_patologia\IHQ251436.pdf",
]
MODELS = ["mistralai/mistral-7b-instruct-v0.3", "mistralai/mistral-nemo-instruct-2407"]

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
- "diagnostico_coloracion": diagnostico base del estudio de coloracion (H&E), con grado si aplica.
- "biomarcadores_solicitados": lista de nombres de biomarcadores estudiados (HER2, Ki-67, etc.).
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

def llm(ocr, model):
    # mistral-7b en LM Studio NO acepta rol 'system' -> fusionamos todo en 'user'.
    # Tampoco acepta response_format json_object -> pedimos JSON por prompt + parse robusto.
    user = SYSTEM + "\n\nINFORME (extrae los campos y responde SOLO con el JSON):\n" + ocr[:12000]
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": user}],
        "temperature": 0, "max_tokens": 2500,
    }).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:1234/v1/chat/completions",
                                 data=body, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=900)
    d = json.load(r)
    return d["choices"][0]["message"]["content"], d.get("usage", {})

out = {"_estado": "iniciando"}
def save():
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
save()

try:
    from core.processors.ocr_processor import pdf_to_text_enhanced
    for pdf in PDFS:
        name = os.path.basename(pdf)
        out[name] = {"estado": "ocr..."}; save()
        try:
            t0 = time.time()
            ocr = pdf_to_text_enhanced(pdf)
            out[name] = {"ocr_chars": len(ocr), "ocr_seg": round(time.time() - t0, 1),
                         "ocr_preview": ocr[:1800], "models": {}}
        except Exception as e:
            out[name] = {"ocr_error": str(e)[:200]}; save(); continue
        save()
        for model in MODELS:
            short = model.split("/")[-1]
            try:
                t0 = time.time()
                content, usage = llm(ocr, model)
                dt = round(time.time() - t0, 1)
                parsed = _parse_json(content)
                raw = None if parsed is not None else content[:3000]
                out[name]["models"][short] = {"seg": dt, "usage": usage, "parsed": parsed, "raw_si_fallo": raw}
            except Exception as e:
                out[name]["models"][short] = {"error": str(e)[:250]}
            save()
    out["_estado"] = "completo"
    save()
except Exception as e:
    out["_estado"] = "ERROR"; out["_error"] = str(e); out["_tb"] = traceback.format_exc()
    save()
