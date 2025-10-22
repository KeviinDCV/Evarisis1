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
            # V5.3.1: PRIORIDAD 1 - Capturar RANGOS primero (ej: "51-60%")
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


def extract_biomarkers(text: str) -> Dict[str, str]:
    """Extrae todos los biomarcadores configurados del texto

    v5.3.1: MEJORADO - Prioriza sección REPORTE sobre descripción de anticuerpos

    Args:
        text: Texto del informe IHQ

    Returns:
        Diccionario con biomarcadores encontrados
        Ejemplo: {'HER2': 'POSITIVO', 'KI67': '25%', 'ER': 'POSITIVO'}
    """
    if not text:
        return {}

    results = {}

    # v5.3.1: NUEVO - Extraer sección REPORTE primero
    report_section = extract_report_section(text)
    search_text = report_section if report_section else text

    # NUEVA FUNCIÓN: Detectar formato narrativo de biomarcadores
    # Buscar PRIMERO en sección REPORTE si existe
    narrative_results = extract_narrative_biomarkers(search_text)
    results.update(narrative_results)

    # Procesar cada biomarcador definido en configuración (método original)
    # Buscar PRIMERO en sección REPORTE si existe
    for biomarker_name, definition in BIOMARKER_DEFINITIONS.items():
        # Solo procesar si no fue encontrado por método narrativo
        if biomarker_name not in results:
            # Intentar primero en sección REPORTE
            value = extract_single_biomarker(search_text, biomarker_name, definition)

            # Si no se encontró en REPORTE y existe sección REPORTE, buscar en texto completo como fallback
            if not value and report_section:
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
        r'(?i)inmunorreactividad\s+(?:fuerte\s+y\s+)?difusa\s+para\s+((?:[^\.\n]+(?:\n[A-Z0-9/]+)?)+)',
        r'(?i)presentan\s+inmuno\s*marcaci[óo]n\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+((?:[^\.\n]+(?:\n[A-Z0-9/]+)?)+)'
    ]
    
    for pattern in complex_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            biomarker_name = None
            
            # Mapeo específico para cada patrón
            if 'estr' in pattern.lower():
                biomarker_name = 'ER'
            elif 'progesterona' in pattern.lower():
                biomarker_name = 'PR'
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
                # Para patrones que capturan grupo, tomar el resultado
                value = 'POSITIVO' if match[0].lower() == 'positivo' else 'NEGATIVO'
                results[biomarker_name] = value
    
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
    negative_pattern = r'(?i)negativas?\s+para\s+(.+?)(?:$|\.|;)'
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
        'CDX2': 'CDX2',
        'CDX-2': 'CDX2',
        'CDX 2': 'CDX2',
        'EMA': 'EMA',
        'E.M.A': 'EMA',
        'SOX10': 'SOX10',
        'SOX-10': 'SOX10',
        'SOX 10': 'SOX10',
        'SOXIO': 'SOX10',  # OCR error común 1->I->O
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
