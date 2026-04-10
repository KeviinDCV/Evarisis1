
REPORTE DE REPROCESAMIENTO IHQ250037 - HHV8
===========================================

CASO: IHQ250037
BIOMARCADOR: HHV8
VALOR ESPERADO: NEGATIVO (según OCR: 'HHV8 negativo.')

ESTADO ACTUAL:
--------------
✅ Patrón de extracción agregado correctamente en biomarker_extractor.py
   - Patrones: 3 regex funcionando
   - Normalización: 'negativo' -> 'NEGATIVO' correcta

✅ Extractor validado con OCR del caso:
   - Input: 'HHV8 negativo.'
   - Output: 'HHV8: NEGATIVO'
   - STATUS: ✅ CORRECTO

⚠️  Debug_map actual obsoleto:
   - Generado a las 03:50 AM (antes de agregar patrón HHV8)
   - IHQ_HHV8 en BD: 'NO MENCIONADO' (incorrecto)
   - Requiere: Reprocesamiento completo del PDF

PRÓXIMOS PASOS:
---------------
1. El usuario debe reprocesar el PDF 'IHQ DEL 001 AL 050.pdf' usando la interfaz ui.py
2. Alternativamente, ejecutar FUNC-06 nuevamente:
   python -c "from herramientas_ia.auditor_sistema import AuditorSistema; AuditorSistema().reprocesar_caso_completo('IHQ250037')"
3. Verificar score final con FUNC-01:
   python herramientas_ia/auditor_sistema.py IHQ250037 --inteligente

RESULTADO ESPERADO:
-------------------
Score: 100% (9/9 campos OK)
IHQ_HHV8: NEGATIVO


