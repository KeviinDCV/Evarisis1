#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extractor de biomarcadores IHQ

Extrae biomarcadores con configuración integrada (antes en config/patterns/biomarker_patterns.py)

Versión: 5.0.0 - CONSOLIDADO
Autor: Sistema HUV Refactorizado
Nota: Toda la configuración de patrones está ahora en este archivo para centralización
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
        'nombres_alternativos': ['RECEPTORES ESTROGENOS', 'RE', 'ESTROGENO', 'ESTRÓGENO'],
        'descripcion': 'Receptores de estrógenos',
        'patrones': [
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
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'umbral_positividad': 1,
        'usa_prioridad_seccion': True,  # V6.0.0
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
        }
    },

    'PR': {
        'nombres_alternativos': ['RECEPTORES PROGESTERONA', 'RP', 'PROGESTERONA', 'PROGRESTERONA'],
        'descripcion': 'Receptores de progesterona',
        'patrones': [
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
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'umbral_positividad': 1,
        'usa_prioridad_seccion': True,  # V6.0.0
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
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
        }
    },

    'P40': {
        'nombres_alternativos': ['P-40', 'P 40'],
        'descripcion': 'Proteína p40',
        'patrones': [
            # V5.2: Captura TODO el contexto
            r'(?i)p40[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)p[^\w]*40[:\s]*(.+?)(?:\.|$|\n)',
            # Fallback
            r'(?i)p40[:\s]*(positivo|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
        }
    },

    'P53': {
        'nombres_alternativos': ['P-53', 'P 53'],
        'descripcion': 'Proteína supresora tumoral p53',
        'patrones': [
            # V5.2: Captura "con sobreexpresión", porcentajes, intensidad
            r'(?i)p53[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)p[^\w]*53[:\s]*(.+?)(?:\.|$|\n)',
            # Fallback
            r'(?i)p53[:\s]*(positivo|negativo|\d+%)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'CDX2': {
        'nombres_alternativos': ['CDX-2', 'CDX 2'],
        'descripcion': 'Factor de transcripción CDX2',
        'patrones': [
            r'(?i)cdx2[:\s]*(positivo|negativo)',
            r'(?i)cdx[^\w]*2[:\s]*(positivo|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
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
            r'(?i)marcaci[óo]n\s+(positiva|negativa)\s+para[:\s]+E[\s-]?CADHERINA',
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
    'CD3': {
        'nombres_alternativos': ['CD-3'],
        'descripcion': 'Cluster de diferenciación 3',
        'patrones': [
            r'(?i)cd[^\w]*3[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*3(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*3(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'CD5': {
        'nombres_alternativos': ['CD-5'],
        'descripcion': 'Cluster de diferenciación 5',
        'patrones': [
            r'(?i)cd[^\w]*5[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*5(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*5(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
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

    'CD20': {
        'nombres_alternativos': ['CD-20'],
        'descripcion': 'Cluster de diferenciación 20',
        'patrones': [
            r'(?i)cd[^\w]*20[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*20(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*20(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
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
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'CD38': {
        'nombres_alternativos': ['CD-38'],
        'descripcion': 'Cluster de diferenciación 38',
        'patrones': [
            r'(?i)cd[^\w]*38[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*38(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*38(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
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
            r'(?i)cd[^\w]*56[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)positivas?\s+para\s+.*?cd\s*56(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*56(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
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
            r'(?i)cd[^\w]*117[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)c[^\w]*kit[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?cd\s*117(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*117(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }
    },

    'CD138': {
        'nombres_alternativos': ['CD-138', 'SYNDECAN-1'],
        'descripcion': 'Cluster de diferenciación 138',
        'patrones': [
            r'(?i)cd[^\w]*138[:\s]*(positivo|negativo|\d+%?)',
            r'(?i)syndecan[^\w]*1[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+para\s+.*?cd\s*138(?:\s|,|$)',
            r'(?i)negativas?\s+para\s+.*?cd\s*138(?:\s|,|$)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'PERCENTAGE'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
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
        'nombres_alternativos': ['CKAE1/AE3', 'CK AE1/AE3', 'CITOQUERATINA AE1/AE3', 'CAM 5.2'],
        'descripcion': 'Citoqueratinas pancitoqueratina',
        'patrones': [
            r'(?i)CKAE1[/\s]*AE3[:\s]*(positivo|negativo)',
            r'(?i)CK\s+AE1[/\s]*AE3[:\s]*(positivo|negativo)',
            r'(?i)CAM\s+5\.2[:\s]*(positivo|negativo)',
            r'(?i)positivas?\s+.*?para\s+CKAE1[/\s]*AE3',
            r'(?i)negativas?\s+.*?para\s+CKAE1[/\s]*AE3',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'positiva': 'POSITIVO',
            'negativo': 'NEGATIVO',
            'negativa': 'NEGATIVO',
        }
    },

    # V5.3: MARCADORES MMR (Mismatch Repair) - CRÍTICOS PARA INESTABILIDAD MICROSATELITAL
    'MLH1': {
        'nombres_alternativos': ['MLH-1', 'MLH 1'],
        'descripcion': 'Proteína de reparación de ADN MLH1',
        'patrones': [
            # Formato especial: "Expresión nuclear intacta" o "Pérdida de expresión nuclear"
            r'(?i)MLH1[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)MLH[^\w]*1[:\s]*(.+?)(?:\.|$|\n)',
            # Patrones específicos para MMR
            r'(?i)MLH1[:\s]*Expresi[óo]n\s+nuclear\s+(intacta|ausente|p[ée]rdida)',
            r'(?i)MLH1[:\s]*(intacta|ausente|positivo|negativo)',
        ],
        'valores_posibles': ['ESTABLE', 'INESTABLE', 'INTACTA', 'AUSENTE'],
        'normalizacion': {
            'intacta': 'ESTABLE',
            'expresión nuclear intacta': 'ESTABLE',
            'expresion nuclear intacta': 'ESTABLE',
            'ausente': 'INESTABLE',
            'pérdida': 'INESTABLE',
            'perdida': 'INESTABLE',
            'pérdida de expresión': 'INESTABLE',
            'positivo': 'ESTABLE',
            'negativo': 'INESTABLE',
        }
    },

    'MSH2': {
        'nombres_alternativos': ['MSH-2', 'MSH 2'],
        'descripcion': 'Proteína de reparación de ADN MSH2',
        'patrones': [
            r'(?i)MSH2[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)MSH[^\w]*2[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)MSH2[:\s]*Expresi[óo]n\s+nuclear\s+(intacta|ausente|p[ée]rdida)',
            r'(?i)MSH2[:\s]*(intacta|ausente|positivo|negativo)',
        ],
        'valores_posibles': ['ESTABLE', 'INESTABLE', 'INTACTA', 'AUSENTE'],
        'normalizacion': {
            'intacta': 'ESTABLE',
            'expresión nuclear intacta': 'ESTABLE',
            'expresion nuclear intacta': 'ESTABLE',
            'ausente': 'INESTABLE',
            'pérdida': 'INESTABLE',
            'perdida': 'INESTABLE',
            'pérdida de expresión': 'INESTABLE',
            'positivo': 'ESTABLE',
            'negativo': 'INESTABLE',
        }
    },

    'MSH6': {
        'nombres_alternativos': ['MSH-6', 'MSH 6', 'MSH6 Y'],  # "MSH6 Y" es un error común de OCR
        'descripcion': 'Proteína de reparación de ADN MSH6',
        'patrones': [
            r'(?i)MSH6[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)MSH[^\w]*6[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)MSH6[:\s]*Expresi[óo]n\s+nuclear\s+(intacta|ausente|p[ée]rdida)',
            r'(?i)MSH6[:\s]*(intacta|ausente|positivo|negativo)',
        ],
        'valores_posibles': ['ESTABLE', 'INESTABLE', 'INTACTA', 'AUSENTE'],
        'normalizacion': {
            'intacta': 'ESTABLE',
            'expresión nuclear intacta': 'ESTABLE',
            'expresion nuclear intacta': 'ESTABLE',
            'ausente': 'INESTABLE',
            'pérdida': 'INESTABLE',
            'perdida': 'INESTABLE',
            'pérdida de expresión': 'INESTABLE',
            'positivo': 'ESTABLE',
            'negativo': 'INESTABLE',
        }
    },

    'PMS2': {
        'nombres_alternativos': ['PMS-2', 'PMS 2'],
        'descripcion': 'Proteína de reparación de ADN PMS2',
        'patrones': [
            r'(?i)PMS2[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)PMS[^\w]*2[:\s]*(.+?)(?:\.|$|\n)',
            r'(?i)PMS2[:\s]*Expresi[óo]n\s+nuclear\s+(intacta|ausente|p[ée]rdida)',
            r'(?i)PMS2[:\s]*(intacta|ausente|positivo|negativo)',
        ],
        'valores_posibles': ['ESTABLE', 'INESTABLE', 'INTACTA', 'AUSENTE'],
        'normalizacion': {
            'intacta': 'ESTABLE',
            'expresión nuclear intacta': 'ESTABLE',
            'expresion nuclear intacta': 'ESTABLE',
            'ausente': 'INESTABLE',
            'pérdida': 'INESTABLE',
            'perdida': 'INESTABLE',
            'pérdida de expresión': 'INESTABLE',
            'positivo': 'ESTABLE',
            'negativo': 'INESTABLE',
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

    v6.0.2: MEJORADO - Prioriza "Expresión molecular" > REPORTE > texto completo (IHQ250981)

    Args:
        text: Texto del informe IHQ

    Returns:
        Diccionario con biomarcadores encontrados
        Ejemplo: {'HER2': 'POSITIVO', 'KI67': '25%', 'ER': 'POSITIVO'}
    """
    if not text:
        return {}

    results = {}

    # v6.0.2: PRIORIDAD 1 - Extraer sección "Expresión molecular" PRIMERO (caso IHQ250981)
    molecular_section = extract_molecular_expression_section(text)

    # v5.3.1: PRIORIDAD 2 - Extraer sección REPORTE (descripción microscópica)
    report_section = extract_report_section(text)

    # Definir biomarcadores que deben priorizarse de "Expresión molecular"
    molecular_priority = ['ER', 'PR', 'HER2', 'RECEPTOR_ESTROGENOS', 'RECEPTOR_PROGESTERONA']

    # NUEVA FUNCIÓN: Detectar formato narrativo de biomarcadores
    # Para ER, PR, HER2: Buscar PRIMERO en "Expresión molecular"
    if molecular_section:
        narrative_results = extract_narrative_biomarkers(molecular_section)
        results.update(narrative_results)

    # Si no encontró en "Expresión molecular", buscar en REPORTE
    if not results and report_section:
        narrative_results = extract_narrative_biomarkers(report_section)
        results.update(narrative_results)

    # Si aún no encontró, buscar en texto completo
    if not results:
        narrative_results = extract_narrative_biomarkers(text)
        results.update(narrative_results)

    # Procesar cada biomarcador definido en configuración (método original)
    for biomarker_name, definition in BIOMARKER_DEFINITIONS.items():
        # Solo procesar si no fue encontrado por método narrativo
        if biomarker_name not in results:
            value = None

            # Para biomarcadores prioritarios: buscar PRIMERO en "Expresión molecular"
            if biomarker_name.upper() in molecular_priority and molecular_section:
                value = extract_single_biomarker(molecular_section, biomarker_name, definition)

            # Si no encontró en molecular, buscar en REPORTE
            if not value and report_section:
                value = extract_single_biomarker(report_section, biomarker_name, definition)

            # Si no se encontró en REPORTE, buscar en texto completo como fallback
            if not value:
                value = extract_single_biomarker(text, biomarker_name, definition)

            if value:
                results[biomarker_name] = value

    return results


def extract_narrative_biomarkers(text: str) -> Dict[str, str]:
    """Extrae biomarcadores del formato narrativo tipo:
    'células neoplásicas son fuertemente positivas para CK7 y GATA 3 y EMA, negativas para CK20, SOX10 y CDX2'
    Y formatos complejos como 'RECEPTOR DE ESTRÓGENOS, positivo focal'
    """
    results = {}
    
    # Patrón NUEVO: Biomarcadores complejos tipo "RECEPTOR DE ESTRÓGENOS, positivo focal"
    complex_patterns = [
        # V6.0.2: NUEVOS PATRONES para "Expresión molecular" (IHQ250981) - PRIORIDAD MÁXIMA
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
            elif 'progesterona' in pattern.lower():
                biomarker_name = 'PR'
            elif 'her' in pattern.lower():
                biomarker_name = 'HER2'
            elif 'gata' in pattern.lower():
                biomarker_name = 'GATA3'
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

            if biomarker_name and isinstance(match, str):
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
        # Dividir por "y" y normalizar nombres
        positive_biomarkers = [b.strip() for b in re.split(r'\s+y\s+', positive_list)]
        
        for biomarker in positive_biomarkers:
            normalized_name = normalize_biomarker_name(biomarker)
            if normalized_name:
                results[normalized_name] = 'POSITIVO'
    
    # Patrón 2: "negativas para X, Y y Z"
    # V6.0.6: Mejorado para capturar "son negativas para X, Y y Z"
    negative_pattern = r'(?i)(?:son\s+)?negativas?\s+para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9]+)*?)(?:\s*\.|\s*,\s+y\s+son|$)'
    negative_match = re.search(negative_pattern, text)
    
    if negative_match:
        negative_list = negative_match.group(1)
        # Dividir por "y" y "," y normalizar nombres
        negative_biomarkers = []
        for part in re.split(r',\s*', negative_list):
            negative_biomarkers.extend([b.strip() for b in re.split(r'\s+y\s+', part)])
        
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
        r'(?i)(p16|p40|s100|her2|her-2|ki67|ki-67|ck7|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2|er|pr|cd3|cd5|cd10|cd20|cd30|cd34|cd38|cd45|cd56|cd61|cd68|cd117|cd138|sox10|vimentina|chromogranina|synaptophysin|melan-a)\s+(positivo|negativo|focal)',
        r'(?i)(p16|p40|s100|her2|her-2|ki67|ki-67|ck7|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2|er|pr|cd3|cd5|cd10|cd20|cd30|cd34|cd38|cd45|cd56|cd61|cd68|cd117|cd138|sox10|vimentina|chromogranina|synaptophysin|melan-a)\s*:\s*(positivo|negativo|focal)',
        r'(?i)(pl6)\s+(positivo|negativo|focal)',  # Variante pl6 en lugar de p16
    ]

    # Patrón 4B: "El marcador X es positivo/negativo" - CRÍTICO PARA CASO IHQ250009
    single_marker_patterns = [
        r'(?i)el\s+marcador\s+(p16|p40|s100|her2|her-2|ki67|ki-67|ck7|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2)\s+es\s+(positivo|negativo|focal)',
        r'(?i)marcador\s+(p16|p40|s100|her2|her-2|ki67|ki-67|ck7|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2)\s+es\s+(positivo|negativo|focal)',
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
    compound_negative_pattern = r'(?i)((?:p16|p40|s100|her2|her-2|ki67|ki-67|ck7|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2)(?:\s+y\s+(?:p16|p40|s100|her2|her-2|ki67|ki-67|ck7|ck20|ttf1|ttf-1|cdx2|ema|gata3|cdk4|mdm2))*)\s+negativos'
    
    for match in re.finditer(compound_negative_pattern, text):
        compound = match.group(1)
        markers = [m.strip() for m in re.split(r'\s+y\s+', compound)]
        
        for marker in markers:
            normalized_name = normalize_biomarker_name(marker)
            if normalized_name:
                results[normalized_name] = 'NEGATIVO'
    
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
        'KI67': 'KI67',
        'KI-67': 'KI67',
        'ER': 'ER',
        'PR': 'PR',
        # RECEPTORES LARGOS - CRÍTICO PARA CASOS COMPLEJOS
        'RECEPTOR DE ESTRÓGENOS': 'ER',
        'RECEPTOR DE ESTROGENOS': 'ER',
        'RECEPTOR DE PROGESTERONA': 'PR',
        'RECEPTORES DE ESTRÓGENOS': 'ER',
        'RECEPTORES DE ESTROGENOS': 'ER',
        'RECEPTORES DE PROGESTERONA': 'PR',
        # Biomarcadores P
        'P16': 'P16',
        'PL6': 'P16',  # pl6 es variante de p16
        'P40': 'P40',
        'S100': 'S100',
        'TTF1': 'TTF1',
        'TTF-1': 'TTF1',
        'P53': 'P53',
        'CDK4': 'CDK4',
        'MDM2': 'MDM2',
        # Biomarcadores CD - CRÍTICOS PARA CASOS 2-10
        'CD3': 'CD3',
        'CD5': 'CD5',
        'CD10': 'CD10',
        'CD20': 'CD20',
        'CD30': 'CD30',
        'CD34': 'CD34',
        'CD38': 'CD38',
        'CD45': 'CD45',
        'CD56': 'CD56',
        'CD61': 'CD61',
        'CD68': 'CD68',
        'CD117': 'CD117',
        'CD138': 'CD138',
        # Otros biomarcadores
        'VIMENTINA': 'VIMENTINA',
        'VIMENTIN': 'VIMENTINA',
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

    Args:
        raw_value: Valor extraído del texto
        specific_normalization: Normalización específica del biomarcador
        value_type: Tipo de valor ('CATEGORICAL', 'PERCENTAGE', 'NUMERIC')

    Returns:
        Valor normalizado
    """
    if not raw_value:
        return 'SIN DATO'

    # Limpiar el valor
    value_clean = raw_value.strip().upper()

    # V6.0.5: NUEVO - Detectar texto narrativo contaminado y normalizar
    # Ej: "POSITIVAS PARA CKAE1E3, CK7 Y CAM 5.2..." → "POSITIVO"
    if len(value_clean) > 20:  # Si es muy largo, probablemente sea narrativo
        # Buscar patrones narrativos de positividad
        if re.search(r'POSITIVAS?\s+PARA', value_clean):
            return 'POSITIVO'
        if re.search(r'NEGATIVAS?\s+PARA', value_clean):
            return 'NEGATIVO'
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
    # Termina SOLO en: " y células" (con espacio antes de "y"), punto final, o fin de texto
    patrones_narrativo = [
        r'(?:son\s+)?positivas?\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)\s+y\s+c[eé]lulas',
        r'(?:son\s+)?positivas?\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\s+y\s+(?!c[eé]lulas)|\.|\n)',
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
