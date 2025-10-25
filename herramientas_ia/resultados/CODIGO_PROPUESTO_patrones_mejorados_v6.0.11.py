#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CÓDIGO PROPUESTO - v6.0.11
Función: extract_narrative_biomarkers() - PATRONES MEJORADOS
Archivo: core/extractors/biomarker_extractor.py
Línea original: 1203

MEJORA: Patrones adicionales para GATA3 y SOX10 (IHQ250984)
"""

# ═══════════════════════════════════════════════════════════════════════
# PATRONES ACTUALES (líneas 1210-1236)
# ═══════════════════════════════════════════════════════════════════════

complex_patterns_ACTUAL = [
    # V6.0.10: PRIORIDAD MÁXIMA - Formato estructurado con guión SIN paréntesis (IHQ250984)
    r'(?i)-\s*RECEPTORES?\s+DE\s+ESTR[ÓO]GENO[S]?\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?',
    r'(?i)-\s*RECEPTORES?\s+DE\s+PROGESTERONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?',
    r'(?i)-\s*HER\s*-?\s*2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)(?:\s*\(([^)]+)\))?(?:\s+(.+?))?\.?',
    r'(?i)-\s*Ki\s*-?\s*67\s*:\s*(.+?)\.?$',

    # V6.0.10: Patrones para GATA3 y SOX10 (IHQ250984)
    r'(?i)tinción\s+nuclear\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*3',
    r'(?i)negativas?\s+para\s+S[OX]{2,3}10',  # Captura SOX10 y typo SXO10

    # V6.0.2: NUEVOS PATRONES para "Expresión molecular" CON paréntesis (IHQ250981)
    r'(?i)-?\s*RECEPTORES\s+DE\s+ESTR[ÓO]GENOS\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)',
    r'(?i)-?\s*RECEPTORES\s+DE\s+PROGESTERONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)',
    r'(?i)-?\s*SOBREEXPRESI[ÓO]N\s+DE\s+HER-?2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)\s*\(([^)]+)\)',

    # Patrones originales (descripción microscópica)
    r'(?i)receptor\s+de\s+estr[óo]genos?,\s+(positivo|negativo)(?:\s+focal)?',
    r'(?i)receptor\s+de\s+progesterona,\s+(positivo|negativo)(?:\s+focal)?',
    r'(?i)gata\s*3,\s+(positivo|negativo)(?:\s+focal)?',
    # ... más patrones ...
]

# ═══════════════════════════════════════════════════════════════════════
# PATRONES PROPUESTOS (v6.0.11)
# ═══════════════════════════════════════════════════════════════════════

complex_patterns_PROPUESTO = [
    # V6.0.10: PRIORIDAD MÁXIMA - Formato estructurado con guión SIN paréntesis (IHQ250984)
    r'(?i)-\s*RECEPTORES?\s+DE\s+ESTR[ÓO]GENO[S]?\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?',
    r'(?i)-\s*RECEPTORES?\s+DE\s+PROGESTERONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?',
    r'(?i)-\s*HER\s*-?\s*2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)(?:\s*\(([^)]+)\))?(?:\s+(.+?))?\.?',
    r'(?i)-\s*Ki\s*-?\s*67\s*:\s*(.+?)\.?$',

    # ═══════════════════════════════════════════════════════════════════════
    # V6.0.11: PATRONES MEJORADOS para GATA3 y SOX10 (IHQ250984)
    # ═══════════════════════════════════════════════════════════════════════
    # Caso IHQ250984:
    #   "Las células tumorales tienen una tinción nuclear positiva fuerte y difusa para GATA 3."
    #   "Son negativas para SXO10."
    #
    # Mejoras:
    # 1. Agregar variantes con "-" (GATA-3, SOX-10)
    # 2. Agregar patrón con "tienen una tinción"
    # 3. Agregar patrón con "son negativas"
    # 4. Capturar variantes con espacios: "GATA 3", "SOX 10", "SXO 10"
    # ═══════════════════════════════════════════════════════════════════════

    # GATA3 - POSITIVOS (múltiples variantes)
    r'(?i)tinción\s+nuclear\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*-?\s*3',
    r'(?i)positivas?\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*-?\s*3',
    r'(?i)tienen\s+una\s+tinción\s+nuclear\s+positiva\s+.*?para\s+GATA\s*-?\s*3',
    r'(?i)expresan\s+GATA\s*-?\s*3',
    r'(?i)inmunorreactivas?\s+para\s+GATA\s*-?\s*3',

    # SOX10 / SXO10 - NEGATIVOS (múltiples variantes)
    r'(?i)negativas?\s+para\s+S[OX]{2,3}\s*-?\s*10',  # Captura SOX10, SXO10, SOOX10, SO X10, SXO 10
    r'(?i)son\s+negativas?\s+para\s+S[OX]{2,3}\s*-?\s*10',  # Variante con "son"
    r'(?i)no\s+expresan\s+S[OX]{2,3}\s*-?\s*10',

    # SOX10 / SXO10 - POSITIVOS (por completitud)
    r'(?i)positivas?\s+para\s+S[OX]{2,3}\s*-?\s*10',
    r'(?i)son\s+positivas?\s+para\s+S[OX]{2,3}\s*-?\s*10',
    r'(?i)expresan\s+S[OX]{2,3}\s*-?\s*10',

    # V6.0.2: NUEVOS PATRONES para "Expresión molecular" CON paréntesis (IHQ250981)
    r'(?i)-?\s*RECEPTORES\s+DE\s+ESTR[ÓO]GENOS\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)',
    r'(?i)-?\s*RECEPTORES\s+DE\s+PROGESTERONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)',
    r'(?i)-?\s*SOBREEXPRESI[ÓO]N\s+DE\s+HER-?2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)\s*\(([^)]+)\)',

    # Patrones originales (descripción microscópica)
    r'(?i)receptor\s+de\s+estr[óo]genos?,\s+(positivo|negativo)(?:\s+focal)?',
    r'(?i)receptor\s+de\s+progesterona,\s+(positivo|negativo)(?:\s+focal)?',
    r'(?i)gata\s*3,\s+(positivo|negativo)(?:\s+focal)?',
    r'(?i)synaptophysin,\s+(positivo|negativo)(?:\s+focal)?',
    r'(?i)chromogranina,\s+(positivo|negativo)(?:\s+focal)?',
    # ... resto de patrones originales ...
]

# ═══════════════════════════════════════════════════════════════════════
# LÓGICA DE PROCESAMIENTO (fragmento relevante)
# ═══════════════════════════════════════════════════════════════════════

def extract_narrative_biomarkers_MEJORADO(text: str) -> dict:
    """Extrae biomarcadores del formato narrativo.

    v6.0.11: MEJORADO - Patrones adicionales para GATA3 y SOX10 (IHQ250984)
    """
    results = {}

    # ... código existente ...

    # Procesar patrones complejos
    for pattern in complex_patterns_PROPUESTO:
        matches = re.finditer(pattern, text)
        for match in matches:
            # ═══════════════════════════════════════════════════════════════════════
            # V6.0.11: MANEJO ESPECIAL para patrones de GATA3 y SOX10
            # ═══════════════════════════════════════════════════════════════════════

            # Detectar GATA3
            if 'GATA' in pattern.upper():
                # Ejemplo: "tinción nuclear positiva fuerte y difusa para GATA 3"
                if 'positiva' in match.group(0).lower() or 'expresan' in match.group(0).lower():
                    results['GATA3'] = 'POSITIVO'
                elif 'negativa' in match.group(0).lower() or 'no expresan' in match.group(0).lower():
                    results['GATA3'] = 'NEGATIVO'

            # Detectar SOX10 (y typo SXO10)
            elif re.search(r'S[OX]{2,3}\s*-?\s*10', pattern, re.IGNORECASE):
                # Ejemplo: "Son negativas para SXO10"
                if 'negativa' in match.group(0).lower() or 'no expresan' in match.group(0).lower():
                    results['SOX10'] = 'NEGATIVO'  # ← Normalizado a SOX10
                elif 'positiva' in match.group(0).lower() or 'expresan' in match.group(0).lower():
                    results['SOX10'] = 'POSITIVO'  # ← Normalizado a SOX10

            # ... resto de lógica existente para otros biomarcadores ...

    return results


# ═══════════════════════════════════════════════════════════════════════
# TESTS DE REGRESIÓN PROPUESTOS
# ═══════════════════════════════════════════════════════════════════════

def test_gata3_sox10_extraction():
    """Tests para validar extracción de GATA3 y SOX10 (IHQ250984)"""

    # Test 1: GATA3 positivo (caso IHQ250984)
    text1 = "Las células tumorales tienen una tinción nuclear positiva fuerte y difusa para GATA 3."
    result1 = extract_narrative_biomarkers_MEJORADO(text1)
    assert result1.get('GATA3') == 'POSITIVO', f"Esperado POSITIVO, obtenido {result1.get('GATA3')}"

    # Test 2: SOX10 negativo con typo SXO10 (caso IHQ250984)
    text2 = "Son negativas para SXO10."
    result2 = extract_narrative_biomarkers_MEJORADO(text2)
    assert result2.get('SOX10') == 'NEGATIVO', f"Esperado NEGATIVO, obtenido {result2.get('SOX10')}"

    # Test 3: GATA3 con guión
    text3 = "Las células expresan GATA-3"
    result3 = extract_narrative_biomarkers_MEJORADO(text3)
    assert result3.get('GATA3') == 'POSITIVO', f"Esperado POSITIVO, obtenido {result3.get('GATA3')}"

    # Test 4: SOX10 positivo
    text4 = "Las células son positivas para SOX 10"
    result4 = extract_narrative_biomarkers_MEJORADO(text4)
    assert result4.get('SOX10') == 'POSITIVO', f"Esperado POSITIVO, obtenido {result4.get('SOX10')}"

    # Test 5: Caso completo (IHQ250984)
    text5 = """
    REPORTE DE BIOMARCADORES:

    -RECEPTOR DE ESTRÓGENOS: Negativo.
    -RECEPTOR DE PROGESTERONA: Negativo.
    -HER 2: Positivo (Score 3+) tinción membranosa fuerte y completa en el 100 %.
    -Ki-67: Tinción nuclear en el 60% de las células tumorales.

    Las células tumorales tienen una tinción nuclear positiva fuerte y difusa para GATA 3.
    Son negativas para SXO10.
    """
    result5 = extract_narrative_biomarkers_MEJORADO(text5)
    assert result5.get('GATA3') == 'POSITIVO', f"Test completo GATA3 falló"
    assert result5.get('SOX10') == 'NEGATIVO', f"Test completo SOX10 falló"

    print("✅ Todos los tests de GATA3/SOX10 pasaron")


# ═══════════════════════════════════════════════════════════════════════
# RESUMEN DE CAMBIOS
# ═══════════════════════════════════════════════════════════════════════

"""
CAMBIOS EN PATRONES (líneas 1217-1236 aprox.):

ANTES (v6.0.10):
  2 patrones para GATA3/SOX10

DESPUÉS (v6.0.11):
  10 patrones para GATA3/SOX10
  - 5 patrones para GATA3 (positivo)
  - 5 patrones para SOX10 (positivo/negativo)
  - Soporte para typo SXO10
  - Soporte para variantes con espacios y guiones

IMPACTO:
  - Mayor cobertura de formatos narrativos
  - Mejor detección de typos (SXO10 → SOX10)
  - Normalización automática a SOX10 (no SXO10)

CASOS BENEFICIADOS:
  - IHQ250984: GATA3 y SOX10 ahora extraídos ✅
  - Cualquier caso con formato similar
  - Casos futuros con variantes de escritura
"""
