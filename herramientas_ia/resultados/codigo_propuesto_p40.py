# CÓDIGO PROPUESTO PARA CORRECCIÓN P40
# Fecha: 2025-10-24
# Caso: IHQ250983
# Archivo: core/extractors/biomarker_extractor.py
# Líneas a modificar: 178-195

# ============================================================================
# SECCIÓN A REEMPLAZAR EN BIOMARKER_DEFINITIONS
# ============================================================================

"""
BUSCAR EN biomarker_extractor.py (línea 178):
    'P40': {

REEMPLAZAR desde línea 178 hasta línea 195 (incluye cierre de diccionario)
"""

# ----------------------------------------------------------------------------
# CODIGO ANTERIOR (PROBLEMATICO):
# ----------------------------------------------------------------------------

CODIGO_ANTERIOR = r"""
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
"""

# ----------------------------------------------------------------------------
# CODIGO NUEVO (CORREGIDO):
# ----------------------------------------------------------------------------

CODIGO_NUEVO = r"""
    'P40': {
        'nombres_alternativos': ['P-40', 'P 40'],
        'descripcion': 'Proteína p40',
        'patrones': [
            # V6.0.10: Patrones específicos con modificadores (FIX: IHQ250983)
            # Captura: "p40 positivo heterogéneo", "p40 heterogéneo", "p40 positivo"
            # CRÍTICO: Patrones específicos evitan captura de basura contextual
            r'(?i)p40[:\s]+(positiv[oa](?:\s+(?:heterog[eé]neo|focal|difuso))?)',
            r'(?i)p40[:\s]+(negativ[oa](?:\s+focal)?)',
            r'(?i)p40[:\s]+(heterog[eé]neo)',  # Solo heterogéneo = POSITIVO HETEROGÉNEO
            r'(?i)p40[:\s]+(focal)',  # Solo focal = POSITIVO FOCAL
            r'(?i)p40[:\s]+(difuso)',  # Solo difuso = POSITIVO DIFUSO
            r'(?i)p[^\w]*40[:\s]+(positiv[oa]|negativ[oa])',  # Con separador (P-40, P 40)
            # Fallback conservador
            r'(?i)p40[:\s]*(positivo|negativo)',
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO', 'POSITIVO HETEROGÉNEO', 'POSITIVO FOCAL', 'POSITIVO DIFUSO', 'NEGATIVO FOCAL'],
        'normalizacion': {
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
            '+': 'POSITIVO',
            '-': 'NEGATIVO',
            # V6.0.10: Modificadores (FIX: IHQ250983)
            'heterogéneo': 'POSITIVO HETEROGÉNEO',
            'heterogeneo': 'POSITIVO HETEROGÉNEO',
            'focal': 'POSITIVO FOCAL',
            'difuso': 'POSITIVO DIFUSO',
            'positivo heterogéneo': 'POSITIVO HETEROGÉNEO',
            'positivo heterogeneo': 'POSITIVO HETEROGÉNEO',
            'positivo focal': 'POSITIVO FOCAL',
            'positivo difuso': 'POSITIVO DIFUSO',
            'negativo focal': 'NEGATIVO FOCAL',
        }
    },
"""

# ============================================================================
# VALIDACIÓN DE SINTAXIS
# ============================================================================

def validar_sintaxis():
    """Valida que el código propuesto sea Python válido"""
    import ast

    # Crear diccionario completo para validar sintaxis
    test_dict = f"""
{{
{CODIGO_NUEVO}
}}
"""

    try:
        ast.parse(test_dict)
        print("OK - Sintaxis valida")
        return True
    except SyntaxError as e:
        print(f"ERROR - Error de sintaxis: {e}")
        return False


# ============================================================================
# CASOS DE PRUEBA
# ============================================================================

def test_patrones():
    """Prueba los patrones regex contra casos conocidos"""
    import re

    # Extraer patrones del código nuevo
    patrones = [
        r'(?i)p40[:\s]+(positiv[oa](?:\s+(?:heterog[eé]neo|focal|difuso))?)',
        r'(?i)p40[:\s]+(negativ[oa](?:\s+focal)?)',
        r'(?i)p40[:\s]+(heterog[eé]neo)',
        r'(?i)p40[:\s]+(focal)',
        r'(?i)p40[:\s]+(difuso)',
        r'(?i)p[^\w]*40[:\s]+(positiv[oa]|negativ[oa])',
        r'(?i)p40[:\s]*(positivo|negativo)',
    ]

    casos_prueba = [
        # (texto, valor_esperado_capturado)
        ("p40 heterogéneo", "heterogéneo"),
        ("p40 positivo", "positivo"),
        ("p40 positivo heterogéneo", "positivo heterogéneo"),
        ("p40 positivo focal", "positivo focal"),
        ("p40 negativo", "negativo"),
        ("p40 negativo focal", "negativo focal"),
        ("p40 focal", "focal"),
        ("p40 difuso", "difuso"),
        ("P-40 positivo", "positivo"),
        ("P 40 negativo", "negativo"),
        ("y p40 heterogéneo y son", "heterogéneo"),  # Caso IHQ250983
    ]

    print("\nPRUEBAS DE PATRONES:\n")

    for texto, esperado in casos_prueba:
        encontrado = False
        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                capturado = match.group(1).strip()
                resultado = "OK" if capturado.lower() == esperado.lower() else "FAIL"
                print(f"{resultado} '{texto}' -> Capturo: '{capturado}' (Esperado: '{esperado}')")
                encontrado = True
                break

        if not encontrado:
            print(f"FAIL '{texto}' -> NO CAPTURO NADA (Esperado: '{esperado}')")


# ============================================================================
# INSTRUCCIONES DE APLICACIÓN
# ============================================================================

INSTRUCCIONES = """
================================================================================
                    INSTRUCCIONES DE APLICACION
================================================================================

1. ABRIR ARCHIVO:
   C:\\Users\\drestrepo\\Documents\\ProyectoHUV9GESTOR_ONCOLOGIA_automatizado\\core\\extractors\\biomarker_extractor.py

2. LOCALIZAR LÍNEA 178:
   Buscar: 'P40': {

3. SELECCIONAR DESDE LÍNEA 178 HASTA LÍNEA 195 (incluye cierre de diccionario)
   Seleccionar TODO el diccionario P40 completo hasta el cierre con },

4. REEMPLAZAR CON EL CÓDIGO NUEVO (ver arriba en CODIGO_NUEVO)

5. GUARDAR ARCHIVO

6. VALIDAR SINTAXIS:
   python herramientas_ia/editor_core.py --validar-sintaxis biomarker_extractor.py

7. REPROCESAR CASO DE PRUEBA:
   python herramientas_ia/editor_core.py --reprocesar IHQ250983

8. VERIFICAR CORRECCIÓN:
   python herramientas_ia/gestor_base_datos.py --buscar IHQ250983 --detallado

   VERIFICAR QUE:
   IHQ_P40_ESTADO = "POSITIVO HETEROGÉNEO" (no ", S100 Y CKAE1AE3")

9. AUDITAR CON IA:
   python herramientas_ia/auditor_sistema.py IHQ250983 --inteligente

10. SI TODO OK, ACTUALIZAR VERSION:
    python herramientas_ia/gestor_version.py --actualizar patch --mensaje "Fix: Correccion extractor P40 con modificadores (IHQ250983)"

================================================================================
                              IMPORTANTE
================================================================================

- CREAR BACKUP ANTES DE MODIFICAR:
  El archivo biomarker_extractor.py se respaldará automáticamente en backups/
  cuando uses editor_core.py

- SI USAS EDITOR MANUAL:
  Copia manualmente biomarker_extractor.py a backups/ antes de modificar

- VERIFICAR OTROS CASOS:
  Después de validar IHQ250983, buscar otros casos con P40:

  python herramientas_ia/gestor_base_datos.py --buscar-avanzado --biomarcadores IHQ_P40_ESTADO

"""


# ============================================================================
# EJECUCIÓN DE VALIDACIONES
# ============================================================================

if __name__ == "__main__":
    print("=" * 78)
    print("VALIDACION DE CODIGO PROPUESTO PARA CORRECCION P40".center(78))
    print("=" * 78 + "\n")

    print("Validando sintaxis Python...")
    if validar_sintaxis():
        print("\nProbando patrones regex...")
        test_patrones()
        print("\n" + INSTRUCCIONES)
        print("\nVALIDACION COMPLETADA - CODIGO LISTO PARA APLICAR")
    else:
        print("\nERROR: Codigo tiene errores de sintaxis. REVISAR antes de aplicar.")
