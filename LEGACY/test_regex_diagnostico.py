#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test regex para Diagnostico Principal
UBICACIÓN: LEGACY/ - Script temporal de testing
"""

import re

# Texto del diagnóstico completo de IHQ250988
texto = """Región inguinal derecha. Tumor. Biopsia. LOS HALLAZGOS HISTOLÓGICOS, DE INMUNOHISTOQUÍMICA FAVORECEN LINFOMA ANAPLÁSICO ALK NEGATIVO. SOBREEXPRESIÓN DE P53 (MUTADO). VER COMENTARIO."""

print("="*80)
print("TEST: Patrón de extracción Diagnostico Principal - IHQ250988")
print("="*80)
print(f"\n📝 Texto completo:\n{texto}\n")

# ESTRATEGIA 3: Patrón MEJORADO (v6.0.12)
patron_hallazgos = r'LOS HALLAZGOS[^.]*?FAVORECEN\s+(?:UNA\s+|UN\s+)?([^.]+?)(?:\.|VER COMENTARIO|$)'
match_hallazgos = re.search(patron_hallazgos, texto, re.IGNORECASE)

if match_hallazgos:
    print("✅ ESTRATEGIA 3: Match encontrado")
    diagnostico = match_hallazgos.group(1).strip().upper()
    print(f"   Extracción inicial: {diagnostico}")
    
    # Limpiar "VER COMENTARIO" si quedó
    diagnostico = re.sub(r'\s*VER COMENTARIO.*$', '', diagnostico, flags=re.IGNORECASE).strip()
    print(f"   Después de limpiar VER COMENTARIO: {diagnostico}")
    
    # V6.0.12: Limpiar calificadores adicionales
    diagnostico = re.sub(r'\s*SOBREEXPRESI[ÓO]N\s+DE\s+P\d+.*$', '', diagnostico, flags=re.IGNORECASE).strip()
    print(f"   Después de limpiar SOBREEXPRESIÓN: {diagnostico}")
    
    print(f"\n✅ RESULTADO FINAL: {diagnostico}")
    
    if "LINFOMA" in diagnostico:
        print(f"\n🎉 ¡ÉXITO! Contiene 'LINFOMA'")
    else:
        print(f"\n❌ FALLO: No contiene 'LINFOMA'")
else:
    print("❌ ESTRATEGIA 3: No match")
