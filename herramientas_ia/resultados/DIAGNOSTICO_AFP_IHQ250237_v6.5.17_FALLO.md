# DIAGNÓSTICO: AFP Extracción Incorrecta IHQ250237 (v6.5.17 FALLÓ)

## PROBLEMA
- **Caso:** IHQ250237
- **Biomarcador:** IHQ_AFP
- **Valor BD:** POSITIVO
- **Valor Esperado:** NEGATIVO
- **Modificación:** v6.5.17 agregó filtro "PARA TINCIÓN CON"
- **Resultado:** FALLÓ - AFP sigue siendo POSITIVO

## ANÁLISIS DEL OCR

**Mención 1 (DESCRIPCIÓN MACROSCÓPICA - debe excluirse):**
```
tinción con los marcadores: SALL 4, PODOPLANINA, GLYPICAN 3, AFP, CD 30, CKAE1E3
```
- **Contexto:** Lista de estudios solicitados
- **Acción esperada:** EXCLUIR (no es un resultado)
- **Resultado:** NO SE EXCLUYÓ (filtro falló)

**Mención 2 (DESCRIPCIÓN MICROSCÓPICA - resultado real):**
```
es negativo para GLYPICAN 3, AFP y CD 30
```
- **Contexto:** Resultado de IHQ
- **Valor:** NEGATIVO
- **Acción esperada:** EXTRAER ESTE VALOR

## CAUSA RAÍZ

El filtro v6.5.17 agregó:
```python
contextos_excluidos = [
    'PARA TINCIÓN CON',  # V6.5.17 FIX IHQ250237
    'PARA TINCION CON',  # V6.5.17 FIX IHQ250237
]
```

**Problema identificado:**
1. El texto OCR dice: "para tinción con **los marcadores:**"
2. El filtro busca: `'PARA TINCIÓN CON' in contexto_previo`
3. Esto **DEBERÍA hacer match** (substring match)
4. **PERO NO FUNCIONA** → Posible problema con tamaño del contexto_previo

## HIPÓTESIS

El `contexto_previo` que se evalúa NO incluye suficientes caracteres antes del biomarcador "AFP" para capturar el texto "PARA TINCIÓN CON".

**Verificación necesaria:**
- ¿Cuántos caracteres incluye `contexto_previo`?
- ¿El patrón regex captura AFP antes de llegar al contexto "tinción con"?

## SOLUCIÓN PROPUESTA

**Opción 1: Aumentar ventana de contexto**
```python
# En vez de usar contexto limitado, buscar en ventana más amplia
contexto_previo = texto_antes_del_match[-200:].upper()  # Aumentar de 100 a 200
```

**Opción 2: Patrón regex más específico para AFP**
```python
'AFP': {
    'nombres_alternativos': ['ALFA-FETOPROTEINA', 'ALFAFETOPROTEINA', ...],
    'descripcion': 'Alfa-fetoproteína',
    'patrones': [
        # Patrón negativo explícito
        r'(?i)(?:es\s+)?negativo?\s+para\s+.*?AFP',
        # Patrón de lista (múltiples marcadores)
        r'(?i)(?:positivo|negativo)\s+para\s+[^.]{0,50}?\bAFP\b',
    ]
}
```

**Opción 3: Filtro más robusto con regex**
```python
# En vez de substring match, usar regex con flexibilidad
patron_exclusion = r'(?i)para\s+tinci[óo]n\s+con\s+(?:los\s+)?marcadores'
if re.search(patron_exclusion, contexto_previo):
    continue  # Excluir
```

## SIGUIENTE PASO

Implementar **Opción 3** (filtro regex más flexible) porque:
- Más robusto ante variaciones textuales
- No requiere aumentar ventana (más eficiente)
- Captura "para tinción con", "para tinción con los marcadores", etc.

