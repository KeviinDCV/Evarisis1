import fitz
import re
from core.extractors.medical_extractor import normalize_organ_name

pdf_path = 'pdfs_patologia/IHQ DEL 980 AL 1037.pdf'
doc = fitz.open(pdf_path)

for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    
    if 'IHQ251029' in text:
        print('='*80)
        print('SIMULANDO extract_organ_information() PARA IHQ251029')
        print('='*80)
        
        # ESTRATEGIA 2
        print('\n[ESTRATEGIA 2] Tabla estudios solicitados:')
        estudios_table_pattern = r'estudios\s+solicitados.*?(?:organo|órgano)\s+fecha\s+toma.*?(?:bloques\s+y\s+laminas\s+|almacenamiento.*?)([A-Z\s\n]+?)(?=\s+INFORME\s+DE|\s+ESTUDIO\s+DE|$)'
        estudios_match = re.search(estudios_table_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if estudios_match:
            organo_from_table = estudios_match.group(1).strip()
            organo_from_table_limpio = re.sub(r'\s*\n\s*', ' ', organo_from_table).strip()
            normalized_estrategia2 = normalize_organ_name(organo_from_table_limpio)
            
            print(f'  Capturado: "{organo_from_table}" ({len(organo_from_table)} chars)')
            print(f'  Limpio: "{organo_from_table_limpio}" ({len(organo_from_table_limpio)} chars)')
            print(f'  Normalizado: "{normalized_estrategia2}" ({len(normalized_estrategia2)} chars)')
            
            if normalized_estrategia2 != 'ORGANO_NO_ESPECIFICADO':
                print(f'  [RETORNA] "{normalized_estrategia2}"')
        else:
            print('  [NO MATCH]')
        
        # ESTRATEGIA 3
        print('\n[ESTRATEGIA 3] Bloques y laminas:')
        bloques_pattern = r'bloques\s+y\s+laminas\s+([A-Z][A-Z \n]{2,120})\s*(?=IHQ\d+|ESTUDIO DE|$)'
        bloques_match = re.search(bloques_pattern, text, re.IGNORECASE | re.MULTILINE)
        
        if bloques_match:
            organo_from_bloques = bloques_match.group(1).strip()
            organo_from_bloques_limpio = re.sub(r'\s*\n\s*', ' ', organo_from_bloques).strip()
            normalized_estrategia3 = normalize_organ_name(organo_from_bloques_limpio)
            
            print(f'  Capturado: "{organo_from_bloques}" ({len(organo_from_bloques)} chars)')
            print(f'  Limpio: "{organo_from_bloques_limpio}" ({len(organo_from_bloques_limpio)} chars)')
            print(f'  Normalizado: "{normalized_estrategia3}" ({len(normalized_estrategia3)} chars)')
            
            if normalized_estrategia3 != 'ORGANO_NO_ESPECIFICADO':
                print(f'  [RETORNA] "{normalized_estrategia3}"')
        else:
            print('  [NO MATCH]')
        
        break

doc.close()
