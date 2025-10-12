"""
Herramienta para analizar PDF y crear reporte de casos problemáticos
"""
import sys
sys.path.insert(0, ".")

from pdf2image import convert_from_path
import pytesseract
import re

print("Analizando PDF ordenamientos.pdf...")
print("=" * 80)

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pdf_path = "pdfs_patologia/ordenamientos.pdf"

# Convertir solo primeras 20 páginas (10 casos aprox)
images = convert_from_path(pdf_path, first_page=1, last_page=20, dpi=200)

print(f"Páginas convertidas: {len(images)}")

casos_textos = []
caso_actual = []
numero_caso = 0

for idx, image in enumerate(images, 1):
    print(f"  Procesando página {idx}/20...", end="\r")
    texto = pytesseract.image_to_string(image, lang="spa", config="--psm 6")
    
    # Detectar si hay cambio de caso (nueva petición IHQ)
    if re.search(r"IHQ25\d{4}", texto) and caso_actual:
        numero_caso += 1
        casos_textos.append("\n".join(caso_actual))
        caso_actual = []
    
    caso_actual.append(texto)

# Agregar último caso
if caso_actual:
    numero_caso += 1
    casos_textos.append("\n".join(caso_actual))

print(f"\n\nCasos detectados: {len(casos_textos)}")

# Analizar primeros 5 casos problemáticos conocidos
casos_problematicos = [9, 11, 13, 14, 15]  # IHQ250009, 250011, 250013, 250014, 250015

print("\n" + "=" * 80)
print("ANÁLISIS DE CASOS PROBLEMÁTICOS (sin diagnóstico en BD)")
print("=" * 80)

for i in casos_problematicos[:3]:  # Analizar 3 primeros
    if i <= len(casos_textos):
        texto = casos_textos[i-1]
        
        print(f"\n\n{'='*80}")
        print(f"CASO {i} (IHQ2500{i:02d})")
        print('='*80)
        
        # Buscar petición
        peticion = re.search(r"(IHQ25\d{4})", texto)
        if peticion:
            print(f"Petición: {peticion.group(1)}")
        
        # Buscar sección de diagnóstico
        diag_match = re.search(
            r"(DIAGN[ÓO]STICO|DESCRIPCI[ÓO]N\s+DIAGN[ÓO]STICO?)[:\s]+(.*?)(?=FACTOR|CONGELACIONES|IHQ|$)",
            texto,
            re.IGNORECASE | re.DOTALL
        )
        
        if diag_match:
            print(f"\nDIAGNÓSTICO ENCONTRADO EN PDF:")
            print("-" * 80)
            diag_texto = diag_match.group(2).strip()[:500]
            print(diag_texto)
        else:
            print("\n⚠️ NO SE ENCONTRÓ SECCIÓN DE DIAGNÓSTICO")
            # Mostrar texto completo reducido
            print("\nTEXTO DEL CASO (primeros 800 caracteres):")
            print("-" * 80)
            print(texto[:800])
        
        # Buscar factor pronóstico
        factor_match = re.search(
            r"FACTOR\s+PRON[ÓO]STICO[:\s]+(.*?)(?=CONGELACIONES|$)",
            texto,
            re.IGNORECASE | re.DOTALL
        )
        
        if factor_match:
            print(f"\nFACTOR PRONÓSTICO ENCONTRADO:")
            print("-" * 80)
            print(factor_match.group(1).strip()[:300])

print("\n\n" + "=" * 80)
print("Análisis completado")
print("=" * 80)
