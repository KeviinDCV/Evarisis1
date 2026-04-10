#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extractor de biomarcadores IHQ

Extrae biomarcadores con configuración integrada (antes en config/patterns/biomarker_patterns.py)

Versión: 6.1.8 - NORMALIZACIÓN HEMATOLÓGICA COMPLETA
Autor: Sistema HUV Refactorizado
Nota: Toda la configuración de patrones está ahora en este archivo para centralización

Cambios v6.1.8:
  - ✅ NUEVO: Patrones específicos para casos hematológicos (IHQ250992)
  - ✅ "EXPRESIÓN DE [BIOMARCADOR]" → "POSITIVO"
  - ✅ "EXPRESIÓN ABERRANTE PARA X" → "POSITIVO (aberrante)"
  - ✅ "RESTRICCIÓN DE CADENAS LIVIANAS KAPPA" → "POSITIVO (restricción kappa)"
  - ✅ "EXPRESIÓN DÉBIL PARA X" → "POSITIVO (débil)"
  - ✅ "CON EXPRESIÓN DE X" → "POSITIVO"
  - ✅ Resuelve: IHQ250992 CD38, CD138, CD56, KAPPA con formatos narrativos

Cambios v6.1.7:
  - ✅ CRÍTICO: Limpieza completa de \n, \r, \t en valores de biomarcadores (normalize_biomarker_value)
  - ✅ CRÍTICO: Estandarización de formatos narrativos a POSITIVO/NEGATIVO + contexto
  - ✅ "NO ES CONTRIBUTIVA" → "NEGATIVO (no contributiva)"
  - ✅ "AUSENCIA DE EXPRESION PARA X (MUTADO)" → "NEGATIVO (mutado)"
  - ✅ "EXPRESION POSITIVA (MUTADO)" → "POSITIVO (mutado)"
  - ✅ Limpieza de descripciones macroscópica/microscópica antes de guardar en BD
  - ✅ Resuelve: IHQ251011 P53 con "\n" residual, formatos largos no estandarizados

Cambios v6.1.6:
  - ✅ FIX P53: Captura "NO es contributiva" completo (línea 365) - incluye negación
  - ✅ NUEVO IDH1: Definición completa con patrones neuropatología (línea 511-530)
  - ✅ NUEVO ATRX: Definición completa con patrones neuropatología (línea 532-552)
  - ✅ Patrones específicos: "expresión para IDH1 es positiva (mutado)", "Ausencia de expresión para ATRX (mutado)"
  - ✅ Normalización inteligente: IDH1 positivo = mutado, ATRX ausencia = negativo (mutado)

Cambios v6.1.5:
  - ✅ FIX P53: Nuevo patrón "expresión para p53 no es contributiva" (línea 356) - casos neuropatología
  - ✅ FIX Ki-67: Nuevo patrón "El Ki-67 es del X%" (línea 106) - casos neuropatología
  - ✅ Resuelve: IHQ251011 donde P53 capturaba fragmento erróneo y Ki-67 no se extraía
  - ✅ Nuevos valores posibles: P53 acepta "NO CONTRIBUTIVA" y "NO CONTRIBUTIVO"

Cambios v6.1.4:
  - ✅ FIX CRÍTICO P63: Biomarcadores sin signo +/- en formato compacto ahora infieren POSITIVO (línea 2110)
  - ✅ Resuelve: "p40+/PAX8+/p63" → P63 sin signo ahora se detecta como POSITIVO
  - ✅ Validación inteligente: Solo infiere POSITIVO si normalize_biomarker_name() lo reconoce

Cambios v6.1.3:
  - ✅ FIX CRÍTICO P16: Nuevos patrones para "POSITIVO PARA SOBREEXPRESIÓN DE P16" (línea 225)
  - ✅ FIX CRÍTICO PAX8: Patrón para formato compacto "PAX8+" en inmunofenotipo (línea 2080)
  - ✅ Resuelve: IHQ251010 donde P16 capturaba "." y PAX8 se extraía como NEGATIVO en lugar de POSITIVO
  - ✅ Nuevo patrón: Formato compacto de inmunofenotipo "CK7+/CK20-, p40+/PAX8+" (línea 2080)
  - ✅ Normalización P16: Agrega "sobreexpresión" → POSITIVO automáticamente

Cambios v5.0.4:
  - ✅ FIX CRÍTICO: Patrón narrativo "inmunorreactividad moderada y fuerte a receptores de estrogeno" (línea 125)
  - ✅ Resuelve: IHQ251007 capturaba solo "." en vez del valor completo
  - ✅ Nuevo patrón ANTES del genérico (línea 135) para priorizar casos narrativos
  - ✅ Soporta: "moderada", "fuerte", "moderada y fuerte", con "para" o "a"
  - ✅ Asigna: POSITIVO automáticamente (interpretación de inmunorreactividad)

Cambios v5.0.3:
  - ✅ NUEVO PATRÓN: "Hay positividad para celulas mioepiteliales X y Y" (línea 3161)
  - ✅ Resuelve: IHQ251007 no detectaba CK5/6 y P63 en descripción microscópica
  - ✅ Captura: "Hay positividad para celulas mioepiteliales CK5/6 y P63"
  - ✅ Soporta: con/sin tilde en "células", opcional "mioepiteliales"
  - ✅ Asigna: Valor POSITIVO automáticamente para todos los biomarcadores detectados

Cambios v5.0.2:
  - ✅ NUEVO PATRÓN ER/PR: "R. Estrogenos" y "R. Progesterona" con salto de línea
  - ✅ PATRÓN NARRATIVO MEJORADO: Captura multilínea con lookahead (ignora "R." como fin de lista)
  - ✅ Resuelve: IHQ250994 donde "R.\nEstrogenos" no se detectaba
  - ✅ Patrones agregados en ER y PR con soporte para \n entre "R." y nombre
  - ✅ extract_narrative_biomarkers() ahora captura "marcación positiva para P40, R.\nEstrogenos además"
  - ✅ Estado POSITIVO/NEGATIVO se asigna correctamente desde contexto de lista narrativa

Cambios v5.0.1:
  - Corregido split por "/" en extract_narrative_biomarkers
  - "/" ahora se usa solo para variantes del mismo biomarcador (EBERP4/Ep-CAM)
  - Mejora captura de P63 y BER-EP4 en listas narrativas
"""

import re
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Agregar path del proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ======================== DEFINICIONES DE BIOMARCADORES ========================
# Movido desde: config/patterns/biomarker_patterns.py

BIOMARKER_DEFINITIONS = {
    'HER2': {
        'nombres_alternativos': ['HER-2', 'HER 2', 'CERB-B2', 'ERBB2'],
        'descripcion': 'Receptor 2 del factor de crecimiento epidérmico humano',
        'patrones': [
            # V6.0.12: PRIORIDAD 0 - Formato narrativo en descripción microscópica (IHQ250985)
            # Captura completa: "HER2/Neu: NEGATIVO (Score 0)" → captura TODO hasta KI-67 o fin
            r'(?i)HER\s*-?\s*2\s*/\s*Neu\s*:\s*([^K]+?)(?=\s*KI-67|$)',
            # V6.0.0: PRIORIDAD 1 - DIAGNÓSTICO/Expresión molecular
            r'(?i)(?:SOBREEXPRESI[ÓO]N\s+DE\s+)?HER[^\w]*2\s*:\s*(.+?)(?:\s*\n|\.)',
            # V5.2: PATRONES MEJORADOS - Capturan TODO (score, intensidad, calificadores)
            r'(?i)sobreexpresi[oó]n\s+de\s+(?:oncog[eé]n\s+)?her[^\w]*2[:\s]*-?\s*(.+?)(?:\.|$|\n)',
            r'(?i)expresi[oó]n\s+del?\s+(?:oncog[eé]n\s+)?her[^\w]*2[:\s]*-?\s*(.+?)(?:\.|$|\n)',
            r'(?i)her[^\w]*2[:\s]*-?\s*(.+?)(?:\.|$|\n)',
            # Patrones fallback (compatibilidad con formato simple)
            r'(?i)her[^\w]*2[:\s]*(\d+\+?)',
            r'(?i)her[^\w]*2[:\s]*(positivo|negativo|equivoco)',
            r'(?i)cerb[^\w]*b[^\w]*2[:\s]*(\d+\+?|positivo|negativo)',
            r'(?i)erbb2[:\s]*(\d+\+?|positivo|negativo)',
        ],
        'valores_posibles': ['0', '1+', '2+', '3+', 'POSITIVO', 'NEGATIVO', 'EQUIVOCO'],
        'umbral_positividad': '3+',
        'usa_prioridad_seccion': True,  # V6.0.0
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'equívoco': 'EQUIVOCO',
            'equivoco': 'EQUIVOCO',
            '3+': 'POSITIVO',
            '2+': 'EQUIVOCO',
            '1+': 'NEGATIVO',
            '0': 'NEGATIVO',
        }
    },

    'KI67': {
        'nombres_alternativos': ['KI-67', 'KI 67', 'INDICE MITOTICO', 'ÍNDICE MITÓTICO'],
        'descripcion': 'Índice de proliferación celular',
        'patrones': [
            # V6.0.23: PRIORIDAD -2 - Formato narrativo linfomas "Ki67 con marcación difusa, el 90%" (IHQ251009)
            r'(?i)Ki[^\w]*67\s+con\s+marcaci[óo]n\s+(?:difusa|focal|d[ée]bil|fuerte),?\s+el\s+(\d{1,3})\s*%',
            # V6.1.4: PRIORIDAD -1.5 - Formato "El Ki-67 es del X%" (IHQ251011 - neuropatología)
            r'(?i)El\s+Ki[^\w]*67\s+es\s+del\s+(\d{1,3})\s*%',
            # V6.1.2: PRIORIDAD -1 - Formato "El índice de proliferación celular (Ki-67) es aproximadamente del X%" (IHQ250997)
            r'(?i)[ÍI]ndice\s+de\s+proliferaci[óo]n\s+c[ée]lular\s*\(Ki[^\w]*67\)\s+es\s+aproximadamente\s+del\s+(\d{1,3})\s*%',
            # V6.0.12: PRIORIDAD 0 - Formato narrativo en descripción microscópica (IHQ250985)
            # Captura: "KI-67: Tasa de proliferación celuar estimada en el 2%"
            # Nota: [la]+ acepta "celuar" (typo común) o "celular"
            r'(?i)K[I1]\s*-?\s*67\s*:\s*Tasa\s+de\s+proliferaci[óo]n\s+celu[la]+r?\s+estimada\s+en\s+el\s+(\d{1,3})\s*%',
            # V6.0.0: PRIORIDAD 1 - Formato DIAGNÓSTICO/Expresión molecular con rangos
            r'(?i)[ÍI]ndice\s+de\s+proliferaci[óo]n\s+c[ée]lular\s*(?:\()?Ki[^\w]*67(?:\))?\s*[:\s]*(\d{1,3}(?:-\d{1,3})?)\s*%',
            # V5.3.1: PRIORIDAD 2 - Capturar RANGOS primero (ej: "51-60%")
            r'(?i)ki[^\w]*67[:\s]*(\d{1,3}-\d{1,3})\s*%',  # "Ki67: 51-60%"
            r'(?i)ki[^\w]*67\s+del\s+(\d{1,3}-\d{1,3})\s*%',  # "Ki67 del 51-60%"
            # CORREGIDO v5.0.1: Patrones más específicos para evitar capturar porcentajes de otros campos
            # BUG FIX: Evitar capturar "10%" de "Diferenciación glandular = 3 (Menor del 10%)"
            r'(?i)[ÍI]ndice\s+de\s+proliferaci[óo]n\s+c[ée]lular\s+(?:medido\s+con\s+)?(?:\()?ki[^\w]*67(?:\))?\s*[:\s]*(\d{1,3})\s*%',
            r'(?i)ki[^\w]*67\s+del\s+(\d{1,3})\s*%',  # "Ki67 DEL 20%"
            r'(?i)ki[^\w]*67\s*:\s*(\d{1,3})\s*%',  # "Ki67: 20%"
            r'(?i)ki[^\w]*67\s*[:\s]+<\s*(\d{1,3})\s*%',  # "Ki67 <5%"
            r'(?i)índice\s+mitótico[:\s]*(\d{1,3})\s*%',
            r'(?i)indice\s+mitotico[:\s]*(\d{1,3})\s*%',
            # V3.2.2: NUEVOS PATRONES para casos no estándar detectados en verificación
            r'(?i)(\d{1,3})\s*%\s+ki[^\w]*67',  # "15% Ki67" (orden invertido)
            r'(?i)ki[^\w]*67\s+menor\s+(?:al|del)\s+(\d{1,3})\s*%',  # "Ki67 menor al 5%"
            r'(?i)ki[^\w]*67\s+expresi[óo]n\s+limitada',  # "Ki67 expresión limitada" → texto descriptivo
            r'(?i)ki[^\w]*67[:\s]+aproximadamente\s+(\d{1,3})\s*%',  # "Ki67: aproximadamente 5%"
        ],
        'tipo_valor': 'PERCENTAGE',
        'usa_prioridad_seccion': True,  # V6.0.0: NUEVO - Usar lógica de prioridad
        'umbrales': {
            'bajo': lambda x: x < 14,
            'intermedio': lambda x: 14 <= x <= 20,
            'alto': lambda x: x > 20,
        },
        'normalizacion': {}
    },

    'ER': {
        'nombres_alternativos': ['RECEPTORES ESTROGENOS', 'RE', 'ESTROGENO', 'ESTRÓGENO', 'R. ESTROGENOS', 'R.ESTROGENOS'],
        'descripcion': 'Receptores de estrógenos',
        'patrones': [
            # V6.1.6: FIX IHQ251007 - Patrón narrativo para casos con calificadores (moderada y fuerte)
            # DEBE IR PRIMERO para evitar que el patrón genérico línea 132 capture solo "."
            r'(?i)inmunor?r?eactividad\s+(?:moderada(?:\s+y\s+fuerte)?|fuerte)\s+(?:para|a)\s+(?:los\s+)?receptores?\s+de\s+estr[oó]geno[s]?',
            # V6.1.3: FIX IHQ250999 - Formato narrativo con intensidad ANTES de "receptor"
            r'(?i)(?:con\s+)?expresi[oó]n\s+(moderada|d[eé]bil|intensa?|fuerte)\s+de\s+(?:los\s+)?receptor[es]*\s+de\s+estr[oó]geno[s]?',
            # V6.0.17: NUEVO - Formato abreviado "R. Estrogenos" con salto de línea (IHQ250994)
            r'(?i)R\.\s*\n?\s*ESTR[ÓO]GENOS?',  # Retorna match vacío, se interpreta como POSITIVO
            # V6.0.0: PRIORIDAD 1 - DIAGNÓSTICO/Expresión molecular
            r'(?i)RECEPTORES?\s+DE\s+ESTR[ÓO]GENOS?\s*:\s*(.+?)(?:\s*\n|\.)',
            # V5.2: PATRONES MEJORADOS - Capturan CONTEXTO COMPLETO (porcentajes, intensidad, calificadores)
            # Captura hasta el punto o salto de línea para obtener TODA la información
            r'(?i)expresi[oó]n\s+de\s+receptor[es]*\s+de\s+estr[oó]geno[s]?[:\s]*-?\s*(.+?)(?:\.|$|\n)',
            r'(?i)receptor[es]*\s+de\s+estr[oó]geno[s]?[:\s]*-?\s*(.+?)(?:\.|$|\n)',
            r'(?i)\bER\b[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)\bRE\b[:\s]*(.+?)(?:\.|$|\n)',
            # Patrones fallback (compatibilidad con formato simple)
            r'(?i)(?:receptor[es]*\s+)?estr[oó]geno[s]?[:\s]*(positivo|negativo|\d+%)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE', 'EXPRESION MODERADA', 'EXPRESION DEBIL', 'EXPRESION INTENSA', 'EXPRESION FUERTE'],
        'umbral_positividad': 1,
        'usa_prioridad_seccion': True,  # V6.0.0
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
            'moderada': 'EXPRESION MODERADA',
            'débil': 'EXPRESION DEBIL',
            'debil': 'EXPRESION DEBIL',
            'intensa': 'EXPRESION INTENSA',
            'intensa': 'EXPRESION INTENSA',
            'fuerte': 'EXPRESION FUERTE',
        }
    },

    'PR': {
        'nombres_alternativos': ['RECEPTORES PROGESTERONA', 'RP', 'PROGESTERONA', 'PROGRESTERONA', 'R. PROGESTERONA', 'R.PROGESTERONA'],
        'descripcion': 'Receptores de progesterona',
        'patrones': [
            # V6.1.3: FIX IHQ250999 - Formato narrativo con intensidad ANTES de "receptor"
            r'(?i)(?:con\s+)?expresi[oó]n\s+(moderada|d[eé]bil|intensa?|fuerte)\s+de\s+(?:los\s+)?receptor[es]*\s+de\s+progr?e?sterona',
            # V6.0.17: NUEVO - Formato abreviado "R. Progesterona" con salto de línea (IHQ250994)
            r'(?i)R\.\s*\n?\s*PROGR?E?STERONA',  # Retorna match vacío, se interpreta como POSITIVO (maneja typo PROGRESTERONA)
            # V6.0.0: PRIORIDAD 1 - DIAGNÓSTICO/Expresión molecular
            r'(?i)RECEPTORES?\s+DE\s+PROGESTERONA\s*:\s*(.+?)(?:\s*\n|\.)',
            # V5.3.1: CORREGIDO - Manejar typo común "PROGRESTERONA" (sin O)
            r'(?i)receptor[es]*\s+de\s+progresterona[:\s]*-?\s*(.+?)(?:\.|$|\n)',
            # V5.2: PATRONES MEJORADOS - Capturan CONTEXTO COMPLETO (porcentajes, intensidad, calificadores)
            r'(?i)expresi[oó]n\s+de\s+receptor[es]*\s+de\s+progesterona[:\s]*-?\s*(.+?)(?:\.|$|\n)',
            r'(?i)receptor[es]*\s+de\s+progesterona[:\s]*-?\s*(.+?)(?:\.|$|\n)',
            r'(?i)\bRP\b[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)\bPR\b[:\s]*(.+?)(?:\.|$|\n)',
            # Patrones fallback (compatibilidad con formato simple)
            r'(?i)(?:receptor[es]*\s+)?progr[e]?sterona[:\s]*(positivo|negativo|\d+%)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE', 'EXPRESION MODERADA', 'EXPRESION DEBIL', 'EXPRESION INTENSA', 'EXPRESION FUERTE'],
        'umbral_positividad': 1,
        'usa_prioridad_seccion': True,  # V6.0.0
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
            'moderada': 'EXPRESION MODERADA',
            'débil': 'EXPRESION DEBIL',
            'debil': 'EXPRESION DEBIL',
            'intensa': 'EXPRESION INTENSA',
            'intensa': 'EXPRESION INTENSA',
            'fuerte': 'EXPRESION FUERTE',
        }
    },

    'PDL1': {
        'nombres_alternativos': ['PD-L1', 'PD L1', 'PDL-1', 'PD-1'],
        'descripcion': 'Ligando de muerte programada 1',
        'patrones': [
            r'(?i)pd[^\w]*l1[:\s]*(\d{1,3})%?',
            r'(?i)pd[^\w]*l1[:\s]*(positivo|negativo)',
            r'(?i)pd[^\w]*1[:\s]*(\d{1,3})%?',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'umbral_positividad': 1,
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'P16': {
        'nombres_alternativos': ['P-16', 'P 16'],
        'descripcion': 'Proteína p16',
        'patrones': [
            # V6.1.3: PRIORIDAD 0 - Patrón para "POSITIVO PARA SOBREEXPRESIÓN DE P16" (IHQ251010)
            r'(?i)POSITIVO\s+(?:PARRA|PARA)\s+SOBREEXPRESI[ÓO]N\s+DE\s+P16',
            # V6.1.3: PRIORIDAD 1 - Patrón para "sobreexpresión en bloque para p16" (IHQ251010)
            r'(?i)sobreexpresi[óo]n\s+en\s+bloque\s+para\s+p16',
            # V6.1.3: PRIORIDAD 2 - Patrón para "presenta sobreexpresión...para P16" (IHQ251010)
            r'(?i)presenta\s+sobreexpresi[óo]n.*?para\s+p16',
            # V5.2: Captura calificadores como "en bloque", "difuso", "focal"
            r'(?i)p16[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)p[^\w]*16[:\s]*(.+?)(?:\.|$|\n)',
            # Fallback
            r'(?i)p16[:\s]*(positivo|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
            'sobreexpresion': 'POSITIVO',
            'sobreexpresión': 'POSITIVO',
        }
    },

    'P40': {
        'nombres_alternativos': ['P-40', 'P 40'],
        'descripcion': 'Proteína p40',
        'patrones': [
            # V6.0.12: PRIORIDAD 0 - Formato narrativo "marcación positiva para: p40" (IHQ250991)
            r'(?i)marcaci[óo]n\s+positiva\s+para[:\s]+.*?[pP][\s-]?40(?:\s|,|\.)',
            r'(?i)positiv[ao]s?\s+para[:\s]+.*?[pP][\s-]?40(?:\s|,|\.)',
            r'(?i)negativ[ao]s?\s+para[:\s]+.*?[pP][\s-]?40(?:\s|,|\.)',
            # V6.0.10: Patrones específicos que evitan captura de basura (IHQ250983)
            # PRIORIDAD 1: Estado + modificador
            r'(?i)p[^\w]*40[:\s]+(positiv[oa]\s+(?:heterog[eé]neo|focal|difuso))',
            r'(?i)p[^\w]*40[:\s]+(negativ[oa]\s+(?:heterog[eé]neo|focal|difuso))',
            # PRIORIDAD 2: Solo modificador (implica positivo)
            r'(?i)p[^\w]*40\s+(heterog[eé]neo|focal|difuso)',
            # PRIORIDAD 3: Estado sin modificador
            r'(?i)p[^\w]*40[:\s]+(positiv[oa]|negativ[oa])',
            # PRIORIDAD 4: Símbolos
            r'(?i)p[^\w]*40[:\s]*(\+|\-)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'POSITIVO HETEROGÉNEO', 'NEGATIVO FOCAL', 'POSITIVO FOCAL', 'POSITIVO DIFUSO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'positivo heterogeneo': 'POSITIVO HETEROGÉNEO',
            'positivo heterogéneo': 'POSITIVO HETEROGÉNEO',
            'negativo heterogeneo': 'NEGATIVO HETEROGÉNEO',
            'negativo heterogéneo': 'NEGATIVO HETEROGÉNEO',
            'positivo focal': 'POSITIVO FOCAL',
            'negativo focal': 'NEGATIVO FOCAL',
            'positivo difuso': 'POSITIVO DIFUSO',
            'negativo difuso': 'NEGATIVO DIFUSO',
            'heterogeneo': 'POSITIVO HETEROGÉNEO',
            'heterogéneo': 'POSITIVO HETEROGÉNEO',
            'focal': 'POSITIVO FOCAL',
            'difuso': 'POSITIVO DIFUSO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
        }
    },

    # V6.1.2: Biomarcadores IHQ250997 (tumor maligno indiferenciado)
    'DOG1': {
        'nombres_alternativos': ['DOG-1', 'DOG 1'],
        'descripcion': 'Discovered on GIST-1 (marcador de tumor estromal gastrointestinal)',
        'patrones': [
            r'(?i)DOG[^\w]*1[:\s]+(positiv[oa]|negativ[oa])',
            r'(?i)DOG[^\w]*1[:\s]*(\+|\-)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'POSITIVO FOCAL', 'NEGATIVO FOCAL'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
            'focal': 'POSITIVO FOCAL',
        }
    },

    'H_CALDESMON': {
        'nombres_alternativos': ['H-CALDESMON', 'H CALDESMON', 'HCALDESMON', 'H-CALDESMÓN', 'CALDESMON'],
        'descripcion': 'H-Caldesmon (marcador de diferenciación de músculo liso)',
        'patrones': [
            r'(?i)H[^\w]*CALDESM[ÓO]N[:\s]+(positiv[oa]|negativ[oa])',
            r'(?i)H[^\w]*CALDESM[ÓO]N[:\s]*(\+|\-)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'POSITIVO FOCAL', 'NEGATIVO FOCAL'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
            'focal': 'POSITIVO FOCAL',
        }
    },

    'AML': {
        'nombres_alternativos': ['ACTINA DE MÚSCULO LISO', 'ACTINA DE MUSCULO LISO', 'ACTINA MÚSCULO LISO', 'ACTINA MUSCULO LISO', 'SMA'],
        'descripcion': 'Actina de músculo liso (Smooth Muscle Actin)',
        'patrones': [
            r'(?i)(?:ACTINA\s+DE\s+M[ÚU]SCULO\s+LISO|AML|SMA)[:\s]+(positiv[oa]|negativ[oa])',
            r'(?i)(?:ACTINA\s+DE\s+M[ÚU]SCULO\s+LISO|AML|SMA)[:\s]*(\+|\-)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'POSITIVO FOCAL', 'NEGATIVO FOCAL'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
            'focal': 'POSITIVO FOCAL',
        }
    },

    'P53': {
        'nombres_alternativos': ['P-53', 'P 53'],
        'descripcion': 'Proteína supresora tumoral p53',
        'patrones': [
            # V6.1.5: PRIORIDAD -1 - "expresión para p53 no es contributiva" (IHQ251011 - neuropatología)
            # Captura el "no es" DENTRO del grupo para incluir la negación
            r'(?i)(?:la\s+)?expresi[óo]n\s+para\s+p53\s+((?:no\s+)?es\s+.+?)(?:\.|,|$)',
            # V6.0.12: PRIORIDAD 0 - "sobreexpresión de p53" (IHQ250988)
            r'(?i)sobreexpresi[óo]n\s+de\s+p53',
            # V5.2: Captura "con sobreexpresión", porcentajes, intensidad
            r'(?i)p53[:\s]*([^.]+?)(?:\.|$|\n)',  # Modificado: [^.] evita capturar solo el punto
            r'(?i)p[^\w]*53[:\s]*([^.]+?)(?:\.|$|\n)',
            # Fallback
            r'(?i)p53[:\s]*(positivo|negativo|\d+%)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE', 'SOBREEXPRESIÓN', 'NO CONTRIBUTIVA', 'NO CONTRIBUTIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sobreexpresión': 'POSITIVO (SOBREEXPRESIÓN)',  # V6.0.12
            'no es contributiva': 'NO CONTRIBUTIVA',  # V6.1.4
            'no contributiva': 'NO CONTRIBUTIVA',
            'no contributivo': 'NO CONTRIBUTIVO',
        }
    },

    'CDX2': {
        'nombres_alternativos': ['CDX-2', 'CDX 2'],
        'descripcion': 'Factor de transcripción CDX2',
        'patrones': [
            # V6.0.15: PRIORIDAD 0 - "sin marcación para CDX2" (IHQ250987)
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*CDX\s*2(?:\s|,|\.)',
            r'(?i)cdx2[:\s]*(positivo|negativo)',
            r'(?i)cdx[^\w]*2[:\s]*(positivo|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',  # V6.0.15
        }
    },

    'CK7': {
        'nombres_alternativos': ['CK-7', 'CK 7', 'CITOKERATINA 7', 'CYTOKERATIN 7'],
        'descripcion': 'Citoqueratina 7 - Marcador epitelial',
        'patrones': [
            r'(?i)ck[^\w]*7[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+ck[^\w]*7.*?(positiva|positivo)',
            r'(?i)negativas?\s+para\s+ck[^\w]*7.*?(negativa|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'CK19': {
        'nombres_alternativos': ['CK-19', 'CK 19', 'CITOKERATINA 19', 'CYTOKERATIN 19'],
        'descripcion': 'Citoqueratina 19 - Marcador de carcinomas (tiroides, mama)',
        'patrones': [
            # V6.0.15: Agregado para IHQ250987 (carcinoma metastásico de tiroides)
            # PRIORIDAD 0: Listas tipo "positivas para CK7, CK19 y TTF1"
            r'(?i)positivas?\s+para\s+[^.]*?ck[^\w]*19(?:\s+y|\s*,|\s*\.)',
            r'(?i)negativas?\s+para\s+[^.]*?ck[^\w]*19(?:\s+y|\s*,|\s*\.)',
            r'(?i)sin\s+marcaci[óo]n\s+para\s+[^.]*?CK\s*19(?:\s+y|\s*,|\s*\.)',
            # Patrones simples
            r'(?i)ck[^\w]*19[:\s]*(positivo|negativo|positiva|negativa)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',
        }
    },

    'CK20': {
        'nombres_alternativos': ['CK-20', 'CK 20', 'CITOKERATINA 20', 'CYTOKERATIN 20'],
        'descripcion': 'Citoqueratina 20 - Marcador epitelial',
        'patrones': [
            r'(?i)ck[^\w]*20[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+ck[^\w]*20.*?(positiva|positivo)',
            r'(?i)negativas?\s+para\s+ck[^\w]*20.*?(negativa|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'EMA': {
        'nombres_alternativos': ['E.M.A', 'EPITHELIAL MEMBRANE ANTIGEN'],
        'descripcion': 'Antígeno de membrana epitelial',
        'patrones': [
            r'(?i)ema[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+.*?ema(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?ema(?:\s|,|$)',
            r'(?i)positivas?\s+para\s+[\w\s]*?\s+y\s+ema(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'GATA3': {
        'nombres_alternativos': ['GATA-3', 'GATA 3'],
        'descripcion': 'Factor de transcripción GATA3',
        'patrones': [
            r'(?i)gata[^\w]*3[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+.*?gata\s*3(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?gata\s*3(?:\s|,|$)',
            r'(?i)positivas?\s+para\s+[\w\s]*?\s+y\s+gata\s*3(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'GFAP': {
        'nombres_alternativos': ['G FAP', 'G-FAP'],
        'descripcion': 'Proteína ácida fibrilar glial (Glial Fibrillary Acidic Protein)',
        'patrones': [
            r'(?i)gfap[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+.*?gfap(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?gfap(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'IDH1': {
        'nombres_alternativos': ['IDH-1', 'IDH 1', 'ISOCITRATO DESHIDROGENASA'],
        'descripcion': 'Isocitrato Deshidrogenasa 1 - Marcador de gliomas',
        'patrones': [
            # V6.1.5: PRIORIDAD 0 - "expresión para IDH1 es positiva (mutado)" (IHQ251011)
            r'(?i)(?:la\s+)?(?:expre+si?[óo]n|expresi[óo]n)\s+para\s+idh[^\w]*1\s+(?:es\s+)?(positiva?|negativa?)\s*(?:\(mutado\))?',
            # Patrones generales
            r'(?i)idh[^\w]*1[:\s]*(positivo|negativo|mutado)',
            r'(?i)positivas?\s+para\s+.*?idh[^\w]*1(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?idh[^\w]*1(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'MUTADO', 'POSITIVO (MUTADO)', 'NEGATIVO (WILD TYPE)'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO (MUTADO)',  # En neuropatología, positivo = mutado
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
            'mutado': 'POSITIVO (MUTADO)',
        }
    },

    'ATRX': {
        'nombres_alternativos': ['ALPHA THALASSEMIA'],
        'descripcion': 'ATRX - Marcador de astrocitomas IDH-mutados',
        'patrones': [
            # V6.1.5: PRIORIDAD 0 - "Ausencia de expresión para ATRX (mutado)" (IHQ251011)
            r'(?i)(?:ausencia|p[eé]rdida)\s+de\s+expresi[óo]n\s+para\s+atrx\s*(?:\(mutado\))?',
            # Patrones generales
            r'(?i)atrx[:\s]*(positivo|negativo|mutado|ausencia)',
            r'(?i)positivas?\s+para\s+.*?atrx(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?atrx(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'AUSENCIA DE EXPRESIÓN', 'NEGATIVO (MUTADO)'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO (MUTADO)',  # En neuropatología, ausencia = negativo = mutado
            'negativa': 'NEGATIVO (MUTADO)',
            'ausencia': 'NEGATIVO (MUTADO)',
            'mutado': 'NEGATIVO (MUTADO)',
        }
    },

    'SOX10': {
        'nombres_alternativos': ['SOX-10', 'SOX 10', 'SOXIO'],
        'descripcion': 'Factor de transcripción SOX10',
        'patrones': [
            r'(?i)sox[^\w]*10[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+.*?sox\s*(?:10|io)(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?sox\s*(?:10|io)(?:\s|,|$)',
            r'(?i)sox\s*(?:10|io)\s+y\s+[\w\s]*?(negativ|positiv)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'E_CADHERINA': {
        'nombres_alternativos': ['E-CADHERINA', 'E CADHERINA', 'ECADHERINA', 'E-CAD', 'CADHERINA E'],
        'descripcion': 'E-Cadherina - Molécula de adhesión celular (diferencial lobulillar vs ductal)',
        'patrones': [
            # V6.0.2: MEJORADO - Patrones más robustos para E-Cadherina (IHQ250981)
            r'(?i)E[\s-]?CADHERINA\s*:\s*(POSITIV[OA]S?|NEGATIV[OA]S?)',
            r'(?i)marcaci[óo]n\s+(positiva|negativa)\s+para[:\s-]+E[\s-]?CADHERINA',
            r'(?i)E[\s-]?CADHERINA\s+con\s+marcaci[óo]n\s+\w+\s+(positiva|negativa)',  # "E-CADHERINA con marcación membranosa positiva"
            r'(?i)E[\s-]?CADHERINA\s*\+',  # "E-Cadherina +"
            r'(?i)E[\s-]?CADHERINA\s*-(?!\s*\d)',  # "E-Cadherina -" (negative lookahead para evitar "E-Cadherina-2")
            r'(?i)E[\s-]?CADHERINA\s*:\s*(.+?)(?:\s*\n|\.)',  # Patrón genérico (fallback)
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'usa_prioridad_seccion': True,
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
            'presente': 'POSITIVO',
            'ausente': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
            'pos': 'POSITIVO',
            'neg': 'NEGATIVO',
        }
    },

    'TTF1': {
        'nombres_alternativos': ['TTF-1', 'TTF 1', 'THYROID TRANSCRIPTION FACTOR 1'],
        'descripcion': 'Factor de transcripción tiroideo 1',
        'patrones': [
            r'(?i)ttf[^\w]*1[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+.*?ttf\s*1(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?ttf\s*1(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
            'neg': 'NEGATIVO',
            'pos': 'POSITIVO',
        }
    },

    'S100': {
        'nombres_alternativos': ['S-100', 'S 100'],
        'descripcion': 'Proteína S100',
        'patrones': [
            r'(?i)s[^\w]*100[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+.*?s\s*100(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?s\s*100(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'VIMENTINA': {
        'nombres_alternativos': ['VIMENTIN'],
        'descripcion': 'Vimentina',
        'patrones': [
            r'(?i)vimentin[a]?[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+.*?vimentin[a]?(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?vimentin[a]?(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
            'neg': 'NEGATIVO',
            'pos': 'POSITIVO',
        }
    },

    'BER_EP4': {
        'nombres_alternativos': ['BER-EP4', 'BER EP4', 'BERRP4', 'EBERP4', 'BerEP4', 'Ber-EP4', 'EP-CAM', 'EPCAM', 'Ep-CAM'],
        'descripcion': 'Antígeno epitelial BER-EP4 / Ep-CAM - Marcador de células epiteliales',
        'patrones': [
            r'(?i)(?:EBERP4|BER[\s-]?EP4|Ep[\s-]?CAM)[\s/]*(?:Ep[\s-]?CAM)?[:\s]*(positiv[ao]s?|negativ[ao]s?)',
            r'(?i)marcaci[óo]n\s+positiva\s+para[:\s]+.*?(?:EBERP4|BER[\s-]?EP4)',
            r'(?i)positiv[ao]s?\s+para[:\s]+.*?(?:EBERP4|BER[\s-]?EP4)',
            r'(?i)(?:BER[\s-]?EP4|BERRP4|EBERP4)[:\s]*(positiv[ao]s?|negativ[ao]s?)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'positivos': 'POSITIVO',
            'positivas': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'BCL2': {
        'nombres_alternativos': ['BCL-2', 'BCL 2'],
        'descripcion': 'Proteína anti-apoptótica BCL2',
        'patrones': [
            r'(?i)marcaci[óo]n\s+positiva\s+para[:\s]+.*?BCL[\s-]?2',
            r'(?i)positiv[ao]s?\s+para[:\s]+.*?BCL[\s-]?2',
            r'(?i)BCL[\s-]?2[:\s]*(positiv[ao]s?|negativ[ao]s?)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'positivos': 'POSITIVO',
            'positivas': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'P63': {
        'nombres_alternativos': ['P-63', 'P 63'],
        'descripcion': 'Proteína p63 - Marcador de células basales/mioepiteliales',
        'patrones': [
            # V6.2.1: PRIORIDAD 0 - FIX IHQ251012: Captura en listas con "y" (CKAE1E3 y p63)
            # Formato: "positivas para [BIOMARCADOR] y p63" → captura "positivas"
            r'(?i)(positiv[ao]s?|negativ[ao]s?)\s+para\s+[A-Z0-9/\-]+\s+y\s+[pP][\s-]?63(?:\s|,|\.)',
            # V6.1.3: PRIORIDAD 1 - Formato narrativo general "positivas para P63"
            r'(?i)(positiv[ao]s?|negativ[ao]s?)\s+para[:\s]+.*?[pP][\s-]?63(?:\s|,|\.)',
            # Formato "marcación positiva para: p63" → captura "positiva"
            r'(?i)marcaci[óo]n\s+(positiva|negativa)\s+para[:\s]+.*?[pP][\s-]?63(?:\s|,|\.)',
            # Formato directo "p63: positivo" → captura "positivo"
            r'(?i)[pP][\s-]?63[:\s]*(positiv[ao]s?|negativ[ao]s?)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'positivos': 'POSITIVO',
            'positivas': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'CK5_6': {
        'nombres_alternativos': ['CK5/6', 'CK5/5', 'CK55', 'CK5 / 6', 'CK5 6', 'CK56', 'CK 5/6', 'CK 5 / 6'],
        'descripcion': 'Citoqueratina 5/6 - Marcador de células basales/mioepiteliales (IHQ250999)',
        'patrones': [
            # V6.1.3: Biomarcadores celulas mioepiteliales (IHQ250999)
            # Formato narrativo "positivas para ... CK5/6"
            r'(?i)(positiv[ao]s?|negativ[ao]s?)\s+para[:\s]+.*?CK5[\s/\-]?6(?:\s|,|\.)',
            # Formato "CK5/6: positivo"
            r'(?i)CK5[\s/\-]?6[:\s]*(positiv[ao]s?|negativ[ao]s?)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'positivos': 'POSITIVO',
            'positivas': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'CALPONINA': {
        'nombres_alternativos': [],
        'descripcion': 'Calponina - Marcador de células musculares lisas/mioepiteliales (IHQ250999)',
        'patrones': [
            # V6.1.3: Biomarcadores celulas mioepiteliales (IHQ250999)
            # Formato narrativo "positivas para ... calponina"
            r'(?i)(positiv[ao]s?|negativ[ao]s?)\s+para[:\s]+.*?calponina(?:\s|,|\.)',
            # Formato "calponina: positivo"
            r'(?i)calponina[:\s]*(positiv[ao]s?|negativ[ao]s?)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'positivos': 'POSITIVO',
            'positivas': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'RACEMASA': {
        'nombres_alternativos': ['RACEMASE', 'P504S', 'AMACR', 'ALPHA-METHYLACYL-COA RACEMASE'],
        'descripcion': 'Alfa-metilacil-CoA racemasa - Marcador de cáncer de próstata',
        'patrones': [
            # V6.1.1: FIX IHQ250995 - Biomarcador de próstata
            # Formato narrativo "marcación positiva para Racemasa"
            r'(?i)marcaci[óo]n\s+positiva\s+para[:\s]+.*?[Rr]acemas[ae](?:\s|,|\.)',
            r'(?i)marcaci[óo]n\s+negativa\s+para[:\s]+.*?[Rr]acemas[ae](?:\s|,|\.)',
            r'(?i)positiv[ao]s?\s+para[:\s]+.*?[Rr]acemas[ae](?:\s|,|\.)',
            r'(?i)negativ[ao]s?\s+para[:\s]+.*?[Rr]acemas[ae](?:\s|,|\.)',
            # Formato directo "racemasa: positivo" o "P504S: positivo"
            r'(?i)[Rr]acemas[ae][:\s]*(positiv[ao]s?|negativ[ao]s?)',
            r'(?i)P504S[:\s]*(positiv[ao]s?|negativ[ao]s?)',
            r'(?i)AMACR[:\s]*(positiv[ao]s?|negativ[ao]s?)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'positivos': 'POSITIVO',
            'positivas': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'CHROMOGRANINA': {
        'nombres_alternativos': ['CHROMOGRANIN', 'CROMOGRANINA', 'CHROMOGRANIN A'],
        'descripcion': 'Cromogranina A',
        'patrones': [
            r'(?i)(?:chrom|crom)ogranin[a]?[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+.*?(?:chrom|crom)ogranin[a]?(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?(?:chrom|crom)ogranin[a]?(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
            'pos': 'POSITIVO',
        }
    },

    'SYNAPTOPHYSIN': {
        'nombres_alternativos': ['SINAPTOFISINA', 'SYNAPTOPHYSINA'],
        'descripcion': 'Sinaptofisina',
        'patrones': [
            r'(?i)s[iy]naptofis[i]?n[a]?[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+.*?s[iy]naptofis[i]?n[a]?(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?s[iy]naptofis[i]?n[a]?(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'MELAN_A': {
        'nombres_alternativos': ['MELAN-A', 'MELAN A', 'MELANA', 'MART-1'],
        'descripcion': 'Melan-A / MART-1',
        'patrones': [
            r'(?i)melan[^\w]*a[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)mart[^\w]*1[:\s]*(positivo|negativo|positiva|negativa)',
            r'(?i)positivas?\s+para\s+.*?melan[^\w]*a(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?melan[^\w]*a(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
            'neg': 'NEGATIVO',
        }
    },

    # V5.2: BIOMARCADORES FALTANTES identificados en análisis de casos IHQ250022, etc.
    'WT1': {
        'nombres_alternativos': ['WT-1', 'WT 1', 'WILMS TUMOR 1'],
        'descripcion': 'Tumor de Wilms 1',
        'patrones': [
            r'(?i)wt1[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)wt[^\w]*1[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)positivas?\s+para\s+.*?wt\s*1(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?wt\s*1(?:\s|,|$)',
            # Fallback
            r'(?i)wt1[:\s]*(positivo|negativo|positiva|negativa)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'PAX5': {
        'nombres_alternativos': ['PAX-5', 'PAX 5'],
        'descripcion': 'Factor de transcripción PAX5 (marcador de células B)',
        'patrones': [
            # V6.0.25: Patrón para "linfocitos positivos para CD20 y PAX5" (IHQ251009)
            r'(?i)linfocitos\s+positivos\s+para\s+(?:CD\s*20\s+y\s+)?PAX\s*5',
            r'(?i)positivos\s+para\s+(?:[A-Z0-9]+\s+y\s+)?PAX\s*5',
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*PAX\s*5(?:\s|,|\.)',
            r'(?i)pax[^\w]*5[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?pax\s*5(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?pax\s*5(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',
        }
    },

    'PAX8': {
        'nombres_alternativos': ['PAX-8', 'PAX 8'],
        'descripcion': 'Factor de transcripción PAX8',
        'patrones': [
            r'(?i)pax[^\w]*8[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)pax\s*8[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)positivas?\s+para\s+.*?pax\s*8(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?pax\s*8(?:\s|,|$)',
            # Fallback
            r'(?i)pax[^\w]*8[:\s]*(positivo|negativo|positiva|negativa)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    'NAPSIN': {
        'nombres_alternativos': ['NAPSIN-A', 'NAPSIN A', 'NAPSINA', 'NAPSINA A'],
        'descripcion': 'Napsina A',
        'patrones': [
            r'(?i)napsin[a]?(?:\s*a)?[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)positivas?\s+para\s+.*?napsin[a]?(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?napsin[a]?(?:\s|,|$)',
            # Fallback
            r'(?i)napsin[a]?[:\s]*(positivo|negativo|positiva|negativa)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    # Marcadores CD
    'CD2': {
        'nombres_alternativos': ['CD-2'],
        'descripcion': 'Cluster de diferenciación 2 (marcador de linfocitos T)',
        'patrones': [
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*CD\s*2(?:\s|,|\.)',
            r'(?i)cd[^\w]*2[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?cd\s*2(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*2(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',
        }
    },

    'CD3': {
        'nombres_alternativos': ['CD-3'],
        'descripcion': 'Cluster de diferenciación 3',
        'patrones': [
            # V6.2.1: PRIORIDAD 0 - Formato narrativo "timocitos son positivos para CD1a, CD3..." (IHQ251012)
            r'(?i)timocitos\s+son\s+(positiv[ao]s?|negativ[ao]s?)\s+para\s+[A-Z0-9,\s]*CD\s*3(?:\s|,|\.|\sy)',
            # V6.0.12: PRIORIDAD 1 - "sin marcación para CD2, CD3, CD5..." (IHQ250988)
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*CD\s*3(?:\s|,|\.)',
            # V6.0.13: ELIMINADO \d+%? - CD3 solo POSITIVO/NEGATIVO (no porcentaje)
            r'(?i)cd[^\w]*3[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?cd\s*3(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*3(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',  # V6.0.12
        }
    },

    'CD4': {
        'nombres_alternativos': ['CD-4'],
        'descripcion': 'Cluster de diferenciación 4 (linfocitos T helper)',
        'patrones': [
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*CD\s*4(?:\s|,|\.)',
            r'(?i)cd[^\w]*4[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?cd\s*4(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*4(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',
        }
    },

    'CD5': {
        'nombres_alternativos': ['CD-5'],
        'descripcion': 'Cluster de diferenciación 5',
        'patrones': [
            # V6.2.1: PRIORIDAD -1 - Formato narrativo "timocitos son positivos para CD1a, CD3 y CD5" (IHQ251012)
            r'(?i)timocitos\s+son\s+(positiv[ao]s?|negativ[ao]s?)\s+para\s+[A-Z0-9,\s]*(?:y\s+)?CD\s*5(?!6)(?:\s|,|\.)',
            # V6.0.12: PRIORIDAD 0 - "sin marcación para CD2, CD3, CD5..." (IHQ250988)
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*CD\s*5(?:\s|,|\.)',
            # V6.2.1: PRIORIDAD 1 - Evitar confusión con CD56 usando límites de palabra estrictos
            r'(?i)cd[^\w]*5(?!6)[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?cd\s*5(?!6)(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*5(?!6)(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',  # V6.0.12
        }
    },

    'CD8': {
        'nombres_alternativos': ['CD-8'],
        'descripcion': 'Cluster de diferenciación 8 (linfocitos T citotóxicos)',
        'patrones': [
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*CD\s*8(?:\s|,|\.)',
            r'(?i)cd[^\w]*8[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?cd\s*8(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*8(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',
        }
    },

    'CD10': {
        'nombres_alternativos': ['CD-10'],
        'descripcion': 'Cluster de diferenciación 10',
        'patrones': [
            r'(?i)cd[^\w]*10[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*10(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*10(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'CD15': {
        'nombres_alternativos': ['CD-15'],
        'descripcion': 'Cluster de diferenciación 15 (Linfoma de Hodgkin)',
        'patrones': [
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*CD\s*15(?:\s|,|\.)',
            r'(?i)cd[^\w]*15[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?cd\s*15(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*15(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',
        }
    },

    'CD20': {
        'nombres_alternativos': ['CD-20'],
        'descripcion': 'Cluster de diferenciación 20 (marcador de células B)',
        'patrones': [
            # V6.2.1: PRIORIDAD -1 - Formato "expresión aberrante para CD20" (IHQ251012)
            # Captura solo "aberrante" para normalizar correctamente
            r'(?i)(?:focos\s+de\s+)?expresi[óo]n\s+(aberrante)\s+para\s+CD\s*20',
            # V6.0.13: PRIORIDAD 0 - Formato "CD20+" → POSITIVO (IHQ250989)
            r'(?i)linfocitos\s+B\s*\(CD\s*20\s*\+\)',
            r'(?i)cd\s*20\s*\+',
            # V6.0.12: PRIORIDAD 1 - "sin marcación para CD2, CD3, CD5..." (IHQ250988)
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*CD\s*20(?:\s|,|\.)',
            # Patrones existentes
            r'(?i)cd[^\w]*20[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*20(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*20(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE', 'POSITIVO (aberrante)'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            'aberrante': 'POSITIVO (aberrante)',
        }
    },

    'CD23': {
        'nombres_alternativos': ['CD-23'],
        'descripcion': 'Cluster de diferenciación 23 (marcador de linfomas)',
        'patrones': [
            # V6.0.25: Patrón para "positividad fuerte para CD23" (IHQ251009)
            r'(?i)positividad\s+(?:fuerte|débil|moderada|leve)\s+para\s+CD\s*23',
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*CD\s*23(?:\s|,|\.)',
            r'(?i)cd[^\w]*23[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?cd\s*23(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*23(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'positividad fuerte': 'POSITIVO',
            'positividad débil': 'POSITIVO',
            'sin marcación': 'NEGATIVO',
        }
    },

    'CD30': {
        'nombres_alternativos': ['CD-30'],
        'descripcion': 'Cluster de diferenciación 30',
        'patrones': [
            r'(?i)cd[^\w]*30[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*30(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*30(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'CD34': {
        'nombres_alternativos': ['CD-34'],
        'descripcion': 'Cluster de diferenciación 34',
        'patrones': [
            r'(?i)cd[^\w]*34[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*34(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*34(?:\s|,|$)',
        
            # V6.2.2: Formato con símbolo separado: 'CD34 +' o 'CD34 -' (IHQ251014)
            r'(?i)cd\s*34\s+(\+)',
            r'(?i)cd\s*34\s+(-)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
        }
    },

    # V6.1.4: Biomarcadores hepáticos (IHQ251000)
    'HEPATOCITO': {
        'nombres_alternativos': ['HEPATOCYTE'],
        'descripcion': 'Marcador de células hepáticas',
        'patrones': [
            r'(?i)hepatocito[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+hepatocito',
            r'(?i)negativas?\s+para\s+hepatocito',
            r'(?i)marcaci[óo]n\s+(?:usual\s+)?para\s+hepatocito',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'ARGINASA': {
        'nombres_alternativos': ['ARGINASE', 'ARG1'],
        'descripcion': 'Enzima marcador hepático',
        'patrones': [
            r'(?i)arginasa[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+arginasa',
            r'(?i)negativas?\s+para\s+arginasa',
            r'(?i)marcaci[óo]n\s+(?:usual\s+)?para\s+arginasa',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'CD38': {
        'nombres_alternativos': ['CD-38'],
        'descripcion': 'Cluster de diferenciación 38',
        'patrones': [
            # V6.0.12: "expresión de CD38" → POSITIVO (IHQ250992)
            r'(?i)expresi[óo]n\s+de\s+cd\s*38',
            r'(?i)cd[^\w]*38[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)cd\s*38\s*\+',  # CD38+
            r'(?i)positivas?\s+para\s+.*?cd\s*38(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*38(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
        }
    },

    'CD45': {
        'nombres_alternativos': ['CD-45'],
        'descripcion': 'Cluster de diferenciación 45',
        'patrones': [
            r'(?i)cd[^\w]*45[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*45(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*45(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'CD56': {
        'nombres_alternativos': ['CD-56'],
        'descripcion': 'Cluster de diferenciación 56',
        'patrones': [
            # V6.0.12: "expresión aberrante para CD56" → POSITIVO ABERRANTE (IHQ250992)
            r'(?i)expresi[óo]n\s+aberrante\s+para\s+cd\s*56',
            r'(?i)cd[^\w]*56[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*56(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*56(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE', 'POSITIVO ABERRANTE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'aberrante': 'POSITIVO ABERRANTE',
        }
    },

    'CD61': {
        'nombres_alternativos': ['CD-61'],
        'descripcion': 'Cluster de diferenciación 61',
        'patrones': [
            r'(?i)cd[^\w]*61[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*61(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*61(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'CD68': {
        'nombres_alternativos': ['CD-68'],
        'descripcion': 'Cluster de diferenciación 68',
        'patrones': [
            # V6.2.1: PRIORIDAD 0 - "CD68+" con detalles de expresión (IHQ251002)
            r'(?i)cd\s*68\s*\+.*?(?:presenta\s+)?expresi[óo]n\s+(\w+)\s+(\w+)\s+y?\s+(\w+)',
            r'(?i)cd\s*68\s*\+',
            # Patrones existentes
            r'(?i)cd[^\w]*68[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*68(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*68(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'CD117': {
        'nombres_alternativos': ['CD-117', 'C-KIT'],
        'descripcion': 'Cluster de diferenciación 117 (c-KIT)',
        'patrones': [
            # V6.2.1: PRIORIDAD -1 - Formato "Sin expresión para CD117" (IHQ251012)
            # Captura solo "sin expresión" para normalizar correctamente
            r'(?i)(sin\s+expresi[óo]n)\s+para\s+cd\s*117',
            # V6.0.12: PRIORIDAD 0 - "expresión débil para CD117" → POSITIVO DÉBIL (IHQ250992)
            r'(?i)expresi[óo]n\s+(d[ée]bil|debil)\s+para\s+cd\s*117',
            # Patrones estándar
            r'(?i)cd[^\w]*117[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)c[^\w]*kit[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?cd\s*117(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*117(?:\s|,|$)',
        
            # V6.2.2: Formato con símbolo separado: 'CD117 +' o 'CD117 -' (IHQ251014)
            r'(?i)cd\s*117\s+(\+)',
            r'(?i)cd\s*117\s+(-)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE', 'POSITIVO DÉBIL'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin expresión': 'NEGATIVO',
            'sin expresion': 'NEGATIVO',
            'débil': 'POSITIVO DÉBIL',
            'debil': 'POSITIVO DÉBIL',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
        }
    },

    'CD138': {
        'nombres_alternativos': ['CD-138', 'SYNDECAN-1', 'CD38'],
        'descripcion': 'Cluster de diferenciación 138 (marcador de células plasmáticas)',
        'patrones': [
            # V6.0.13: Formato "CD38+" o "CD138+" → POSITIVO (IHQ250989)
            r'(?i)cd\s*38\s*\+',
            r'(?i)cd\s*138\s*\+',
            # V6.0.12: "expresión de CD138" → POSITIVO (IHQ250992)
            r'(?i)expresi[óo]n\s+de\s+cd\s*138',
            r'(?i)expresi[óo]n\s+de\s+.*?\s+cd\s*138',
            # Formatos estándar
            r'(?i)cd[^\w]*138[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)cd[^\w]*38[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)syndecan[^\w]*1[:\s]*(positivo|negativo)',
            # Formatos narrativos
            r'(?i)células\s+plasmáticas\s*\(cd\s*38\s*\+\)',
            r'(?i)positivas?\s+para\s+.*?cd\s*138(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*138(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
        }
    },

    # V6.2.1: NUEVO - Biomarcadores específicos de timomas (IHQ251012)
    'CD1A': {
        'nombres_alternativos': ['CD-1A', 'CD1a', 'CD 1A', 'CD 1a'],
        'descripcion': 'Cluster de diferenciación 1A (marcador de timocitos corticales)',
        'patrones': [
            # V6.2.1: Formato narrativo "timocitos son positivos para CD1a, CD3..."
            r'(?i)timocitos\s+son\s+(positiv[ao]s?|negativ[ao]s?)\s+para\s+[A-Z0-9,\s]*CD1[aA]',
            # Formato "positivos para CD1a"
            r'(?i)(positiv[ao]s?|negativ[ao]s?)\s+para\s+.*?CD1[aA](?:\s|,|\.)',
            # Formato directo "CD1a: positivo"
            r'(?i)CD1[aA][:\s]*(positiv[ao]s?|negativ[ao]s?)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'positivos': 'POSITIVO',
            'positivas': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },


    # V6.0.13: Biomarcadores para linfomas y mielomas (IHQ250989)
    'BCL6': {
        'nombres_alternativos': ['BCL-6', 'B-CELL LYMPHOMA 6'],
        'descripcion': 'B-cell lymphoma 6 (oncogén, linfomas de células B)',
        'patrones': [
            # Formato "BCL6 Negativo" o "BCL-6 Positivo"
            r'(?i)bcl\s*-?\s*6\s+(positivo|negativo)',
            r'(?i)bcl\s*-?\s*6\s*:\s*(positivo|negativo)',
            # Formato narrativo
            r'(?i)positivas?\s+para\s+.*?bcl\s*-?\s*6(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?bcl\s*-?\s*6(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'MUM1': {
        'nombres_alternativos': ['MUM-1', 'MUM 1', 'IRF4', 'MULTIPLE MYELOMA ONCOGENE 1'],
        'descripcion': 'Multiple Myeloma Oncogene 1 (marcador de mieloma múltiple)',
        'patrones': [
            # Formato "MUM-1 negativo" o "MUM 1 positivo"
            r'(?i)mum\s*-?\s*1\s+(positivo|negativo)',
            r'(?i)mum\s*-?\s*1\s*:\s*(positivo|negativo)',
            # Formato narrativo
            r'(?i)marcadores?\s+mum\s*-?\s*1\s+(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?mum\s*-?\s*1(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?mum\s*-?\s*1(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    # V6.0.12: Cadenas livianas para mieloma múltiple/plasmocitoma (IHQ250992)
    'KAPPA': {
        'nombres_alternativos': ['K', 'KAPPA LIGHT CHAIN', 'CADENA LIGERA KAPPA'],
        'descripcion': 'Cadena ligera Kappa (mieloma múltiple/plasmocitoma)',
        'patrones': [
            # V6.0.12: "restricción de cadenas livianas kappa" → POSITIVO (IHQ250992)
            r'(?i)restricci[óo]n\s+de\s+cadenas?\s+livianas?\s+kappa',
            # Formato "kappa positivo" o "kappa negativo" (sensible a minúsculas)
            r'(?i)\bkappa\b\s*:?\s*(positivo|negativo)',
            # Formato narrativo
            r'(?i)positivas?\s+para\s+.*?kappa(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?kappa(?:\s|,|$)',
            # Formato "expresión de kappa"
            r'(?i)expresi[óo]n\s+de\s+.*?kappa',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'RESTRICCION'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'restricción': 'POSITIVO (RESTRICCIÓN)',
            'restriccion': 'POSITIVO (RESTRICCIÓN)',
        }
    },

    'LAMBDA': {
        'nombres_alternativos': ['L', 'LAMBDA LIGHT CHAIN', 'CADENA LIGERA LAMBDA'],
        'descripcion': 'Cadena ligera Lambda (mieloma múltiple/plasmocitoma)',
        'patrones': [
            # V6.0.12: "lambda negativo" → NEGATIVO (IHQ250992)
            r'(?i)\blambda\b\s+(negativo|positivo)',
            # Formato "lambda: positivo" o "lambda: negativo"
            r'(?i)\blambda\b\s*:?\s*(positivo|negativo)',
            # Formato narrativo
            r'(?i)positivas?\s+para\s+.*?lambda(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?lambda(?:\s|,|$)',
            # Formato "restricción de cadenas livianas lambda"
            r'(?i)restricci[óo]n\s+de\s+cadenas?\s+livianas?\s+lambda',
            # Formato "expresión de lambda"
            r'(?i)expresi[óo]n\s+de\s+.*?lambda',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'RESTRICCION'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'restricción': 'POSITIVO (RESTRICCIÓN)',
            'restriccion': 'POSITIVO (RESTRICCIÓN)',
        }
    },

    # V6.0.16: Biomarcadores para linfomas (IHQ250988)
    'LMP1': {
        'nombres_alternativos': ['LMP-1', 'LMP 1', 'EBV LMP1'],
        'descripcion': 'Latent Membrane Protein 1 (Virus Epstein-Barr)',
        'patrones': [
            # V6.0.16: "No tienen expresión de ALK1 ni de LMP1" (IHQ250988)
            r'(?i)no\s+tienen?\s+expresi[óo]n\s+de\s+.*?LMP\s*1',
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*LMP\s*1(?:\s|,|\.)',
            r'(?i)lmp[^\w]*1[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?lmp\s*1(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?lmp\s*1(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',
            'no tienen expresión': 'NEGATIVO',
        }
    },

    'SALL4': {
        'nombres_alternativos': ['SALL-4', 'SALL 4'],
        'descripcion': 'Sal-like protein 4 (marcador células germinales/hematológicas)',
        'patrones': [
            # V6.0.16: "sin marcación para... ni SALL4" o "no SALL4" (IHQ250988)
            r'(?i)\bni\s+SALL\s*4\b',
            r'(?i)\bno\s+SALL\s*4\b',
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*SALL\s*4(?:\s|,|\.)',
            r'(?i)sall[^\w]*4[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?sall\s*4(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?sall\s*4(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',
            'ni sall4': 'NEGATIVO',
            'no sall4': 'NEGATIVO',
        }
    },

    'ALK1': {
        'nombres_alternativos': ['ALK-1', 'ALK 1'],
        'descripcion': 'Anaplastic Lymphoma Kinase 1 (linfoma anaplásico)',
        'patrones': [
            # V6.0.16: "No tienen expresión de ALK1" (IHQ250988)
            r'(?i)no\s+tienen?\s+expresi[óo]n\s+de\s+ALK\s*1',
            r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*ALK\s*1(?:\s|,|\.)',
            r'(?i)alk[^\w]*1[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?alk\s*1(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?alk\s*1(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'sin marcación': 'NEGATIVO',
            'no tienen expresión': 'NEGATIVO',
        }
    },

    # V6.0.9: Biomarcadores hematológicos adicionales (IHQ251014)
    'TDT': {
        'nombres_alternativos': ['T-DT', 'TdT', 'TERMINAL DEOXYNUCLEOTIDYL TRANSFERASE', 'DT'],
        'descripcion': 'Terminal deoxynucleotidyl transferase (marcador de linfoblastos)',
        'patrones': [
            # Formato con símbolos: "TDT +" o "TDT -"
            r'(?i)tdt\s*[:\s]*\+',
            r'(?i)tdt\s*[:\s]*-',
            # Formato estándar: "TDT: POSITIVO" o "TDT NEGATIVO"
            r'(?i)tdt[:\s]+(positivo|negativo)',
            # Formato narrativo
            r'(?i)positivas?\s+para\s+.*?tdt(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?tdt(?:\s|,|$)',
            # Formato "expresión de TDT"
            r'(?i)expresi[óo]n\s+de\s+.*?tdt',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
        }
    },

    'GLICOFORINA': {
        'nombres_alternativos': ['GLYCOPHORIN', 'GLICOFORINA A', 'GLYCOPHORIN A', 'GLICO', 'GPA'],
        'descripcion': 'Glicoforina A (marcador de diferenciación eritroide)',
        'patrones': [
            # Formato con símbolos: "GLICOFORINA +" o "GLICOFORINA -"
            r'(?i)glicoforina\s*[aA]?\s*[:\s]*\+',
            r'(?i)glicoforina\s*[aA]?\s*[:\s]*-',
            r'(?i)glycophorin\s*[aA]?\s*[:\s]*\+',
            r'(?i)glycophorin\s*[aA]?\s*[:\s]*-',
            # Formato estándar: "GLICOFORINA: POSITIVO" o "GLICOFORINA NEGATIVO"
            r'(?i)glicoforina\s*[aA]?[:\s]+(positivo|negativo)',
            r'(?i)glycophorin\s*[aA]?[:\s]+(positivo|negativo)',
            # Formato narrativo
            r'(?i)positivas?\s+para\s+.*?glicoforina(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?glicoforina(?:\s|,|$)',
            r'(?i)positivas?\s+para\s+.*?glycophorin(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?glycophorin(?:\s|,|$)',
            # Formato "expresión de GLICOFORINA"
            r'(?i)expresi[óo]n\s+de\s+.*?glicoforina',
        
            # Formato narrativo: 'eritroide (Glycophorin)' indica POSITIVO (IHQ251014)
            r'(?i)eritroide\s*\(\s*glycophorin',
            r'(?i)eritroide\s*\(\s*glicoforina',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
            'eritroide': 'POSITIVO',  # IHQ251014: 'eritroide (Glycophorin)' indica presencia
        }
    },


    # Biomarcadores hormonales
    'ACTH': {
        'nombres_alternativos': ['HORMONA ADRENOCORTICOTROPA', 'CORTICOTROPINA'],
        'descripcion': 'Hormona adrenocorticotrópica',
        'patrones': [
            r'(?i)ACTH[,\s:]+(positivo|negativo)',
            r'(?i)ACTH[,\s:]+(\d+%)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'GH': {
        'nombres_alternativos': ['HORMONA DE CRECIMIENTO', 'SOMATOTROPINA'],
        'descripcion': 'Hormona de crecimiento',
        'patrones': [
            r'(?i)\bGH\b[,\s:]+(positivo|negativo)',
            r'(?i)hormona\s+de\s+crecimiento[,\s:]+(positivo|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'PROLACTINA': {
        'nombres_alternativos': ['PRL', 'PROLACTIN'],
        'descripcion': 'Prolactina',
        'patrones': [
            r'(?i)PROLACTINA[,\s:]+(positivo|negativo)',
            r'(?i)PRL[,\s:]+(positivo|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'TSH': {
        'nombres_alternativos': ['TIROTROPINA', 'THYROTROPIN'],
        'descripcion': 'Hormona estimulante de tiroides',
        'patrones': [
            r'(?i)\bTSH\b[,\s:]+(positivo|negativo)',
            r'(?i)tirotropina[,\s:]+(positivo|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'LH': {
        'nombres_alternativos': ['HORMONA LUTEINIZANTE', 'LUTEINIZING HORMONE'],
        'descripcion': 'Hormona luteinizante',
        'patrones': [
            r'(?i)\bLH\b[,\s:]+(positivo|negativo)',
            r'(?i)hormona\s+luteinizante[,\s:]+(positivo|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'FSH': {
        'nombres_alternativos': ['HORMONA FOLICULOESTIMULANTE', 'FOLLICLE STIMULATING HORMONE'],
        'descripcion': 'Hormona foliculoestimulante',
        'patrones': [
            r'(?i)\bFSH\b[,\s:]+(positivo|negativo)',
            r'(?i)hormona\s+foliculoestimulante[,\s:]+(positivo|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    # Otros biomarcadores especializados
    'CKAE1AE3': {
        'nombres_alternativos': ['CKAE1/AE3', 'CK AE1/AE3', 'CITOQUERATINA AE1/AE3', 'CAM 5.2', 'CKAE1E3'],
        'descripcion': 'Citoqueratinas pancitoqueratina',
        'patrones': [
            # V6.2.1: PRIORIDAD -1 - Formato "positivas para CKAE1E3 y p63" (IHQ251012)
            r'(?i)(positiv[ao]s?|negativ[ao]s?)\s+para\s+CKAE1[E/\s]*[AE]*3(?:\s+y\s+|,|\.)',
            # Patrones existentes
            r'(?i)CKAE1[/\s]*AE3[:\s]*(positivo|negativo)',
            r'(?i)CKAE1[E/\s]*3[:\s]*(positivo|negativo)',
            r'(?i)CK\s+AE1[/\s]*AE3[:\s]*(positivo|negativo)',
            r'(?i)CAM\s+5\.2[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+.*?para\s+CKAE1[/\s]*AE3',
            r'(?i)negativas?\s+.*?para\s+CKAE1[/\s]*AE3',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'positivos': 'POSITIVO',
            'positivas': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    # V5.3: MARCADORES MMR (Mismatch Repair) - CRÍTICOS PARA INESTABILIDAD MICROSATELITAL
    # V6.2.0: MEJORADO - Preserva texto completo "EXPRESIÓN NUCLEAR INTACTA" (IHQ251001)
    'MLH1': {
        'nombres_alternativos': ['MLH-1', 'MLH 1'],
        'descripcion': 'Proteína de reparación de ADN MLH1',
        'patrones': [
            # PRIORIDAD 1: Capturar texto completo "Expresión nuclear intacta/ausente"
            r'(?i)MLH1[:\s]*(Expresi[óo]n\s+nuclear\s+(?:intacta|preservada|normal|ausente|p[ée]rdida))',
            # PRIORIDAD 2: Formato corto
            r'(?i)MLH1[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)MLH[^\w]*1[:\s]*(.+?)(?:\.|$|\n)',
            # PRIORIDAD 3: Solo estado
            r'(?i)MLH1[:\s]*(intacta|ausente|positivo|negativo|preservada|normal)',
        ],
        'valores_posibles': ['EXPRESIÓN NUCLEAR INTACTA', 'PÉRDIDA DE EXPRESIÓN', 'ESTABLE', 'INESTABLE'],
        'normalizacion': {
            'intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'expresión nuclear intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'expresion nuclear intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'preservada': 'EXPRESIÓN NUCLEAR INTACTA',
            'normal': 'EXPRESIÓN NUCLEAR INTACTA',
            'ausente': 'PÉRDIDA DE EXPRESIÓN',
            'pérdida': 'PÉRDIDA DE EXPRESIÓN',
            'perdida': 'PÉRDIDA DE EXPRESIÓN',
            'pérdida de expresión': 'PÉRDIDA DE EXPRESIÓN',
            'positivo': 'EXPRESIÓN NUCLEAR INTACTA',
            'negativo': 'PÉRDIDA DE EXPRESIÓN',
            # Compatibilidad hacia atrás
            'estable': 'EXPRESIÓN NUCLEAR INTACTA',
            'inestable': 'PÉRDIDA DE EXPRESIÓN',
        }
    },

    'MSH2': {
        'nombres_alternativos': ['MSH-2', 'MSH 2'],
        'descripcion': 'Proteína de reparación de ADN MSH2',
        'patrones': [
            # PRIORIDAD 1: Capturar texto completo
            r'(?i)MSH2[:\s]*(Expresi[óo]n\s+nuclear\s+(?:intacta|preservada|normal|ausente|p[ée]rdida))',
            # PRIORIDAD 2: Formato corto
            r'(?i)MSH2[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)MSH[^\w]*2[:\s]*(.+?)(?:\.|$|\n)',
            # PRIORIDAD 3: Solo estado
            r'(?i)MSH2[:\s]*(intacta|ausente|positivo|negativo|preservada|normal)',
        ],
        'valores_posibles': ['EXPRESIÓN NUCLEAR INTACTA', 'PÉRDIDA DE EXPRESIÓN', 'ESTABLE', 'INESTABLE'],
        'normalizacion': {
            'intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'expresión nuclear intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'expresion nuclear intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'preservada': 'EXPRESIÓN NUCLEAR INTACTA',
            'normal': 'EXPRESIÓN NUCLEAR INTACTA',
            'ausente': 'PÉRDIDA DE EXPRESIÓN',
            'pérdida': 'PÉRDIDA DE EXPRESIÓN',
            'perdida': 'PÉRDIDA DE EXPRESIÓN',
            'pérdida de expresión': 'PÉRDIDA DE EXPRESIÓN',
            'positivo': 'EXPRESIÓN NUCLEAR INTACTA',
            'negativo': 'PÉRDIDA DE EXPRESIÓN',
            'estable': 'EXPRESIÓN NUCLEAR INTACTA',
            'inestable': 'PÉRDIDA DE EXPRESIÓN',
        }
    },

    'MSH6': {
        'nombres_alternativos': ['MSH-6', 'MSH 6', 'MSH6 Y'],  # "MSH6 Y" es un error común de OCR
        'descripcion': 'Proteína de reparación de ADN MSH6',
        'patrones': [
            # PRIORIDAD 1: Capturar texto completo
            r'(?i)MSH6[:\s]*(Expresi[óo]n\s+nuclear\s+(?:intacta|preservada|normal|ausente|p[ée]rdida))',
            # PRIORIDAD 2: Formato corto
            r'(?i)MSH6[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)MSH[^\w]*6[:\s]*(.+?)(?:\.|$|\n)',
            # PRIORIDAD 3: Solo estado
            r'(?i)MSH6[:\s]*(intacta|ausente|positivo|negativo|preservada|normal)',
        ],
        'valores_posibles': ['EXPRESIÓN NUCLEAR INTACTA', 'PÉRDIDA DE EXPRESIÓN', 'ESTABLE', 'INESTABLE'],
        'normalizacion': {
            'intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'expresión nuclear intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'expresion nuclear intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'preservada': 'EXPRESIÓN NUCLEAR INTACTA',
            'normal': 'EXPRESIÓN NUCLEAR INTACTA',
            'ausente': 'PÉRDIDA DE EXPRESIÓN',
            'pérdida': 'PÉRDIDA DE EXPRESIÓN',
            'perdida': 'PÉRDIDA DE EXPRESIÓN',
            'pérdida de expresión': 'PÉRDIDA DE EXPRESIÓN',
            'positivo': 'EXPRESIÓN NUCLEAR INTACTA',
            'negativo': 'PÉRDIDA DE EXPRESIÓN',
            'estable': 'EXPRESIÓN NUCLEAR INTACTA',
            'inestable': 'PÉRDIDA DE EXPRESIÓN',
        }
    },

    'PMS2': {
        'nombres_alternativos': ['PMS-2', 'PMS 2'],
        'descripcion': 'Proteína de reparación de ADN PMS2',
        'patrones': [
            # PRIORIDAD 1: Capturar texto completo
            r'(?i)PMS2[:\s]*(Expresi[óo]n\s+nuclear\s+(?:intacta|preservada|normal|ausente|p[ée]rdida))',
            # PRIORIDAD 2: Formato corto
            r'(?i)PMS2[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)PMS[^\w]*2[:\s]*(.+?)(?:\.|$|\n)',
            # PRIORIDAD 3: Solo estado
            r'(?i)PMS2[:\s]*(intacta|ausente|positivo|negativo|preservada|normal)',
        ],
        'valores_posibles': ['EXPRESIÓN NUCLEAR INTACTA', 'PÉRDIDA DE EXPRESIÓN', 'ESTABLE', 'INESTABLE'],
        'normalizacion': {
            'intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'expresión nuclear intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'expresion nuclear intacta': 'EXPRESIÓN NUCLEAR INTACTA',
            'preservada': 'EXPRESIÓN NUCLEAR INTACTA',
            'normal': 'EXPRESIÓN NUCLEAR INTACTA',
            'ausente': 'PÉRDIDA DE EXPRESIÓN',
            'pérdida': 'PÉRDIDA DE EXPRESIÓN',
            'perdida': 'PÉRDIDA DE EXPRESIÓN',
            'pérdida de expresión': 'PÉRDIDA DE EXPRESIÓN',
            'positivo': 'EXPRESIÓN NUCLEAR INTACTA',
            'negativo': 'PÉRDIDA DE EXPRESIÓN',
            'estable': 'EXPRESIÓN NUCLEAR INTACTA',
            'inestable': 'PÉRDIDA DE EXPRESIÓN',
        }
    },
}

# Valores de normalización globales
GLOBAL_VALUE_NORMALIZATION = {
    'positivo': 'POSITIVO',
    '+': 'POSITIVO',
    'pos': 'POSITIVO',
    'negativo': 'NEGATIVO',
    '-': 'NEGATIVO',
    'neg': 'NEGATIVO',
    'indeterminado': 'INDETERMINADO',
    'equivoco': 'EQUIVOCO',
    'equívoco': 'EQUIVOCO',
    'no evaluable': 'NO EVALUABLE',
    'n/a': 'N/A',
    'sin dato': 'SIN DATO',
    'no realizado': 'NO REALIZADO',
}


def get_biomarker_info(biomarker_name):
    """Retorna información de un biomarcador específico"""
    return BIOMARKER_DEFINITIONS.get(biomarker_name.upper(), None)


def extract_molecular_expression_section(text: str) -> str:
    """Extrae la sección EXPRESIÓN MOLECULAR del texto (PRIORIDAD MÁXIMA)

    v6.0.2: NUEVO - Prioriza sección "Expresión molecular" sobre descripción microscópica (IHQ250981)

    Args:
        text: Texto completo del informe

    Returns:
        Texto de la sección "Expresión molecular", o string vacío si no se encuentra
    """
    if not text:
        return ''

    # Patrón para identificar "Expresión molecular:"
    pattern = r'Expresi[óo]n\s+molecular\s*:\s*(.*?)(?=\n\n|Nota:|NANCY|ARMANDO|CARLOS|M[ÉE]dica?\s+Pat[óo]log|$)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

    if match:
        return match.group(1).strip()

    return ''


def extract_report_section(text: str) -> str:
    """Extrae la sección REPORTE DE BIOMARCADORES del texto

    v5.3.1: NUEVO - Prioriza resultados sobre descripción de anticuerpos

    Args:
        text: Texto completo del informe

    Returns:
        Texto de la sección de reporte, o string vacío si no se encuentra
    """
    if not text:
        return ''

    # Patrones para identificar la sección REPORTE
    report_start_patterns = [
        r'REPORTE\s+DE\s+BIOMARCADORES\s*:?',
        r'RESULTADOS?\s+(?:DE\s+)?INMUNOHISTOQU[ÍI]MICA',
        r'RESULTADOS?\s+(?:DE\s+)?IHQ',
        r'BIOMARCADORES\s*:',
    ]

    # Patrones para el final de la sección (antes de diagnóstico o comentarios)
    report_end_patterns = [
        r'DIAGN[ÓO]STICO',
        r'COMENTARIOS',
        r'Isquemia\s+fr[íi]a',
        r'diagnósticos?\s+de\s+"',  # Antes de diagnóstico citado
    ]

    # Buscar inicio de sección REPORTE
    report_start = None
    for pattern in report_start_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            report_start = match.end()
            break

    if report_start is None:
        return ''  # No se encontró sección REPORTE

    # Buscar final de sección
    report_end = None
    text_after_start = text[report_start:]
    for pattern in report_end_patterns:
        match = re.search(pattern, text_after_start, re.IGNORECASE)
        if match:
            report_end = report_start + match.start()
            break

    # Si no se encontró final, usar hasta el final del texto
    if report_end is None:
        report_end = len(text)

    # Extraer la sección
    report_section = text[report_start:report_end].strip()

    return report_section


def extraer_seccion(texto, inicio, fin):
    """Extrae una sección del texto entre dos marcadores

    V6.0.0: NUEVO - Función auxiliar para lógica de prioridad de secciones

    Args:
        texto: Texto completo del informe
        inicio: Patrón regex del marcador de inicio de sección
        fin: Patrón regex del marcador de fin de sección

    Returns:
        Texto de la sección extraída o None si no se encuentra
    """
    patron = rf'{inicio}(.*?)(?:{fin})'
    match = re.search(patron, texto, re.DOTALL | re.IGNORECASE)
    return match.group(1) if match else None


def buscar_en_diagnostico(texto_completo, patron):
    """Busca patrón en la sección DIAGNÓSTICO del PDF

    V6.0.0: NUEVO - PRIORIDAD 1 para extracción de biomarcadores

    Esta función implementa la lógica de prioridad:
    - Busca PRIMERO en la sección DIAGNÓSTICO (incluye subsecciones como "Expresión molecular")
    - La información del DIAGNÓSTICO es la final, revisada y condensada

    Args:
        texto_completo: Texto completo del informe IHQ
        patron: Patrón regex a buscar

    Returns:
        Valor capturado por el patrón o None si no se encuentra
    """
    # Extraer sección DIAGNÓSTICO (incluye subsecciones como "Expresión molecular")
    seccion_diagnostico = extraer_seccion(
        texto_completo,
        inicio=r"DIAGN[ÓO]STICO|EXPRESI[ÓO]N\s+MOLECULAR",
        fin=r"COMENTARIOS|OBSERVACIONES|DESCRIPCI[ÓO]N\s+MICROSC[ÓO]PICA|RESPONSABLE|$"
    )

    if seccion_diagnostico:
        match = re.search(patron, seccion_diagnostico, re.IGNORECASE)
        if match:
            # Retornar el primer grupo capturado si existe, sino el match completo
            if match.groups():
                return match.group(1).strip()
            else:
                return match.group(0).strip()
    return None


def buscar_en_microscopica(texto_completo, patron):
    """Busca patrón en la sección DESCRIPCIÓN MICROSCÓPICA del PDF

    V6.0.0: NUEVO - PRIORIDAD 2 (fallback) para extracción de biomarcadores
    V6.0.14: MEJORADO - Excluye subsección "Anticuerpos:" para evitar capturar reactivos técnicos (IHQ250984)

    Esta función implementa la lógica de prioridad:
    - Busca SOLO SI NO se encontró en DIAGNÓSTICO
    - La información de DESCRIPCIÓN MICROSCÓPICA es más detallada pero preliminar

    Args:
        texto_completo: Texto completo del informe IHQ
        patron: Patrón regex a buscar

    Returns:
        Valor capturado por el patrón o None si no se encuentra
    """
    seccion_microscopica = extraer_seccion(
        texto_completo,
        inicio=r"DESCRIPCI[ÓO]N\s+MICROSC[ÓO]PICA",
        fin=r"DIAGN[ÓO]STICO|EXPRESI[ÓO]N\s+MOLECULAR|RESPONSABLE"
    )

    if seccion_microscopica:
        # V6.0.14: FILTRAR subsección "Anticuerpos:" (reactivos técnicos, NO resultados)
        # Esta subsección contiene información técnica de reactivos que NO debe ser extraída
        anticuerpos_match = re.search(
            r'Anticuerpos:\s*(.+?)(?=REPORTE\s+DE\s+BIOMARCADORES|BLOQUE|$)',
            seccion_microscopica,
            re.IGNORECASE | re.DOTALL
        )
        if anticuerpos_match:
            # Eliminar la subsección de anticuerpos del texto a buscar
            seccion_sin_anticuerpos = seccion_microscopica[:anticuerpos_match.start()] + \
                                     seccion_microscopica[anticuerpos_match.end():]
            seccion_microscopica = seccion_sin_anticuerpos

        match = re.search(patron, seccion_microscopica, re.IGNORECASE)
        if match:
            # Retornar el primer grupo capturado si existe, sino el match completo
            if match.groups():
                return match.group(1).strip()
            else:
                return match.group(0).strip()
    return None


def extract_biomarkers(text: str) -> Dict[str, str]:
    """Extrae todos los biomarcadores configurados del texto

    v6.0.11: CRÍTICO - Filtra sección "Anticuerpos:" antes de extraer (IHQ250984)
    v6.0.2: MEJORADO - Prioriza "Expresión molecular" > REPORTE > texto completo (IHQ250981)

    Args:
        text: Texto del informe IHQ

    Returns:
        Diccionario con biomarcadores encontrados
        Ejemplo: {'HER2': 'POSITIVO', 'KI67': '25%', 'ER': 'POSITIVO'}
    """
    if not text:
        return {}

    # ═══════════════════════════════════════════════════════════════════════
    # V6.0.12: ESTRATEGIA MULTI-BÚSQUEDA SIN CORTAR TEXTO (IHQ250984)
    # ═══════════════════════════════════════════════════════════════════════
    # LECCIÓN APRENDIDA de v6.0.11:
    # - NO cortar el texto (elimina información necesaria en páginas posteriores)
    # - SÍ buscar con patrones específicos que distingan entre:
    #   * Sección técnica: "Anticuerpos: [nombres de reactivos]"
    #   * Sección de resultados: "REPORTE DE BIOMARCADORES: [resultados]"
    #
    # ESTRATEGIA:
    # 1. Buscar primero en secciones específicas (REPORTE, Expresión molecular)
    # 2. Buscar con patrones que filtren contexto técnico
    # 3. Usar texto completo solo como último recurso
    # ═══════════════════════════════════════════════════════════════════════

    results = {}

    # PRIORIDAD 0: Extraer sección "REPORTE DE BIOMARCADORES:" (IHQ250984)
    # Esta sección contiene resultados en formato estructurado con guiones
    biomarker_report_section = None
    match_reporte = re.search(
        r'REPORTE\s+DE\s+BIOMARCADORES?:\s*(.+?)(?=DIAGN[ÓO]STICO|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if match_reporte:
        biomarker_report_section = match_reporte.group(1)

    # v6.0.2: PRIORIDAD 1 - Extraer sección "Expresión molecular" (caso IHQ250981)
    molecular_section = extract_molecular_expression_section(text)

    # v5.3.1: PRIORIDAD 2 - Extraer sección REPORTE (descripción microscópica)
    report_section = extract_report_section(text)

    # Definir biomarcadores que deben priorizarse de "Expresión molecular"
    molecular_priority = ['ER', 'PR', 'HER2', 'RECEPTOR_ESTROGENOS', 'RECEPTOR_PROGESTERONA']

    # V6.0.12: NUEVA CASCADA DE BÚSQUEDA (sin cortar texto)
    # Buscar en orden de especificidad: REPORTE > Molecular > report_section > texto completo

    # PRIORIDAD 0: Buscar en "REPORTE DE BIOMARCADORES:" (formato estructurado IHQ250984)
    if biomarker_report_section:
        narrative_results = extract_narrative_biomarkers(biomarker_report_section)
        results.update(narrative_results)

    # PRIORIDAD 1: Buscar en "Expresión molecular" (IHQ250981)
    if molecular_section:
        narrative_results = extract_narrative_biomarkers(molecular_section)
        # Solo actualizar si no encontró antes
        for key, value in narrative_results.items():
            if key not in results:
                results[key] = value

    # PRIORIDAD 2: Buscar en sección REPORTE (descripción microscópica)
    if report_section:
        narrative_results = extract_narrative_biomarkers(report_section)
        for key, value in narrative_results.items():
            if key not in results:
                results[key] = value

    # PRIORIDAD 3: Buscar en texto completo (fallback)
    if not results:
        narrative_results = extract_narrative_biomarkers(text)
        results.update(narrative_results)

    # Procesar cada biomarcador definido en configuración (método original)
    for biomarker_name, definition in BIOMARKER_DEFINITIONS.items():
        # Solo procesar si no fue encontrado por método narrativo
        if biomarker_name not in results:
            value = None

            # V6.0.12: Cascada de búsqueda específica
            # PRIORIDAD 0: Buscar en "REPORTE DE BIOMARCADORES:"
            if biomarker_report_section:
                value = extract_single_biomarker(biomarker_report_section, biomarker_name, definition)

            # PRIORIDAD 1: Buscar en "Expresión molecular"
            if not value and biomarker_name.upper() in molecular_priority and molecular_section:
                value = extract_single_biomarker(molecular_section, biomarker_name, definition)

            # PRIORIDAD 2: Buscar en sección REPORTE
            if not value and report_section:
                value = extract_single_biomarker(report_section, biomarker_name, definition)

            # PRIORIDAD 3: Buscar en texto completo (fallback)
            if not value:
                value = extract_single_biomarker(text, biomarker_name, definition)

            if value:
                results[biomarker_name] = value

    return results


def extract_narrative_biomarkers(text: str) -> Dict[str, str]:
    """Extrae biomarcadores del formato narrativo tipo:
    'células neoplásicas son fuertemente positivas para CK7 y GATA 3 y EMA, negativas para CK20, SOX10 y CDX2'
    Y formatos complejos como 'RECEPTOR DE ESTRÓGENOS, positivo focal'

    V6.1.1: FIX IHQ250995 - Soporta "pérdida de expresión" y patrones complejos de próstata
    """
    results = {}

    # V6.1.1: FIX IHQ250995 - NUEVO patrón para "pérdida/ausencia de expresión"
    # Casos de próstata: "pérdida de expresión para CK34 BETA E12 y P63"
    perdida_pattern = r'(?i)(?:p[eé]rdida|ausencia|sin)\s+de\s+expresi[óo]n\s+para[:\s]+(.+?)(?:\s+con\s+marcaci[óo]n|\.|$)'
    for match in re.finditer(perdida_pattern, text, re.DOTALL):
        lista_biomarkers_raw = match.group(1).strip()
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)
        biomarcadores_encontrados = re.split(r'[,;]\s*|\s+y\s+', lista_biomarkers_raw)

        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue

            # Normalizar usando la función de medical_extractor para consistencia
            from core.extractors.medical_extractor import normalize_biomarker_name_simple
            bio_norm = normalize_biomarker_name_simple(bio_raw)

            # Convertir a formato IHQ_ para storage
            bio_norm_ihq = normalize_biomarker_name(bio_raw) if bio_norm else None

            if bio_norm_ihq and bio_norm_ihq not in results:
                results[bio_norm_ihq] = 'NEGATIVO'
                logging.info(f"✅ [Pérdida expresión] '{bio_raw}' → {bio_norm_ihq} = NEGATIVO")

    # V6.1.1: FIX IHQ250995 - NUEVO patrón complejo "pérdida de X con marcación positiva para Y"
    # Casos de próstata: "pérdida para CK34 y P63 con marcación positiva para Racemasa"
    complejo_pattern = r'(?i)(?:p[eé]rdida|ausencia)\s+de\s+expresi[óo]n\s+para[:\s]+(.+?)\s+con\s+marcaci[óo]n\s+(positiva|negativa)\s+para[:\s]+(.+?)(?:\.|$)'
    for match in re.finditer(complejo_pattern, text, re.DOTALL):
        # Grupo 1: biomarcadores NEGATIVOS (pérdida de expresión)
        negativos_raw = match.group(1).strip()
        negativos = re.split(r'[,;]\s*|\s+y\s+', re.sub(r'\s*\n\s*', ' ', negativos_raw))

        for bio_raw in negativos:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue

            from core.extractors.medical_extractor import normalize_biomarker_name_simple
            bio_norm = normalize_biomarker_name_simple(bio_raw)
            bio_norm_ihq = normalize_biomarker_name(bio_raw) if bio_norm else None

            if bio_norm_ihq and bio_norm_ihq not in results:
                results[bio_norm_ihq] = 'NEGATIVO'
                logging.info(f"✅ [Pérdida complejo] '{bio_raw}' → {bio_norm_ihq} = NEGATIVO")

        # Grupo 2+3: estado y biomarcadores POSITIVOS/NEGATIVOS
        estado = 'POSITIVO' if 'positiva' in match.group(2).lower() else 'NEGATIVO'
        positivos_raw = match.group(3).strip()
        positivos = re.split(r'[,;]\s*|\s+y\s+', re.sub(r'\s*\n\s*', ' ', positivos_raw))

        for bio_raw in positivos:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue

            from core.extractors.medical_extractor import normalize_biomarker_name_simple
            bio_norm = normalize_biomarker_name_simple(bio_raw)
            bio_norm_ihq = normalize_biomarker_name(bio_raw) if bio_norm else None

            if bio_norm_ihq and bio_norm_ihq not in results:
                results[bio_norm_ihq] = estado
                logging.info(f"✅ [Marcación complejo] '{bio_raw}' → {bio_norm_ihq} = {estado}")

    # V6.1.2: NUEVO patrón para "Positividad en las células tumorales para [lista]" (IHQ250997)
    # Formato: "Positividad en las células tumorales para HMB-45, CD68, receptor de progesterona, y de manera muy focal para H-caldesmon"
    positividad_pattern = r'(?i)Positividad\s+en\s+las\s+c[eé]lulas\s+tumorales\s+para\s+(.+?)(?:\.\s*(?:El\s+[íi]ndice|Negatividad)|$)'
    for match in re.finditer(positividad_pattern, text, re.DOTALL):
        lista_biomarkers_raw = match.group(1).strip()

        logging.info(f"🔍 [Positividad] Lista detectada: '{lista_biomarkers_raw}'")

        # Limpiar saltos de línea y normalizar espacios
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)

        # V6.1.2: Detectar "y de manera muy focal para [lista]" como grupo separado
        # Split en dos grupos: antes y después de "de manera"
        grupos = []
        if 'de manera' in lista_biomarkers_raw.lower() or 'muy focal' in lista_biomarkers_raw.lower():
            partes = re.split(r',?\s+y\s+de\s+manera\s+(?:muy\s+)?focal\s+para\s+', lista_biomarkers_raw, flags=re.IGNORECASE)
            if len(partes) > 1:
                grupos = [(partes[0], False), (partes[1], True)]  # (texto, es_focal)
            else:
                grupos = [(lista_biomarkers_raw, False)]
        else:
            grupos = [(lista_biomarkers_raw, False)]

        for grupo_texto, es_focal in grupos:
            # Separar por comas Y "y", pero NO por "/"
            biomarcadores_encontrados = re.split(r'[,;]\s*|\s+y\s+', grupo_texto)

            for bio_raw in biomarcadores_encontrados:
                bio_raw = bio_raw.strip().rstrip('.')
                if not bio_raw or bio_raw.lower() in ['de', 'la', 'las', 'los']:
                    continue

                # Normalizar nombre del biomarcador
                normalized_name = normalize_biomarker_name(bio_raw)
                if normalized_name and normalized_name not in results:
                    estado = 'POSITIVO (focal)' if es_focal else 'POSITIVO'
                    results[normalized_name] = estado
                    logging.info(f"✅ [Positividad] Extraído: '{bio_raw}' → {normalized_name} = {estado}")

    # V6.1.2: NUEVO patrón para "Negatividad para [lista]" (IHQ250997)
    # Formato: "Negatividad para CK AE1/AE3, CK7, CK20, sinaptofisina, DOG-1, SOX-10, S100, Melan-A y CD34"
    negatividad_pattern = r'(?i)Negatividad\s+para\s+(.+?)(?:\.|$)'
    for match in re.finditer(negatividad_pattern, text, re.DOTALL):
        lista_biomarkers_raw = match.group(1).strip()

        logging.info(f"🔍 [Negatividad] Lista detectada: '{lista_biomarkers_raw}'")

        # Limpiar saltos de línea y normalizar espacios
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)

        # Separar por comas Y "y", pero NO por "/"
        biomarcadores_encontrados = re.split(r'[,;]\s*|\s+y\s+', lista_biomarkers_raw)

        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue

            # Normalizar nombre del biomarcador
            normalized_name = normalize_biomarker_name(bio_raw)
            if normalized_name and normalized_name not in results:
                results[normalized_name] = 'NEGATIVO'
                logging.info(f"✅ [Negatividad] Extraído: '{bio_raw}' → {normalized_name} = NEGATIVO")

    # V6.1.3: FIX IHQ250999 - Patrón para "células positivas para [lista]" SIN palabra "marcación"
    # Ej: "células mioepiteliales positivas para P63, calponina y CK5/6"
    # Ej: "células neoplásicas negativas para CD20, CD3 y BCL6"
    positivas_list_pattern = r'(?i)(?:células?|c[eé]lulas?)\s+(?:\w+\s+)?(positiv[ao]s?|negativ[ao]s?)\s+para\s+(.+?)(?=\s+recubriendo|\.\s*(?:Se|En|El|La|Las|Los)|,\s+(?:recubriendo|con)|$)'
    for match in re.finditer(positivas_list_pattern, text, re.DOTALL):
        estado = 'POSITIVO' if 'positiv' in match.group(1).lower() else 'NEGATIVO'
        lista_biomarkers_raw = match.group(2).strip()

        logging.info(f"🔍 [V6.1.3] Lista 'células positivas' detectada: '{lista_biomarkers_raw}' → Estado: {estado}")

        # Limpiar saltos de línea y normalizar espacios
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)

        # Separar por comas Y "y", pero NO por "/"
        biomarcadores_encontrados = re.split(r'[,;]\s*|\s+y\s+', lista_biomarkers_raw)

        logging.info(f"🔍 Biomarcadores separados: {biomarcadores_encontrados}")

        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue

            # Si contiene "/" (variantes del mismo biomarcador), tomar solo la primera parte
            if '/' in bio_raw:
                bio_raw_original = bio_raw
                bio_raw = bio_raw.split('/')[0].strip()
                logging.info(f"🔍 Split por '/': '{bio_raw_original}' → '{bio_raw}'")

            # Normalizar nombre del biomarcador
            normalized_name = normalize_biomarker_name(bio_raw)
            if normalized_name and normalized_name not in results:
                results[normalized_name] = estado
                logging.info(f"✅ [células positivas] Extraído: '{bio_raw}' → {normalized_name} = {estado}")

    # V6.1.3: NUEVO - Patrón para formato compacto de inmunofenotipo (IHQ251010)
    # Ej: "inmunofenotipo CK7+/CK20-, p40+/PAX8+/p63 y negativas para TTF-1"
    # Captura biomarcadores en formato compacto con +/- que indica POSITIVO/NEGATIVO
    compact_immunophenotype_pattern = r'(?i)inmunofenotipo\s+([A-Z0-9\+\-/,\s]+?)(?:\s+y\s+(?:positivas?|negativas?)\s+para|\.|\s*$)'
    for match in re.finditer(compact_immunophenotype_pattern, text):
        compact_list = match.group(1).strip()

        logging.info(f"🔍 [V6.1.3 inmunofenotipo compacto] Detectado: '{compact_list}'")

        # Split por comas, espacios y barras para separar biomarcadores
        # Ej: "CK7+/CK20-, p40+/PAX8+/p63" → ["CK7+", "CK20-", "p40+", "PAX8+", "p63"]
        compact_markers = re.split(r'[,/\s]+', compact_list)

        for marker_raw in compact_markers:
            marker_raw = marker_raw.strip()
            if not marker_raw or marker_raw in ['y', 'e']:
                continue

            # Detectar si termina en + o -
            if marker_raw.endswith('+'):
                bio_name = marker_raw[:-1].strip()
                estado = 'POSITIVO'
            elif marker_raw.endswith('-'):
                bio_name = marker_raw[:-1].strip()
                estado = 'NEGATIVO'
            else:
                # V6.1.3: Si no tiene +/-, intentar normalizar para verificar si es un biomarcador válido
                # Ejemplo: "p40+/PAX8+/p63" → p63 no tiene signo pero es un biomarcador válido
                bio_name = marker_raw
                # Intentar normalizar para verificar si es reconocido
                normalized_test = normalize_biomarker_name(bio_name)
                if normalized_test:
                    # Es un biomarcador válido reconocido → inferir POSITIVO (está en inmunofenotipo)
                    estado = 'POSITIVO'
                    logging.info(f"🔍 [inmunofenotipo compacto] '{marker_raw}' sin signo → inferir POSITIVO")
                else:
                    # No es un biomarcador reconocido, ignorar (puede ser texto descriptivo)
                    continue

            # Normalizar nombre del biomarcador
            normalized_name = normalize_biomarker_name(bio_name)
            if normalized_name and normalized_name not in results:
                results[normalized_name] = estado
                logging.info(f"✅ [inmunofenotipo compacto] Extraído: '{marker_raw}' → {normalized_name} = {estado}")

    # V6.0.22: NUEVO - Patrón para "Sin marcación para [lista]" (IHQ251009)
    # Ej: "Sin marcación para CD30, CICLINA, CMYC"
    # Captura listas de biomarcadores NEGATIVOS en casos de linfomas
    sin_marcacion_pattern = r'(?i)Sin\s+marcaci[óo]n\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ]+?)(?=\.|\s+Ki67|\s+ki67|$)'
    for match in re.finditer(sin_marcacion_pattern, text, re.DOTALL):
        lista_biomarkers_raw = match.group(1).strip()

        logging.info(f"🔍 [V6.0.22] 'Sin marcación' detectada: '{lista_biomarkers_raw}' → Estado: NEGATIVO")

        # Limpiar saltos de línea y normalizar espacios
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)

        # Separar por comas Y "y", pero NO por "/"
        biomarcadores_encontrados = re.split(r'[,;]\s*|\s+y\s+', lista_biomarkers_raw)

        logging.info(f"🔍 Biomarcadores sin marcación separados: {biomarcadores_encontrados}")

        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue

            # Normalizar nombre del biomarcador
            normalized_name = normalize_biomarker_name(bio_raw)
            if normalized_name and normalized_name not in results:
                results[normalized_name] = 'NEGATIVO'
                logging.info(f"✅ [sin marcación] Extraído: '{bio_raw}' → {normalized_name} = NEGATIVO")

    # V6.0.12.1: FIX - Patrón para "marcación positiva/negativa para: lista, de, biomarcadores" (IHQ250991)
    # V6.0.17: MEJORADO - Captura multilínea incluyendo "R.\nEstrogenos" (IHQ250994)
    # Ej: "Las células tumorales basaloides presentan marcación positiva para: p40, p63, EBERP4/Ep-CAM, BCL2."
    # Ej: "marcación positiva para P40, R.\nEstrogenos además" (captura todo incluyendo saltos de línea)
    logging.info("🔍 [V6.0.17] Ejecutando extract_narrative_biomarkers con soporte para R. Estrogenos")
    # Captura hasta palabras clave que indican fin de lista: "además", inicio de oración, secciones, punto + mayúscula
    marcacion_list_pattern = r'(?i)(?:presentan\s+)?marcaci[óo]n\s+(positiva|negativa)\s+para[:\s]+(.+?)(?=\s+además|\.\s*(?:En|A\d+\.)|$)'
    for match in re.finditer(marcacion_list_pattern, text, re.DOTALL):
        estado = 'POSITIVO' if 'positiva' in match.group(1).lower() else 'NEGATIVO'
        lista_biomarkers_raw = match.group(2).strip()
        
        logging.info(f"🔍 Lista detectada: '{lista_biomarkers_raw}' → Estado: {estado}")
        
        # Limpiar saltos de línea y normalizar espacios
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)
        
        # V6.0.12.1 FIX: Separar por comas Y "y", pero NO por "/" 
        # "/" se usa para variantes del MISMO biomarcador (EBERP4/Ep-CAM son el mismo: BER_EP4)
        biomarcadores_encontrados = re.split(r'[,;]\s*|\s+y\s+', lista_biomarkers_raw)
        
        logging.info(f"🔍 Biomarcadores separados: {biomarcadores_encontrados}")
        
        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue
            
            # V6.0.12.1: Si contiene "/" (variantes del mismo biomarcador), tomar solo la primera parte
            # Ej: "EBERP4/Ep-CAM" → "EBERP4", "p63 p40" → "p63 p40" (sin cambios)
            if '/' in bio_raw:
                bio_raw_original = bio_raw
                bio_raw = bio_raw.split('/')[0].strip()
                logging.info(f"🔍 Split por '/': '{bio_raw_original}' → '{bio_raw}'")

            # V6.0.17: Limpiar texto descriptivo antes de normalizar (IHQ250994)
            # Ej: "P16 de forma parcheada" → "P16", "P53 de expresión usual (Wild Type)" → "P53"
            bio_raw = re.sub(r'\s+de\s+(forma|expresi[óo]n)\s+\w+.*', '', bio_raw, flags=re.IGNORECASE).strip()
            bio_raw = re.sub(r'\s*\([^)]+\).*', '', bio_raw).strip()  # Eliminar paréntesis y todo después

            # Normalizar nombre del biomarcador
            normalized_name = normalize_biomarker_name(bio_raw)
            if normalized_name and normalized_name not in results:
                results[normalized_name] = estado
                logging.info(f"✅ [extract_narrative] Extraído: '{bio_raw}' → {normalized_name} = {estado}")
            elif normalized_name in results:
                logging.info(f"⚠️ [extract_narrative] YA existe: '{bio_raw}' → {normalized_name}")
            else:
                logging.warning(f"❌ [extract_narrative] NO normalizado: '{bio_raw}'")

    # V6.1.4: FIX IHQ251000 - NUEVOS patrones para formato narrativo hepático
    # 1. "marcación usual para [lista]" → POSITIVO
    # 2. "hay marcación positiva de [lista]" → POSITIVO (con "de" en vez de "para")
    # 3. "marcación para [biomarcador]" → POSITIVO (sin palabra positiva/negativa)

    # Patrón 1: "marcación usual para [lista]"
    # Ej: "presenta marcación usual para arginasa y Hepatocito"
    marcacion_usual_pattern = r'(?i)marcaci[óo]n\s+usual\s+para\s+(.+?)(?=,\s+hay|,\s+marcaci[óo]n|\.|$)'
    for match in re.finditer(marcacion_usual_pattern, text, re.DOTALL):
        lista_biomarkers_raw = match.group(1).strip()

        logging.info(f"🔍 [V6.1.4 marcación usual] Lista detectada: '{lista_biomarkers_raw}'")

        # Limpiar saltos de línea y normalizar espacios
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)

        # Separar por "y" (no por comas en este contexto)
        biomarcadores_encontrados = re.split(r'\s+y\s+', lista_biomarkers_raw)

        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.,')
            if not bio_raw:
                continue

            # Normalizar nombre del biomarcador
            normalized_name = normalize_biomarker_name(bio_raw)
            if normalized_name and normalized_name not in results:
                results[normalized_name] = 'POSITIVO'
                logging.info(f"✅ [marcación usual] Extraído: '{bio_raw}' → {normalized_name} = POSITIVO")

    # Patrón 2: "hay marcación positiva de [lista]" (con "de" en lugar de "para")
    # Ej: "hay marcación positiva de CK19 Y CK7 en zonas con reacción ductular"
    marcacion_de_pattern = r'(?i)hay\s+marcaci[óo]n\s+(positiva|negativa)\s+de\s+(.+?)(?=\s+en\s+zonas|\s+en\s+la|\s+en\s+el|\s+y\s+marcaci[óo]n|\.|\s*$)'
    for match in re.finditer(marcacion_de_pattern, text, re.DOTALL):
        estado = 'POSITIVO' if 'positiva' in match.group(1).lower() else 'NEGATIVO'
        lista_biomarkers_raw = match.group(2).strip()

        logging.info(f"🔍 [V6.1.4 marcación de] Lista detectada: '{lista_biomarkers_raw}' → Estado: {estado}")

        # Limpiar saltos de línea y normalizar espacios
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)

        # Separar por "Y" (mayúscula común en OCR) o "y"
        biomarcadores_encontrados = re.split(r'\s+[Yy]\s+', lista_biomarkers_raw)

        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.,')
            if not bio_raw:
                continue

            # Normalizar nombre del biomarcador
            normalized_name = normalize_biomarker_name(bio_raw)
            if normalized_name and normalized_name not in results:
                results[normalized_name] = estado
                logging.info(f"✅ [marcación de] Extraído: '{bio_raw}' → {normalized_name} = {estado}")

    # Patrón 3: "marcación para [biomarcador]" sin palabra positiva/negativa
    # Ej: "marcación para CD34 en la vasculatura hepatica"
    # IMPORTANTE: Solo capturar cuando NO hay "positiva" o "negativa" explícita
    marcacion_simple_pattern = r'(?i)(?<!positiva\s)(?<!negativa\s)marcaci[óo]n\s+para\s+([A-Z0-9\-/]+)(?=\s+en\s+|\s+que\s+|\s+de\s+|\.|\s*$)'
    for match in re.finditer(marcacion_simple_pattern, text):
        bio_raw = match.group(1).strip()

        logging.info(f"🔍 [V6.1.4 marcación simple] Biomarcador detectado: '{bio_raw}'")

        # Normalizar nombre del biomarcador
        normalized_name = normalize_biomarker_name(bio_raw)
        if normalized_name and normalized_name not in results:
            # Por defecto POSITIVO si solo dice "marcación para"
            results[normalized_name] = 'POSITIVO'
            logging.info(f"✅ [marcación simple] Extraído: '{bio_raw}' → {normalized_name} = POSITIVO")

    # V6.1.5: FIX IHQ251003 - Biomarcadores entre paréntesis como evidencia de positividad
    # Ej: "células neoplásicas de origen epitelial (CKAE1/AE3)" → CKAE1AE3 POSITIVO
    # Ej: "con expresión de marcadores que sugieren origen mamario (MAMAGLOBINA y GATA 3)" → POSITIVO
    # Captura cualquier paréntesis después de frases clave relacionadas con marcadores/origen
    parentesis_pattern = r'(?i)(?:de\s+origen\s+\w+|expresi[óo]n\s+de\s+marcadores?(?:\s+que)?(?:\s+sugieren)?(?:\s+origen)?(?:\s+\w+)?)\s*\(([^)]+)\)'
    for match in re.finditer(parentesis_pattern, text, re.DOTALL):
        lista_biomarkers_raw = match.group(1).strip()

        logging.info(f"🔍 [V6.1.5 paréntesis] Lista detectada: '{lista_biomarkers_raw}'")

        # Limpiar saltos de línea y normalizar espacios
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)

        # Separar por comas Y "y", pero NO por "/"
        biomarcadores_encontrados = re.split(r'[,;]\s*|\s+y\s+', lista_biomarkers_raw)

        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue

            # V6.1.5: NO dividir por "/" si es CKAE1/AE3 (es un biomarcador único, no variantes)
            # Si contiene "/" y NO es CKAE1/AE3, tomar solo la primera parte
            if '/' in bio_raw and 'CKAE1' not in bio_raw.upper():
                bio_raw_original = bio_raw
                bio_raw = bio_raw.split('/')[0].strip()
                logging.info(f"🔍 Split por '/': '{bio_raw_original}' → '{bio_raw}'")

            # Normalizar nombre del biomarcador
            normalized_name = normalize_biomarker_name(bio_raw)
            if normalized_name and normalized_name not in results:
                results[normalized_name] = 'POSITIVO'
                logging.info(f"✅ [paréntesis] Extraído: '{bio_raw}' → {normalized_name} = POSITIVO")

    # V6.1.6: FIX IHQ251004 - Patrón narrativo "siendo negativo/positivo en las células neoplásicas"
    # Ej: "control interno positivo con expresión de GATA 3, siendo negativo en las células neoplásicas"
    # Este patrón es común cuando el biomarcador es positivo en tejido normal (control) pero negativo en tumor
    sendo_pattern = r'(?i)(?:con\s+)?expresi[óo]n\s+de\s+([A-Z0-9\s/-]+?),?\s+siendo\s+(negativ[ao]s?|positiv[ao]s?)\s+en\s+las\s+c[ée]lulas\s+neopl[áa]sicas'
    for match in re.finditer(sendo_pattern, text, re.DOTALL):
        bio_raw = match.group(1).strip()
        estado = 'POSITIVO' if 'positiv' in match.group(2).lower() else 'NEGATIVO'

        logging.info(f"🔍 [V6.1.6 siendo neoplásicas] Detectado: '{bio_raw}' siendo {estado} en células neoplásicas")

        # Normalizar nombre del biomarcador
        normalized_name = normalize_biomarker_name(bio_raw)
        if normalized_name and normalized_name not in results:
            results[normalized_name] = estado
            logging.info(f"✅ [siendo neoplásicas] Extraído: '{bio_raw}' → {normalized_name} = {estado}")

    # Patrón NUEVO: Biomarcadores complejos tipo "RECEPTOR DE ESTRÓGENOS, positivo focal"
    complex_patterns = [
        # V6.0.13: CORREGIDO - Formato estructurado con guión SIN paréntesis (IHQ250984)
        r'(?i)-\s*RECEPTOR(?:ES)?\s+DE\s+ESTR[ÓO]GENO[S]?\s*:\s*(POSITIV[OA]S?|NEGATIV[OA]S?)\.?',
        # V6.0.13: CORREGIDO - Typo común "PROGRESTERONA" + formato correcto (IHQ250984)
        r'(?i)-\s*RECEPTOR(?:ES)?\s+DE\s+PROGRESTE?RONA\s*:\s*(POSITIV[OA]S?|NEGATIV[OA]S?)\.?',
        # V6.0.14: CORREGIDO - HER2 captura solo resultado y score, NO texto técnico ni reactivos (IHQ250984)
        r'(?i)-\s*HER\s*-?\s*2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)(?:\s*\((?:Score\s+)?(\d+\+?)\))?\s*(tinción\s+[^.]+?(?=\.|$))?\.?',
        # V6.0.13: MEJORADO - Ki-67 formato narrativo "Tinción nuclear en el X%" (IHQ250984)
        r'(?i)-\s*Ki\s*-?\s*67\s*:\s*(?:Tinción\s+nuclear\s+en\s+el\s+)?(\d+)\s*%',
        r'(?i)-\s*Ki\s*-?\s*67\s*:\s*(.+?)\.?$',
        # V6.0.10: Patrones para GATA3 y SOX10 (IHQ250984)
        r'(?i)tinción\s+nuclear\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*3',
        # V6.0.12: Mejorado para capturar typos comunes de SOX10 (SXO10, SO X10, etc.)
        r'(?i)negativas?\s+para\s+S[OX]{1,2}[OX]?\s*10',  # Captura SOX10, SXO10, SO10
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
        r'(?i)acth,\s+(positivo|negativo)(?:\s+focal)?',
        r'(?i)gh,\s+(positivo|negativo)(?:\s+focal)?',
        r'(?i)prolactina,\s+(positivo|negativo)(?:\s+focal)?',
        r'(?i)tsh,\s+(positivo|negativo)(?:\s+focal)?',
        r'(?i)lh,\s+(positivo|negativo)(?:\s+focal)?',
        r'(?i)fsh,\s+(positivo|negativo)(?:\s+focal)?',
        r'(?i)cd45,\s+(positivo|negativo)(?:\s+focal)?',
        r'(?i)cd20,\s+(positivo|negativo)(?:\s+focal)?',
        r'(?i)cd3,\s+(positivo|negativo)(?:\s+focal)?',
        # V6.0.13: BCL6 y MUM1 (IHQ250989)
        r'(?i)bcl\s*-?\s*6\s+(positivo|negativo)',
        r'(?i)marcadores?\s+mum\s*-?\s*1\s+(positivo|negativo)',
        r'(?i)mum\s*-?\s*1\s+(positivo|negativo)',
        # V6.0.13: Formato "(CD20+)" o "CD38+" (IHQ250989)
        r'(?i)linfocitos\s+B\s*\(CD\s*20\s*\+\)',
        r'(?i)células\s+plasmáticas\s*\(CD\s*(?:38|138)\s*\+\)',
        r'(?i)ckae1/ae3,\s+(positivo|negativo)(?:\s+focal)?',
        r'(?i)sinaptofisina,\s+(positivo|negativo)(?:\s+focal)?',
        # NUEVOS PATRONES PARA CASO 2 - BIOMARCADORES HORMONALES
        r'(?i)ckae1/ae3\s*,?\s+(positivo|negativo)(?:\s+(?:fuerte|difuso|focal))*',
        r'(?i)sinaptofisina\s*,?\s+(positivo|negativo)(?:\s+(?:fuerte|difuso|focal))*',
        # Patrones de expresión hormonal específicos
        r'(?i)acth\s*,\s+(positivo|negativo)',
        r'(?i)gh\s*,\s+(positivo|negativo)',
        r'(?i)prolactina\s*,\s+(positivo|negativo)',
        r'(?i)tsh\s*,\s+(positivo|negativo)',
        r'(?i)lh\s*,\s+(positivo|negativo)',
        r'(?i)fsh\s*,\s+(positivo|negativo)',
        # Patrones para inmunomarcación
        # CORREGIDO: Capturar a través de saltos de línea para casos como "CKAE1/AE3 y\nSINAPTOFISINA"
        # Estrategia: Capturar hasta punto, o hasta línea que no sea biomarcador
        r'(?i)inmuno\s*marcaci[óo]n\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+((?:[^\.\n]+(?:\n[A-Z0-9/]+)?)+)',
        # NUEVO: V6.0.6 - Inmunorreactividad en listas narrativas (IHQ250983)
        r'(?i)inmunorreactividad\s+(?:en\s+las\s+)?(?:c[eé]lulas\s+)?(?:tumorales\s+)?para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9]+(?:\s+heterog[eé]neo|focal|difuso)?)?)',
        r'(?i)inmunorreactividad\s+(?:fuerte\s+y\s+)?difusa\s+para\s+((?:[^\.\n]+(?:\n[A-Z0-9/]+)?)+)',
        r'(?i)presentan\s+inmuno\s*marcaci[óo]n\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+((?:[^\.\n]+(?:\n[A-Z0-9/]+)?)+)'
    ]
    
    for pattern in complex_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            biomarker_name = None
            
            # V6.0.2: Detectar patrones de "Expresión molecular" (capturan 2 grupos)
            is_molecular_pattern = ('RECEPTORES' in pattern and 'DE' in pattern) or 'SOBREEXPRESI' in pattern

            # Mapeo específico para cada patrón
            if 'estr' in pattern.lower():
                biomarker_name = 'ER'
            elif 'progesterona' in pattern.lower() or 'progreste' in pattern.lower():
                biomarker_name = 'PR'
            elif 'her' in pattern.lower():
                biomarker_name = 'HER2'
            elif 'ki' in pattern.lower() and '67' in pattern.lower():
                biomarker_name = 'KI67'
            elif 'gata' in pattern.lower():
                biomarker_name = 'GATA3'
            elif 'sox' in pattern.lower() or 'sxo' in pattern.lower() or ('S[OX]' in pattern and '10' in pattern):
                biomarker_name = 'SOX10'
            elif 'synaptophysin' in pattern.lower() or 'sinaptofisina' in pattern.lower():
                biomarker_name = 'SYNAPTOPHYSIN'
            elif 'chromogranina' in pattern.lower():
                biomarker_name = 'CHROMOGRANINA'
            elif 'ckae1' in pattern.lower():
                biomarker_name = 'CKAE1_AE3'
            elif 'acth' in pattern.lower():
                biomarker_name = 'ACTH'
            elif 'gh,' in pattern.lower():
                biomarker_name = 'GH'
            elif 'prolactina' in pattern.lower():
                biomarker_name = 'PROLACTINA'
            elif 'tsh' in pattern.lower():
                biomarker_name = 'TSH'
            elif 'lh' in pattern.lower():
                biomarker_name = 'LH'
            elif 'fsh' in pattern.lower():
                biomarker_name = 'FSH'
            elif 'cd45' in pattern.lower():
                biomarker_name = 'CD45'
            elif 'cd20' in pattern.lower():
                biomarker_name = 'CD20'
            elif 'cd3' in pattern.lower():
                biomarker_name = 'CD3'
            # V6.0.13: BCL6 y MUM1 (IHQ250989)
            elif 'bcl' in pattern.lower() and '6' in pattern.lower():
                biomarker_name = 'BCL6'
            elif 'mum' in pattern.lower():
                biomarker_name = 'MUM1'
            # V6.0.13: CD20+ o CD38+ (IHQ250989)
            elif 'linfocitos' in pattern.lower() and 'cd' in pattern.lower() and '20' in pattern.lower():
                biomarker_name = 'CD20'
            elif 'plasmáticas' in pattern.lower() and 'cd' in pattern.lower():
                biomarker_name = 'CD138'
            elif 'inmuno' in pattern.lower():
                # Patrón especial para "inmunomarcación positiva para X y Y"
                biomarkers_text = match if isinstance(match, str) else match[0] if match else ""
                if biomarkers_text:
                    # CORREGIDO: Limpiar saltos de línea antes de separar
                    biomarkers_text = re.sub(r'\s*\n\s*', ' ', biomarkers_text)
                    # Separar múltiples biomarcadores
                    biomarkers_list = re.split(r'\s+y\s+', biomarkers_text)
                    for bio_text in biomarkers_list:
                        bio_name = normalize_biomarker_name(bio_text.strip())
                        if bio_name:
                            results[bio_name] = 'POSITIVO'
                continue

            # V6.0.10: Procesar patrones de formato estructurado con guión (IHQ250984)
            if biomarker_name == 'GATA3' and isinstance(match, str):
                # Caso GATA3: "tinción nuclear positiva fuerte y difusa para GATA 3"
                results[biomarker_name] = 'POSITIVO'
            elif biomarker_name == 'SOX10' and isinstance(match, str):
                # Caso SOX10: "negativas para SOX10" o "negativas para SXO10"
                results[biomarker_name] = 'NEGATIVO'
            # V6.0.13: CD20+ y CD138/CD38+ son POSITIVO automáticamente (IHQ250989)
            elif biomarker_name == 'CD20' and ('linfocitos' in pattern.lower() or '+' in str(match)):
                results[biomarker_name] = 'POSITIVO'
            elif biomarker_name == 'CD138' and ('plasmáticas' in pattern.lower() or '+' in str(match)):
                results[biomarker_name] = 'POSITIVO'
            elif biomarker_name == 'KI67' and isinstance(match, str):
                # V6.0.13: Caso Ki-67 mejorado para formato "Tinción nuclear en el X%" (IHQ250984)
                # Si es solo un número (del patrón mejorado), agregar %
                if match.strip().isdigit():
                    results[biomarker_name] = f"{match.strip()}%"
                else:
                    # Descripción completa
                    results[biomarker_name] = match.strip()
            elif biomarker_name == 'HER2' and isinstance(match, tuple) and len(match) >= 3:
                # V6.0.14: Caso HER2 con descripción completa: "Positivo (Score 3+) tinción membranosa..." (IHQ250984)
                if match[2]:  # Si hay descripción adicional
                    value = f"{match[0].upper()}"
                    if match[1]:  # Si hay score
                        value += f" (SCORE {match[1].upper()})"
                    results[biomarker_name] = value
                elif match[1]:
                    value = f"{match[0].upper()} (SCORE {match[1].upper()})"
                    results[biomarker_name] = value
                else:
                    value = match[0].upper()
                    results[biomarker_name] = value
            elif biomarker_name and isinstance(match, str):
                value = 'POSITIVO' if match.lower() == 'positivo' else 'NEGATIVO'
                results[biomarker_name] = value
            elif biomarker_name and isinstance(match, tuple):
                # V6.0.2: Para patrones de "Expresión molecular", combinar ambos grupos
                if is_molecular_pattern and len(match) >= 2:
                    # Formato: "POSITIVOS (90-100%)" o "EQUIVOCO (SCORE 2+)"
                    value = f"{match[0].upper()} ({match[1].upper()})"
                    results[biomarker_name] = value
                else:
                    # Para otros patrones, tomar solo el primer grupo
                    value = 'POSITIVO' if match[0].lower() == 'positivo' else 'NEGATIVO'
                    results[biomarker_name] = value

    # V6.0.6: NUEVO - Patrón para listas narrativas con inmunorreactividad
    # Ej: "inmunorreactividad en las células tumorales para CKAE1AE3, S100, PAX8 y p40 heterogéneo"
    immunoreactivity_list_pattern = r'(?i)inmunorreactividad\s+(?:en\s+las\s+)?(?:c[eé]lulas\s+)?(?:tumorales\s+)?para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9]+(?:\s+heterog[eé]neo|focal|difuso)?)?)'

    for match in re.finditer(immunoreactivity_list_pattern, text):
        lista_biomarkers = match.group(1).strip()

        # Usar post-procesador con modificadores
        biomarkers_with_modifiers = post_process_biomarker_list_with_modifiers(lista_biomarkers)

        # Agregar a resultados (NO sobreescribir)
        for bio_name, bio_value in biomarkers_with_modifiers.items():
            if bio_name not in results:
                results[bio_name] = bio_value

    # Patrón 1: "positivas para X y Y, negativas para Z y W"
    positive_pattern = r'(?i)positivas?\s+para\s+(.+?)(?:,\s*negativas?|$|\.|;)'
    positive_match = re.search(positive_pattern, text)
    
    if positive_match:
        positive_list = positive_match.group(1)
        # V6.0.10: Mejorado para manejar listas "X, Y, y Z" correctamente (IHQ250983)
        positive_biomarkers = []
        for part in re.split(r',\s*', positive_list):
            # Limpiar "y" o "e" al inicio del fragmento
            part = re.sub(r'^\s*(?:y|e)\s+', '', part, flags=re.IGNORECASE).strip()
            # Split por "y" o "e" internos
            sub_parts = re.split(r'\s+(?:y|e)\s+', part, flags=re.IGNORECASE)
            # Agregar solo partes no vacías
            positive_biomarkers.extend([b.strip() for b in sub_parts if b.strip()])

        for biomarker in positive_biomarkers:
            normalized_name = normalize_biomarker_name(biomarker)
            if normalized_name:
                results[normalized_name] = 'POSITIVO'
    
    # Patrón 2: "negativas para X, Y y Z"
    # V6.0.6: Mejorado para capturar "son negativas para X, Y y Z"
    # V6.0.10: Mejorado para capturar listas con coma antes de "y" (ej: "X, Y, y Z")
    negative_pattern = r'(?i)(?:son\s+)?negativas?\s+para\s+([A-Z0-9,\s/\-]+(?:(?:,\s*)?(?:y|e)\s+[A-Z0-9]+)*?)(?:\s*\.|\s*,\s+y\s+son|$)'
    negative_match = re.search(negative_pattern, text)
    
    if negative_match:
        negative_list = negative_match.group(1)
        # V6.0.10: Mejorado para manejar listas "X, Y, y Z" correctamente (IHQ250983)
        negative_biomarkers = []
        for part in re.split(r',\s*', negative_list):
            # Limpiar "y" o "e" al inicio del fragmento
            part = re.sub(r'^\s*(?:y|e)\s+', '', part, flags=re.IGNORECASE).strip()
            # Split por "y" o "e" internos
            sub_parts = re.split(r'\s+(?:y|e)\s+', part, flags=re.IGNORECASE)
            # Agregar solo partes no vacías
            negative_biomarkers.extend([b.strip() for b in sub_parts if b.strip()])

        for biomarker in negative_biomarkers:
            normalized_name = normalize_biomarker_name(biomarker)
            if normalized_name:
                results[normalized_name] = 'NEGATIVO'
    
    # Patrón 3: "Los marcadores X, Y y Z son negativos"
    markers_negative_patterns = [
        r'(?i)los\s+marcadores\s+(.+?)\s+son\s+negativos',
        r'(?i)los\s+marcadores,\s*(.+?)\s+son\s+negativos',  # Con coma después de "marcadores"
    ]
    
    for pattern in markers_negative_patterns:
        markers_negative_match = re.search(pattern, text)
        
        if markers_negative_match:
            markers_list = markers_negative_match.group(1)
            # Limpiar y dividir marcadores - manejar comas y "y"
            markers_list = re.sub(r'\s+y\s+', ', ', markers_list)  # Convertir "y" a comas
            markers = [m.strip() for m in markers_list.split(',') if m.strip()]
            
            for marker in markers:
                normalized_name = normalize_biomarker_name(marker)
                if normalized_name:
                    results[normalized_name] = 'NEGATIVO'

    # Patrón 3B: "Los marcadores X, Y y Z son positivos" - CRÍTICO PARA CASO IHQ250009
    markers_positive_patterns = [
        r'(?i)los\s+marcadores\s+(.+?)\s+son\s+positivos',
        r'(?i)los\s+marcadores,\s*(.+?)\s+son\s+positivos',  # Con coma después de "marcadores"
    ]
    
    for pattern in markers_positive_patterns:
        markers_positive_match = re.search(pattern, text)
        
        if markers_positive_match:
            markers_list = markers_positive_match.group(1)
            # Limpiar y dividir marcadores - manejar comas y "y"
            markers_list = re.sub(r'\s+y\s+', ', ', markers_list)  # Convertir "y" a comas
            markers = [m.strip() for m in markers_list.split(',') if m.strip()]
            
            for marker in markers:
                normalized_name = normalize_biomarker_name(marker)
                if normalized_name:
                    results[normalized_name] = 'POSITIVO'
    
    # Patrón 4: Biomarcadores individuales "X positivo", "Y negativo" - AMPLIADO PARA TODOS LOS BIOMARCADORES
    individual_patterns = [
        r'(?i)(p16|p40|s100|her2|her-2|ki67|ki-67|ck7|glicoforina|tdt|atrx|idh1|cmyc|igg4|igg|mamoglobina|hepatocito|psa|lambda|kappa|ck19|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2|er|pr|cd3|cd5|cd10|cd20|cd30|cd34|cd38|cd45|cd56|cd61|cd68|cd117|cd138|sox10|vimentina|chromogranina|synaptophysin|melan-a)\s+(positivo|negativo|focal)',
        r'(?i)(p16|p40|s100|her2|her-2|ki67|ki-67|ck7|ck19|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2|er|pr|cd3|cd5|cd10|cd20|cd30|cd34|cd38|cd45|cd56|cd61|cd68|cd117|cd138|sox10|vimentina|chromogranina|synaptophysin|melan-a)\s*:\s*(positivo|negativo|focal)',
        r'(?i)(pl6)\s+(positivo|negativo|focal)',  # Variante pl6 en lugar de p16
    ]

    # Patrón 4B: "El marcador X es positivo/negativo" - CRÍTICO PARA CASO IHQ250009
    single_marker_patterns = [
        r'(?i)el\s+marcador\s+(p16|p40|s100|her2|her-2|ki67|ki-67|ck7|glicoforina|tdt|atrx|idh1|cmyc|igg4|igg|mamoglobina|hepatocito|psa|lambda|kappa|ck19|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2)\s+es\s+(positivo|negativo|focal)',
        r'(?i)marcador\s+(p16|p40|s100|her2|her-2|ki67|ki-67|ck7|ck19|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2)\s+es\s+(positivo|negativo|focal)',
    ]
    
    # Procesar patrones individuales
    all_individual_patterns = individual_patterns + single_marker_patterns
    
    for pattern in all_individual_patterns:
        for match in re.finditer(pattern, text):
            marker_raw = match.group(1)
            value_raw = match.group(2)
            
            normalized_name = normalize_biomarker_name(marker_raw)
            if normalized_name:
                value = 'POSITIVO' if value_raw.lower() in ['positivo', 'focal'] else 'NEGATIVO'
                results[normalized_name] = value
    
    # Patrón 5: "X y Y negativos"
    compound_negative_pattern = r'(?i)((?:p16|p40|s100|her2|her-2|ki67|ki-67|ck7|glicoforina|tdt|atrx|idh1|cmyc|igg4|igg|mamoglobina|hepatocito|psa|lambda|kappa|ck19|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2)(?:\s+y\s+(?:p16|p40|s100|her2|her-2|ki67|ki-67|ck7|ck19|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2))*)\s+negativos'

    for match in re.finditer(compound_negative_pattern, text):
        compound = match.group(1)
        markers = [m.strip() for m in re.split(r'\s+y\s+', compound)]

        for marker in markers:
            normalized_name = normalize_biomarker_name(marker)
            if normalized_name:
                results[normalized_name] = 'NEGATIVO'

    # V6.X.X: NUEVOS patrones para formato descriptivo tipo IHQ251005
    # Patrón 6: "[lista]: [descripción cualitativa]" - Formato de linfomas/inmunofenotipo
    # Ej: "CD20 y CD3: distribución en patrón reactivo"
    # Ej: "BCL2 y BCL6: expresión en patrón reactivo folicular"
    # Ej: "CD38: células plasmáticas policlonales"
    # Ej: "IgG: células plasmáticas positivas"
    # Detecta términos que indican positividad/reactividad
    # Actualizado: Termina en punto o en otro biomarcador con dos puntos
    descriptive_pattern = r'(?i)([A-Z][A-Za-z0-9\-]+(?:\s+y\s+[A-Z][A-Za-z0-9\-]+)*):\s*([^.]+?)(?=\.\s*[A-Z][A-Za-z0-9\-]+:|\.(?:\s|$)|$)'

    for match in re.finditer(descriptive_pattern, text):
        biomarcadores_raw = match.group(1).strip()
        descripcion = match.group(2).strip().lower()

        # Determinar estado basado en palabras clave en la descripción
        estado = None
        if any(keyword in descripcion for keyword in ['positiv', 'reactiv', 'expresión', 'distribuci', 'marcaci', 'células']):
            # Verificar si hay negación
            if any(neg in descripcion for neg in ['no se', 'ausencia', 'negativ', 'sin expresión']):
                estado = 'NEGATIVO'
            else:
                estado = 'POSITIVO'

        if estado:
            # Separar biomarcadores si hay "y"
            biomarcadores_lista = [b.strip() for b in re.split(r'\s+y\s+', biomarcadores_raw)]

            for bio_raw in biomarcadores_lista:
                normalized_name = normalize_biomarker_name(bio_raw)
                if normalized_name and normalized_name not in results:
                    results[normalized_name] = estado
                    logging.info(f"✅ [Descriptivo] Extraído: '{bio_raw}' → {normalized_name} = {estado} ('{descripcion[:50]}...')")

    return results


def post_process_biomarker_list_with_modifiers(biomarker_text: str) -> Dict[str, str]:
    """
    Procesa lista narrativa de biomarcadores, detectando modificadores individuales.

    V6.0.6: Agregada para IHQ250983 - manejo de listas con modificadores.

    Ejemplos:
    - "CKAE1AE3, S100, PAX8 y p40 heterogéneo"
      -> {'CKAE1AE3': 'POSITIVO', 'S100': 'POSITIVO', 'PAX8': 'POSITIVO', 'P40': 'POSITIVO HETEROGÉNEO'}
    - "CK7, CK20 focal y TTF-1 difuso"
      -> {'CK7': 'POSITIVO', 'CK20': 'POSITIVO FOCAL', 'TTF1': 'POSITIVO DIFUSO'}

    Args:
        biomarker_text: Texto con lista (ej: "CKAE1AE3, S100, PAX8 y p40 heterogéneo")

    Returns:
        Dict con biomarcadores y valores con modificadores
    """
    if not biomarker_text:
        return {}

    result = {}

    # Limpiar texto
    text_clean = biomarker_text.strip()

    # Dividir por comas y "y"/"e"
    # Usar regex para preservar modificadores
    parts = re.split(r',\s*|\s+y\s+|\s+e\s+', text_clean, flags=re.IGNORECASE)

    for part in parts:
        part = part.strip()
        # V6.0.10: Limpiar caracteres especiales iniciales (comas, puntos, punto y coma)
        part = part.lstrip(',.;')
        part = part.strip()
        if not part:
            continue

        # Detectar modificador al final (heterogéneo, focal, difuso)
        modifier_match = re.search(r'^(.+?)\s+(heterog[eé]neo|focal|difuso)$', part, re.IGNORECASE)

        if modifier_match:
            # Tiene modificador
            biomarker_raw = modifier_match.group(1).strip()
            modifier = modifier_match.group(2).strip().upper()

            # Normalizar modificador
            if modifier in ['HETEROGÉNEO', 'HETEROGENEO']:
                modifier = 'HETEROGÉNEO'

            normalized_name = normalize_biomarker_name(biomarker_raw)
            if normalized_name:
                result[normalized_name] = f'POSITIVO {modifier}'
        else:
            # Sin modificador, solo positivo
            normalized_name = normalize_biomarker_name(part)
            if normalized_name:
                result[normalized_name] = 'POSITIVO'

    return result


def normalize_biomarker_name(raw_name: str) -> Optional[str]:
    """Normaliza nombres de biomarcadores a sus equivalentes en BIOMARKER_DEFINITIONS"""
    if not raw_name:
        return None
    
    raw_clean = raw_name.strip().upper()
    
    # Mapeo directo - EXPANDIDO PARA TODOS LOS BIOMARCADORES DETECTADOS
    name_mapping = {
        'CK7': 'CK7',
        'CK-7': 'CK7',
        'CK 7': 'CK7',
        'GLICOFORINA': 'GLICOFORINA',
        'GLICOFORINA': 'GLICOFORINA',
        'GLICOFORINA': 'GLICOFORINA',
        'TDT': 'TDT',
        'TDT': 'TDT',
        'TDT': 'TDT',
        'ATRX': 'ATRX',
        'ATRX': 'ATRX',
        'ATRX': 'ATRX',
        'IDH1': 'IDH1',
        'IDH1': 'IDH1',
        'IDH1': 'IDH1',
        'CMYC': 'CMYC',
        'CMYC': 'CMYC',
        'CMYC': 'CMYC',
        'IGG4': 'IGG4',
        'IGG4': 'IGG4',
        'IGG4': 'IGG4',
        'IGG': 'IGG',
        'IGG': 'IGG',
        'IGG': 'IGG',
        'MAMOGLOBINA': 'MAMOGLOBINA',
        'MAMAGLOBINA': 'MAMOGLOBINA',  # V6.1.5: Variante sin O (IHQ251003)
        'MAMA GLOBINA': 'MAMOGLOBINA',
        'MAMA-GLOBINA': 'MAMOGLOBINA',
        'HEPATOCITO': 'HEPATOCITO',  # V6.0.16: Auto-agregado
        'HEPATOCYTE': 'HEPATOCITO',
        'ARGINASA': 'ARGINASA',  # V6.1.4: Biomarcador hepático
        'ARGINASE': 'ARGINASA',
        'PSA': 'PSA',  # V6.0.17: Duplicados eliminados
        'LAMBDA': 'LAMBDA',  # V6.0.17: Duplicados eliminados
        'KAPPA': 'KAPPA',  # V6.0.17: Duplicados eliminados
        'CK19': 'CK19',  # V6.0.16: Agregado para IHQ250987
        'CK-19': 'CK19',
        'CK 19': 'CK19',
        'CK20': 'CK20',
        'CK-20': 'CK20',
        'CK 20': 'CK20',
        'CK2O': 'CK20',  # OCR error común O->0
        'GATA3': 'GATA3',
        'GATA 3': 'GATA3',
        'GATA-3': 'GATA3',
        'GFAP': 'GFAP',  # V6.0.5: Proteína ácida fibrilar glial
        'G-FAP': 'GFAP',
        'G FAP': 'GFAP',
        'CDX2': 'CDX2',
        'CDX-2': 'CDX2',
        'CDX 2': 'CDX2',
        'EMA': 'EMA',
        'E.M.A': 'EMA',
        'SOX10': 'SOX10',
        'SOX-10': 'SOX10',
        'SOX 10': 'SOX10',
        'SOXIO': 'SOX10',  # OCR error común 1->I->O
        # E-Cadherina
        'E-CADHERINA': 'E_CADHERINA',
        'E CADHERINA': 'E_CADHERINA',
        'ECADHERINA': 'E_CADHERINA',
        'HER2': 'HER2',
        'HER-2': 'HER2',
        'KI67': 'KI-67',
        'KI-67': 'KI-67',
        'ER': 'ER',
        'PR': 'PR',
        # RECEPTORES LARGOS - CRÍTICO PARA CASOS COMPLEJOS
        'RECEPTOR DE ESTRÓGENOS': 'ER',
        'RECEPTOR DE ESTROGENOS': 'ER',
        'RECEPTOR DE PROGESTERONA': 'PR',
        'RECEPTORES DE ESTRÓGENOS': 'ER',
        'RECEPTORES DE ESTROGENOS': 'ER',
        'RECEPTORES DE PROGESTERONA': 'PR',
        # V6.0.17: Formas abreviadas "R. Estrogenos" (IHQ250994)
        'R. ESTROGENOS': 'ER',
        'R. ESTRÓGENOS': 'ER',
        'R.ESTROGENOS': 'ER',
        'R ESTROGENOS': 'ER',
        'R. PROGESTERONA': 'PR',
        'R.PROGESTERONA': 'PR',
        'R PROGESTERONA': 'PR',
        # Biomarcadores P
        'P16': 'P16',
        'PL6': 'P16',  # pl6 es variante de p16
        'P40': 'P40',
        'P63': 'P63',
        'P-63': 'P63',
        'P 63': 'P63',
        # V6.1.3: Biomarcadores celulas mioepiteliales (IHQ250999)
        'CK5/6': 'CK5_6',
        'CK5/5': 'CK5_6',  # Error OCR común
        'CK55': 'CK5_6',   # Variante sin barra
        'CK5 / 6': 'CK5_6',
        'CK5 6': 'CK5_6',
        'CK56': 'CK5_6',
        'CK 5/6': 'CK5_6',
        'CK 5 / 6': 'CK5_6',
        'CALPONINA': 'CALPONINA',
        'S100': 'S100',
        'TTF1': 'TTF1',
        'TTF-1': 'TTF1',
        'P53': 'P53',
        'CDK4': 'CDK4',
        'MDM2': 'MDM2',
        # Biomarcadores CD - CRÍTICOS PARA CASOS 2-10
        'CD1A': 'CD1A',  # V6.2.1: Timomas (IHQ251012)
        'CD1a': 'CD1A',
        'CD-1A': 'CD1A',
        'CD-1a': 'CD1A',
        'CD 1A': 'CD1A',
        'CD 1a': 'CD1A',
        'CD3': 'CD3',
        'CD5': 'CD5',
        'CD10': 'CD10',
        'CD15': 'CD15',  # V6.0.25: Fix IHQ251009 - linfomas
        'CD20': 'CD20',
        'CD23': 'CD23',  # V6.0.25: Fix IHQ251009 - linfomas
        'CD30': 'CD30',
        'CD34': 'CD34',
        'CD38': 'CD38',
        'CD45': 'CD45',
        'CD56': 'CD56',
        'CD61': 'CD61',
        'CD68': 'CD68',
        'CD117': 'CD117',
        'CD138': 'CD138',
        'BCL6': 'BCL6',
        'BCL-6': 'BCL6',
        'BCL 6': 'BCL6',
        'MUM1': 'MUM1',
        'MUM-1': 'MUM1',
        'MUM 1': 'MUM1',
        # Otros biomarcadores
        'VIMENTINA': 'VIMENTINA',
        'VIMENTIN': 'VIMENTINA',
        'BER-EP4': 'BER_EP4',
        'BER EP4': 'BER_EP4',
        'BERRP4': 'BER_EP4',
        'EBERP4': 'BER_EP4',
        'EP-CAM': 'BER_EP4',
        'EPCAM': 'BER_EP4',
        'BCL2': 'BCL2',
        'BCL-2': 'BCL2',
        'BCL 2': 'BCL2',
        'CHROMOGRANINA': 'CHROMOGRANINA',
        'SYNAPTOPHYSIN': 'SYNAPTOPHYSIN',
        'SYNAPTOFISINA': 'SYNAPTOPHYSIN',  # Variante en español
        'SINAPTOFISINA': 'SYNAPTOPHYSIN',  # Variante del caso 2
        'CKAE1/AE3': 'CKAE1AE3',  # Formato del caso 2
        # V6.0.6: Variantes adicionales IHQ250983
        'CKAE1AE3': 'CKAE1AE3',
        'CK AE1/AE3': 'CKAE1AE3',
        'CKAE1 AE3': 'CKAE1AE3',
        'ACTH': 'ACTH',
        'GH': 'GH', 
        'PROLACTINA': 'PROLACTINA',
        'TSH': 'TSH',
        'LH': 'LH',
        'FSH': 'FSH',
        'MELAN-A': 'MELAN_A',
        'MELAN A': 'MELAN_A',
        'NAPSINA': 'NAPSIN',
        'NAPSIN': 'NAPSIN',
        'NAPSINA A': 'NAPSIN',
        'NAPSIN A': 'NAPSIN',
        # V5.2: BIOMARCADORES FALTANTES
        'WT1': 'WT1',
        'WT-1': 'WT1',
        'WT 1': 'WT1',
        'PAX5': 'PAX5',  # V6.0.25: Fix IHQ251009 - linfomas B
        'PAX-5': 'PAX5',
        'PAX 5': 'PAX5',
        'PAX8': 'PAX8',
        'PAX-8': 'PAX8',
        'PAX 8': 'PAX8',
        # V5.3: MARCADORES MMR (Mismatch Repair)
        'MLH1': 'MLH1',
        'MLH-1': 'MLH1',
        'MLH 1': 'MLH1',
        'MSH2': 'MSH2',
        'MSH-2': 'MSH2',
        'MSH 2': 'MSH2',
        'MSH6': 'MSH6',
        'MSH-6': 'MSH6',
        'MSH 6': 'MSH6',
        'MSH6 Y': 'MSH6',  # Error común de OCR
        'PMS2': 'PMS2',
        'PMS-2': 'PMS2',
        'PMS 2': 'PMS2',
        # V6.0.5: BIOMARCADORES NARRATIVOS IHQ250982
        'CKAE1E3': 'CKAE1AE3',
        'CKAE1 E3': 'CKAE1AE3',
        'CKAE1-E3': 'CKAE1AE3',
        'CAM 5.2': 'CAM52',
        'CAM5.2': 'CAM52',
        'CAM52': 'CAM52',
        'GFAP': 'GFAP',
        # V6.1.1: FIX IHQ250995 - Biomarcadores de próstata
        'RACEMASA': 'RACEMASA',
        'RACEMASE': 'RACEMASA',
        'P504S': 'RACEMASA',
        'AMACR': 'RACEMASA',
        'P63': 'P63',
        'P-63': 'P63',
        'P 63': 'P63',
        # V6.1.3: Biomarcadores celulas mioepiteliales (IHQ250999)
        'CK5/6': 'CK5_6',
        'CK5/5': 'CK5_6',  # Error OCR común
        'CK55': 'CK5_6',   # Variante sin barra
        'CK 5/6': 'CK5_6',
        'CK 5 / 6': 'CK5_6',
        'CK55': 'CK5_6',   # Variante sin barra
        'CK5 / 6': 'CK5_6',
        'CK5 6': 'CK5_6',
        'CK56': 'CK5_6',
        'CK 5/6': 'CK5_6',
        'CK 5 / 6': 'CK5_6',
        'CALPONINA': 'CALPONINA',
        # V6.1.2: FIX mapeo 34BE12 - La columna en BD es IHQ_CK34BE12 (con CK)
        '34BE12': 'CK34BE12',
        '34BETAE12': 'CK34BE12',
        '34BETA E12': 'CK34BE12',
        '34 BETA E12': 'CK34BE12',
        '34BETA': 'CK34BE12',
        '34 BETA': 'CK34BE12',
        'CK34BE12': 'CK34BE12',
        'CK34BETAE12': 'CK34BE12',
        'CK34BETA E12': 'CK34BE12',
        'CK34 BETA E12': 'CK34BE12',
        'CK34BETA': 'CK34BE12',
        'CK34 BETA': 'CK34BE12',
        # V6.1.2: Biomarcadores IHQ250997 (tumor maligno indiferenciado)
        'HMB-45': 'HMB45',
        'HMB 45': 'HMB45',
        'HMB45': 'HMB45',
        'H-CALDESMON': 'H_CALDESMON',
        'H CALDESMON': 'H_CALDESMON',
        'HCALDESMON': 'H_CALDESMON',
        'H-CALDESMÓN': 'H_CALDESMON',
        'H CALDESMÓN': 'H_CALDESMON',
        'ACTINA DE MÚSCULO LISO': 'AML',
        'ACTINA DE MUSCULO LISO': 'AML',
        'ACTINA MÚSCULO LISO': 'AML',
        'ACTINA MUSCULO LISO': 'AML',
        'AML': 'AML',
        'DOG-1': 'DOG1',
        'DOG 1': 'DOG1',
        'DOG1': 'DOG1',
    }

    return name_mapping.get(raw_clean)


def extract_single_biomarker(
    text: str,
    biomarker_name: str,
    definition: Dict[str, Any]
) -> Optional[str]:
    """Extrae un biomarcador específico del texto

    Args:
        text: Texto del informe
        biomarker_name: Nombre del biomarcador (ej: 'HER2')
        definition: Definición del biomarcador de la configuración

    Returns:
        Valor del biomarcador normalizado o None si no se encuentra
    """
    # V6.0.1: LÓGICA ESPECIAL PARA KI67 - Invertir prioridad
    if biomarker_name == 'KI67' and definition.get('usa_prioridad_seccion', False):
        # Para Ki67, buscar PRIMERO en DESCRIPCIÓN MICROSCÓPICA
        for pattern in definition.get('patrones', []):
            valor_microscopica = buscar_en_microscopica(text, pattern)
            if valor_microscopica:
                normalized = normalize_biomarker_value(
                    valor_microscopica,
                    definition.get('normalizacion', {}),
                    definition.get('tipo_valor', 'PERCENTAGE')
                )
                if normalized:
                    return normalized

        # LUEGO en DIAGNÓSTICO (fallback)
        for pattern in definition.get('patrones', []):
            valor_diagnostico = buscar_en_diagnostico(text, pattern)
            if valor_diagnostico:
                normalized = normalize_biomarker_value(
                    valor_diagnostico,
                    definition.get('normalizacion', {}),
                    definition.get('tipo_valor', 'PERCENTAGE')
                )
                if normalized:
                    return normalized

        # V6.1.2: PRIORIDAD 3 - Buscar en texto completo (fallback final para IHQ250997)
        # Casos donde Ki-67 está en sección "Inmunohistoquímica:" que NO es parte de DESCRIPCIÓN MICROSCÓPICA ni DIAGNÓSTICO
        for pattern in definition.get('patrones', []):
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                # Obtener valor capturado
                if match.groups():
                    raw_value = match.group(1).strip()
                else:
                    raw_value = match.group(0).strip()

                # Normalizar
                normalized = normalize_biomarker_value(
                    raw_value,
                    definition.get('normalizacion', {}),
                    definition.get('tipo_valor', 'PERCENTAGE')
                )
                if normalized:
                    return normalized

        return None

    # V6.0.0: Si el biomarcador usa prioridad de sección (RESTO DE BIOMARCADORES)
    if definition.get('usa_prioridad_seccion', False):
        # PRIORIDAD 1: Buscar en sección DIAGNÓSTICO
        for pattern in definition.get('patrones', []):
            valor_diagnostico = buscar_en_diagnostico(text, pattern)
            if valor_diagnostico:
                # Normalizar el valor
                normalized = normalize_biomarker_value(
                    valor_diagnostico,
                    definition.get('normalizacion', {}),
                    definition.get('tipo_valor', 'CATEGORICAL')
                )
                if normalized:
                    return normalized

        # PRIORIDAD 2: Buscar en DESCRIPCIÓN MICROSCÓPICA (fallback)
        for pattern in definition.get('patrones', []):
            valor_microscopica = buscar_en_microscopica(text, pattern)
            if valor_microscopica:
                # Normalizar el valor
                normalized = normalize_biomarker_value(
                    valor_microscopica,
                    definition.get('normalizacion', {}),
                    definition.get('tipo_valor', 'CATEGORICAL')
                )
                if normalized:
                    return normalized

        # V6.1.4: PRIORIDAD 3 - Buscar en texto completo (fallback final)
        # Casos donde el biomarcador está en secciones no estándar (ej: E-Cadherina en IHQ251008)
        for pattern in definition.get('patrones', []):
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                # Obtener valor capturado
                if match.groups():
                    raw_value = match.group(1).strip()
                else:
                    raw_value = match.group(0).strip()

                # Normalizar
                normalized = normalize_biomarker_value(
                    raw_value,
                    definition.get('normalizacion', {}),
                    definition.get('tipo_valor', 'CATEGORICAL')
                )
                if normalized:
                    return normalized

        return None

    # Lógica original continúa debajo (para biomarcadores sin prioridad de sección)
    # Intentar con cada patrón definido
    for pattern in definition.get('patrones', []):
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            # VALIDACIÓN ESPECIAL PARA KI67 v5.0.1
            # Verificar que NO estemos capturando porcentajes de otros campos
            if biomarker_name == 'KI67':
                match_start = match.start()
                context_before = text[max(0, match_start - 150):match_start].upper()

                # Si "DIFERENCIACIÓN" o "GLANDULAR" aparecen en los 150 caracteres previos, descartar
                if 'DIFERENCIACI' in context_before and 'GLANDULAR' in context_before:
                    continue

                # Si encontramos "MENOR DEL" justo antes del porcentaje, también descartar
                if 'MENOR DEL' in context_before[-30:]:
                    continue

            # Obtener el valor capturado, manejar casos sin grupos
            if match.groups():
                # V3.2.2: Manejar rangos (Ki67: 1-2%)
                if len(match.groups()) >= 2 and match.group(2):
                    # Es un rango, tomar el valor superior
                    raw_value = match.group(2).strip()
                else:
                    raw_value = match.group(1).strip()
            else:
                raw_value = match.group(0).strip()

            # V3.2.2: Manejo especial para "expresión limitada" → convertir a texto descriptivo
            if biomarker_name == 'KI67' and 'expresi' in raw_value.lower() and 'limitada' in raw_value.lower():
                return "EXPRESIÓN LIMITADA A CAPA BASAL"

            # Normalizar el valor
            normalized = normalize_biomarker_value(
                raw_value,
                definition.get('normalizacion', {}),
                definition.get('tipo_valor', 'CATEGORICAL')
            )

            return normalized

    return None


def normalize_biomarker_value(
    raw_value: str,
    specific_normalization: Dict[str, str],
    value_type: str = 'CATEGORICAL'
) -> str:
    """Normaliza el valor de un biomarcador

    v5.3.1: MEJORADO - Manejo de rangos (ej: "51-60%")
    v6.0.5: MEJORADO - Normalización de valores narrativos contaminados
    v6.1.7: CRÍTICO - Limpieza completa de \n, \r, \t + estandarización narrativa

    Args:
        raw_value: Valor extraído del texto
        specific_normalization: Normalización específica del biomarcador
        value_type: Tipo de valor ('CATEGORICAL', 'PERCENTAGE', 'NUMERIC')

    Returns:
        Valor normalizado
    """
    if not raw_value:
        return 'SIN DATO'

    # V6.1.7: LIMPIEZA COMPLETA - Eliminar \n, \r, \t y espacios múltiples
    import re
    value_clean = raw_value.strip()
    # Reemplazar \n, \r, \t con espacio
    value_clean = re.sub(r'[\n\r\t]+', ' ', value_clean)
    # Reemplazar espacios múltiples con uno solo
    value_clean = re.sub(r'\s+', ' ', value_clean)
    value_clean = value_clean.strip().upper()

    # V6.1.7: ESTANDARIZACIÓN NARRATIVA - Convertir formatos largos a POSITIVO/NEGATIVO + contexto
    # FORMATO: "POSITIVO/NEGATIVO" en mayúsculas + contexto en minúsculas entre paréntesis

    # Patrón 1: "NO ES CONTRIBUTIVA" / "NO CONTRIBUTIVA" → "NEGATIVO (no contributiva)"
    if re.search(r'^NO\s+ES\s+CONTRIBUTIV[AO]$', value_clean):
        return 'NEGATIVO (no contributiva)'
    if re.search(r'^NO\s+CONTRIBUTIV[AO]$', value_clean):
        return 'NEGATIVO (no contributiva)'

    # Patrón 2: "AUSENCIA DE EXPRESION PARA [BIOMARCADOR] (MUTADO)" → "NEGATIVO (mutado)"
    if re.search(r'^AUSENCIA\s+DE\s+EXPRESI[OÓ]N', value_clean):
        if 'MUTADO' in value_clean:
            return 'NEGATIVO (mutado)'
        return 'NEGATIVO (ausencia de expresión)'

    # Patrón 3: "LA EXPRESION PARA [BIOMARCADOR] ES POSITIVA (MUTADO)" → "POSITIVO (mutado)"
    # Patrón 4: "EXPRESION POSITIVA (MUTADO)" → "POSITIVO (mutado)"
    if re.search(r'EXPRESI[OÓ]N.*POSITIV[AO]', value_clean):
        if 'MUTADO' in value_clean:
            return 'POSITIVO (mutado)'
        return 'POSITIVO'

    # Patrón 5: "POSITIVO (MUTADO)" → "POSITIVO (mutado)"
    if re.search(r'^POSITIV[AO]\s*\(MUTADO\)$', value_clean):
        return 'POSITIVO (mutado)'

    # Patrón 6: "NEGATIVO (MUTADO)" → "NEGATIVO (mutado)"
    if re.search(r'^NEGATIV[AO]\s*\(MUTADO\)$', value_clean):
        return 'NEGATIVO (mutado)'

    # Patrón 7: "MARCACION POSITIVA PARA [BIOMARCADOR]" → "POSITIVO"
    if re.search(r'^MARCACI[OÓ]N\s+POSITIV[AO]', value_clean):
        return 'POSITIVO'

    # Patrón 8: "SIENDO NEGATIVA PARA [BIOMARCADOR]" → "NEGATIVO"
    if re.search(r'^SIENDO\s+NEGATIV[AO]', value_clean):
        return 'NEGATIVO'

    # V6.1.8: PATRONES ESPECÍFICOS DE CASOS HEMATOLÓGICOS (IHQ250992)
    # Patrón 9: "EXPRESIÓN DE [BIOMARCADOR]" → "POSITIVO"
    # Ejemplos: "EXPRESIÓN DE CD38", "EXPRESIÓN DE CD38 Y CD138"
    if re.search(r'^EXPRESI[OÓ]N\s+DE\s+', value_clean):
        return 'POSITIVO'

    # Patrón 10: "EXPRESIÓN ABERRANTE PARA [BIOMARCADOR]" → "POSITIVO (aberrante)"
    if re.search(r'EXPRESI[OÓ]N\s+ABERRANTE', value_clean):
        return 'POSITIVO (aberrante)'

    # Patrón 11: "RESTRICCIÓN DE CADENAS LIVIANAS [KAPPA/LAMBDA]" → "POSITIVO (restricción)"
    if re.search(r'RESTRICCI[OÓ]N\s+DE\s+CADENAS', value_clean):
        # Detectar si menciona KAPPA o LAMBDA
        if 'KAPPA' in value_clean:
            return 'POSITIVO (restricción kappa)'
        elif 'LAMBDA' in value_clean:
            return 'POSITIVO (restricción lambda)'
        else:
            return 'POSITIVO (restricción)'

    # Patrón 12: "EXPRESIÓN DÉBIL PARA [BIOMARCADOR]" → "POSITIVO (débil)"
    if re.search(r'EXPRESI[OÓ]N\s+D[ÉE]BIL', value_clean):
        return 'POSITIVO (débil)'

    # Patrón 13: "CON EXPRESIÓN DE [BIOMARCADOR]" → "POSITIVO"
    if re.search(r'^CON\s+EXPRESI[OÓ]N\s+DE', value_clean):
        return 'POSITIVO'

    # V6.0.13: NUEVO - Símbolo "+" al final → POSITIVO (IHQ250989: "CD20+", "CD38+")
    if value_clean.endswith('+'):
        return 'POSITIVO'
    # Símbolo "-" al final → NEGATIVO (raro pero posible)
    if value_clean.endswith('-') and not any(char.isdigit() for char in value_clean):
        return 'NEGATIVO'

    # V6.0.5: NUEVO - Detectar texto narrativo contaminado y normalizar
    # Ej: "POSITIVAS PARA CKAE1E3, CK7 Y CAM 5.2..." → "POSITIVO"
    if len(value_clean) > 20:  # Si es muy largo, probablemente sea narrativo
        # Buscar patrones narrativos de positividad
        if re.search(r'POSITIVAS?\s+PARA', value_clean):
            return 'POSITIVO'
        if re.search(r'NEGATIVAS?\s+PARA', value_clean):
            return 'NEGATIVO'
        # V6.0.12: NUEVO - "sin marcación para..." → NEGATIVO (IHQ250988)
        if re.search(r'SIN\s+MARCACI[ÓO]N\s+PARA', value_clean):
            return 'NEGATIVO'
        # V6.0.12: NUEVO - "sobreexpresión de..." → POSITIVO (IHQ250988)
        if re.search(r'SOBREEXPRESI[ÓO]N\s+DE', value_clean):
            return 'POSITIVO (SOBREEXPRESIÓN)'
        # Si contiene múltiples biomarcadores (comas y "Y"), es narrativo
        if ',' in value_clean and ' Y ' in value_clean:
            # Probablemente sea lista narrativa, marcar como POSITIVO por defecto
            return 'POSITIVO'

    # Intentar normalización específica primero
    if value_clean.lower() in specific_normalization:
        return specific_normalization[value_clean.lower()]

    # Intentar normalización global
    if value_clean.lower() in GLOBAL_VALUE_NORMALIZATION:
        return GLOBAL_VALUE_NORMALIZATION[value_clean.lower()]

    # Si es porcentaje, asegurar que tenga el símbolo %
    if value_type == 'PERCENTAGE' or value_type == 'NUMERIC':
        # V5.3.1: NUEVO - Manejar rangos (ej: "51-60")
        range_match = re.search(r'(\d{1,3})-(\d{1,3})', value_clean)
        if range_match:
            # Es un rango, conservarlo completo
            range_str = f"{range_match.group(1)}-{range_match.group(2)}"
            if value_type == 'PERCENTAGE' and '%' not in raw_value:
                return f"{range_str}%"
            return range_str

        # Extraer solo números (caso sin rango)
        number_match = re.search(r'(\d+)', value_clean)
        if number_match:
            number = number_match.group(1)
            # Agregar % si es porcentaje y no lo tiene
            if value_type == 'PERCENTAGE' and '%' not in raw_value:
                return f"{number}%"
            return number

    # Retornar valor limpio si no hay normalización disponible
    return value_clean


def get_biomarker_summary(biomarkers: Dict[str, str]) -> str:
    """Genera un resumen texto de los biomarcadores encontrados

    Args:
        biomarkers: Diccionario de biomarcadores extraídos

    Returns:
        String con resumen legible
    """
    if not biomarkers:
        return "No se encontraron biomarcadores"

    summary_parts = []
    for name, value in biomarkers.items():
        summary_parts.append(f"{name}: {value}")

    return " | ".join(summary_parts)


def validate_biomarker_value(biomarker_name: str, value: str) -> bool:
    """Valida si un valor es válido para un biomarcador

    Args:
        biomarker_name: Nombre del biomarcador
        value: Valor a validar

    Returns:
        True si el valor es válido
    """
    definition = get_biomarker_info(biomarker_name)
    if not definition:
        return False

    valores_posibles = definition.get('valores_posibles', [])

    # Si valores_posibles es una lista, verificar que esté en la lista
    if isinstance(valores_posibles, list):
        return value in valores_posibles or value.replace('%', '') in [str(v) for v in valores_posibles]

    # Si es un tipo (PERCENTAGE, NUMERIC), validar según el tipo
    if valores_posibles in ['PERCENTAGE', 'NUMERIC']:
        return bool(re.match(r'\d+%?', value))

    return True


# ======================== FUNCIONES DE COMPATIBILIDAD ========================

def extract_biomarkers_legacy_format(text: str) -> dict:
    """Wrapper para compatibilidad con código antiguo

    Mantiene el mismo formato de salida que procesador_ihq_biomarcadores.py
    """
    return extract_biomarkers(text)


def extract_narrative_biomarkers_list(texto_microscopica: str, biomarker_definitions: dict = None) -> Dict[str, str]:
    """Extrae biomarcadores de formato narrativo tipo LISTA en DESCRIPCIÓN MICROSCÓPICA.

    Versión: 6.0.3 - Corrección IHQ250982

    Reconoce patrones como:
    - "son positivas para CKAE1E3, CK7 Y CAM 5.2"
    - "positivas para GFAP, S100 y SOX10"
    - "expresan CK7, CK20 y TTF-1"
    - "muestran positividad para p16 y p40"

    NOTA: Esta función es COMPLEMENTARIA a extract_narrative_biomarkers() existente.
    - extract_narrative_biomarkers(): Patrones complejos tipo "RECEPTOR DE ESTRÓGENOS, positivo focal"
    - extract_narrative_biomarkers_list(): Listas tipo "positivas para X, Y, Z"

    Args:
        texto_microscopica: Texto de la sección DESCRIPCIÓN MICROSCÓPICA
        biomarker_definitions: Definiciones de biomarcadores (BIOMARKER_DEFINITIONS)

    Returns:
        Diccionario con biomarcadores detectados y valor POSITIVO
        Ejemplo: {'IHQ_CK7': 'POSITIVO', 'IHQ_CKAE1_AE3': 'POSITIVO'}

    Ejemplo:
        Input: "son positivas para CKAE1E3, CK7 Y CAM 5.2"
        Output: {'IHQ_CKAE1_AE3': 'POSITIVO', 'IHQ_CK7': 'POSITIVO', 'IHQ_CAM52': 'POSITIVO'}
    """
    if not texto_microscopica:
        return {}

    if biomarker_definitions is None:
        biomarker_definitions = BIOMARKER_DEFINITIONS

    resultados = {}

    # Patrones de formato narrativo tipo LISTA (ordenados por especificidad)
    # V6.0.4 FIX: Cambiado terminador para capturar TODA la lista, no solo el primer elemento
    # V6.0.5 FIX: Cambiado a greedy (+) y terminadores más específicos para capturar "CAM 5.2"
    # V6.0.5.1 FIX: Non-greedy para evitar capturar múltiples listas en una sola captura
    # V6.1.5 FIX IHQ251007: Agregado patrón "Hay positividad para celulas mioepiteliales X y Y"
    # Termina SOLO en: " y células" (con espacio antes de "y"), punto final, o fin de texto
    patrones_narrativo = [
        # V6.0.24: PRIORIDAD MÁXIMA - Patrones ultra-específicos para CD23, CD15, PAX5 (IHQ251009)
        # Patrón: "positividad fuerte para CD23" - captura solo el biomarcador en grupo 1
        r'positividad\s+(?:fuerte|d[eé]bil|moderada|leve)\s+para\s+([A-Z0-9]+)',
        # Patrón: "marcación para CD3, CD5, CD10, CD15" - captura lista con comas
        r'marcaci[óo]n\s+para\s+([A-Z0-9]+(?:,\s+[A-Z0-9]+)+)',
        # Patrón: "linfocitos positivos para CD20 y PAX5" - captura lista con "y"
        r'linfocitos\s+positivos\s+para\s+([A-Z0-9]+(?:\s+y\s+[A-Z0-9]+)+)',

        # V6.0.22: Nuevos patrones para casos hematológicos/linfomas (IHQ251009)
        # Patrón CRÍTICO: "linfocitos positivos para CD20 y PAX5" - captura "y" como separador
        r'linfocitos\s+positivos\s+para\s+([A-Z0-9]+\s+y\s+[A-Z0-9]+)',
        # Patrón: "Linfocitos T acompañantes CD3, CD5" - lista POST-sustantivo con comas
        r'[Ll]infocitos\s+T?\s*acompa[ñn]antes\s+([A-Z0-9]+(?:,\s+[A-Z0-9]+)+)',
        # Patrón: "positividad fuerte para CD23, débil para CD10 y BCL6" - captura CD23
        r'positividad\s+fuerte\s+para\s+([A-Z0-9]+)(?:,\s+d[eé]bil)',
        # Patrón complementario: "débil para CD10 y BCL6" - captura CD10 y BCL6
        r'd[eé]bil\s+para\s+([A-Z0-9]+\s+y\s+[A-Z0-9]+)',
        # Patrón genérico: "para CD138 y CD15" - captura conjunción "y"
        r'(?:para|con)\s+([A-Z0-9]+\s+y\s+[A-Z0-9]+)(?:\s|\.|\,)',

        # Patrones originales mejorados
        # Patrón: "linfocitos positivos para X..." - genérico
        r'linfocitos\s+(?:positivos|T|B)\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)\s+ubicados',
        r'linfocitos\s+(?:positivos|T|B)\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?:\s+y\s+[A-Z0-9]+)*\s+ubicados',
        # Patrón: "Presentan linfocitos positivos para X" - greedy para capturar toda la lista
        r'[Pp]resentan\s+linfocitos\s+positivos\s+para\s+([A-Z0-9\s,yY]+?)(?:\s+ubicados|\s+y\s+[A-Z])',
        # Patrón: "positividad fuerte/débil para CD23" - captura intensidades
        r'positividad\s+(?:fuerte|d[eé]bil|moderada)\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\s+y\s+|\.|\,)',
        # Patrón: "Marcación difusa/débil para MUM1/CD138" - POSITIVOS
        r'[Mm]arcaci[óo]n\s+(?:difusa|d[eé]bil|fuerte|moderada|esporadica|focal)\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\s+y\s+|\.|\,)',
        r'[Mm]arcaci[óo]n\s+(?:d[eé]bil|difusa)\s+y\s+esporadica.*?para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\s+y\s+|\.|\,)',
        # Patrón: "con marcación BCL2 positivos" - orden invertido
        r'con\s+marcaci[óo]n\s+([A-Z0-9]+)\s+positivos',
        # Patrón: "células plasmáticas positivas para CD38"
        r'c[eé]lulas\s+(?:plasm[aá]ticas|neoplásicas|tumorales)\s+positivas\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\s+y\s+|\.|\,)',

        # Patrones originales (mantener sin cambios)
        r'(?:son\s+)?positivas?\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)\s+y\s+c[eé]lulas',
        r'(?:son\s+)?positivas?\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\s+y\s+(?!c[eé]lulas)|\.|\n)',
        # V6.1.5: Nuevo patrón "Hay positividad para celulas mioepiteliales X y Y" (IHQ251007)
        r'(?:Hay|hay)\s+positividad\s+para\s+(?:celulas|células)\s+(?:mioepiteliales\s+)?([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\.|$)',
        r'expresan\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)\s+y\s+c[eé]lulas',
        r'expresan\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\s+y\s+(?!c[eé]lulas)|\.|\n)',
        r'muestran\s+positividad\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)\s+y\s+c[eé]lulas',
        r'muestran\s+positividad\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\s+y\s+(?!c[eé]lulas)|\.|\n)',
        r'con\s+marcaci[óo]n\s+positiva\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)\s+y\s+c[eé]lulas',
        r'con\s+marcaci[óo]n\s+positiva\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\s+y\s+(?!c[eé]lulas)|\.|\n)',
    ]

    for patron in patrones_narrativo:
        matches = re.finditer(patron, texto_microscopica, re.IGNORECASE)

        for match in matches:
            lista_texto = match.group(1).strip()

            # V6.0.5: Usar parser inteligente para procesar la lista
            biomarcadores_dict = parse_narrative_biomarker_list(lista_texto, biomarker_definitions)

            # Agregar biomarcadores encontrados (NO sobreescribir)
            for col, valor in biomarcadores_dict.items():
                if col not in resultados:
                    resultados[col] = valor

    return resultados


def parse_narrative_biomarker_list(biomarker_text: str, biomarker_definitions: Dict[str, Any] = None) -> Dict[str, str]:
    """Parsea una lista narrativa de biomarcadores y retorna diccionario con valores.

    Versión: 6.0.5 - Parser inteligente para listas narrativas de biomarcadores

    Ejemplos de entrada:
    - "CKAE1E3, CK7 Y CAM 5.2"
    - "GFAP, S100 y SOX10"
    - "HER2, Ki-67 y Receptor de Estrógenos"

    Args:
        biomarker_text: Texto con lista de biomarcadores (ej: "CKAE1E3, CK7 Y CAM 5.2")
        biomarker_definitions: Diccionario con definiciones de biomarcadores (BIOMARKER_DEFINITIONS)

    Returns:
        Dict con claves IHQ_* y valores "POSITIVO"

    Ejemplo:
        Input: "CKAE1E3, CK7 Y CAM 5.2"
        Output: {'IHQ_CKAE1AE3': 'POSITIVO', 'IHQ_CK7': 'POSITIVO', 'IHQ_CAM52': 'POSITIVO'}
    """
    if not biomarker_text:
        return {}

    if biomarker_definitions is None:
        biomarker_definitions = BIOMARKER_DEFINITIONS

    # Normalizar texto: quitar saltos de línea, múltiples espacios
    text_clean = ' '.join(biomarker_text.split())
    text_clean = text_clean.upper()

    # Dividir por delimitadores: coma, " Y ", " E "
    # Regex: split por coma O " Y " O " E " (con espacios)
    parts = re.split(r',|\s+[YE]\s+', text_clean, flags=re.IGNORECASE)

    # Limpiar cada parte y normalizar
    biomarkers_found = []
    for part in parts:
        part = part.strip()
        if part:
            biomarkers_found.append(part)

    # Mapear biomarcadores a columnas IHQ usando normalize_biomarker_name()
    result = {}

    for biomarker_raw in biomarkers_found:
        # Usar la función normalize_biomarker_name() existente
        columna_bd = normalize_biomarker_name(biomarker_raw)

        # Verificar que sea biomarcador válido y agregar prefijo IHQ_
        if columna_bd:
            # Agregar prefijo IHQ_ si no lo tiene
            if not columna_bd.startswith('IHQ_'):
                columna_bd = f'IHQ_{columna_bd}'

            result[columna_bd] = 'POSITIVO'

    return result


# ======================== EJEMPLO DE USO ========================

if __name__ == "__main__":
    # Ejemplo de uso
    sample_text = """
    Resultado de Inmunohistoquímica:
    HER2: 3+
    Ki-67: 25%
    Receptor de estrógenos: POSITIVO
    Receptor de progesterona: NEGATIVO
    PD-L1: 5%
    P16: POSITIVO
    P40: POSITIVO
    """

    biomarkers = extract_biomarkers(sample_text)
    logging.info("Biomarcadores extraídos:")
    for name, value in biomarkers.items():
        logging.info(f"  {name}: {value}")

    logging.info(f"\nResumen: {get_biomarker_summary(biomarkers)}")
