# -*- coding: utf-8 -*-
"""V6.9.63 — COLA DE REVISIÓN + AUDITORÍA de la polaridad de biomarcadores.

El extractor NO adivina: cuando sus dos lentes no coinciden sobre un marcador, conserva el
valor previo y lo encola aquí. Esta herramienta muestra esa cola y la auditoría completa.

  python herramientas_ia/cola_revision.py              -> resumen
  python herramientas_ia/cola_revision.py --revision   -> los marcadores a revisar
  python herramientas_ia/cola_revision.py --auditoria  -> todo lo corregido, con su cita
  python herramientas_ia/cola_revision.py --caso IHQ250839
  python herramientas_ia/cola_revision.py --csv salida.csv
"""
import os
import sys
import json
import csv
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(RAIZ, 'auditoria')
F_AUD = os.path.join(DIR, 'polaridad_auditoria.jsonl')
F_REV = os.path.join(DIR, 'polaridad_revision.jsonl')


def leer(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
    return out


def resumen(aud, rev):
    print('=' * 68)
    print('POLARIDAD DE BIOMARCADORES — estado')
    print('=' * 68)
    print(f'  Corregidos por la IA (con cita del informe): {len(aud)}')
    print(f'  PENDIENTES DE REVISIÓN (el sistema no supo): {len(rev)}')
    if aud:
        print('\n  correcciones por marcador (top 8):')
        for c, n in Counter(x.get('columna', '?') for x in aud).most_common(8):
            print(f'     {n:4}  {c}')
    if rev:
        print('\n  a revisar por marcador (top 8):')
        for c, n in Counter(x.get('columna', '?') for x in rev).most_common(8):
            print(f'     {n:4}  {c}')
        print(f'\n  casos implicados: {len({x.get("caso") for x in rev})}')
    print('\n  (--revision para verlos · --auditoria para el detalle · --csv para exportar)')


def ver_revision(rev):
    """Dos clases de ítem, con significados MUY distintos — no confundirlos:
      CAMBIO_APLICADO_PENDIENTE_DE_CONFIRMAR -> la IA ya cambió el valor; confírmalo.
      LENTES_DISCREPAN_NO_SE_TOCO            -> la IA no supo; el valor sigue como estaba.
    """
    apl = [x for x in rev if x.get('motivo') == 'CAMBIO_APLICADO_PENDIENTE_DE_CONFIRMAR']
    dud = [x for x in rev if x.get('motivo') != 'CAMBIO_APLICADO_PENDIENTE_DE_CONFIRMAR']

    if apl:
        print(f'▶ {len(apl)} CAMBIOS APLICADOS — la IA los cambió, CONFÍRMALOS contra la cita:\n')
        for x in apl:
            print(f"  {x.get('caso')}  {x.get('columna')}")
            print(f"     {x.get('valor_previo')}  ->  {x.get('valor_actual')}   (ya está en la BD)")
            cita = (x.get('cita') or '').strip()
            if cita:
                print(f"     dice el informe: «{cita[:100]}»")
            print()
    if dud:
        print(f'▶ {len(dud)} DUDOSOS — la IA NO supo; el valor NO se tocó, decide tú:\n')
        for x in dud:
            print(f"  {x.get('caso')}  {x.get('columna')}")
            print(f"     valor actual (sin tocar) : {x.get('valor_actual')}")
            print(f"     lente A dice             : {x.get('lente_a')}")
            print(f"     lente B dice             : {x.get('lente_b')}")
            cita = (x.get('cita') or '').strip()
            if cita:
                print(f"     cita del informe         : «{cita[:100]}»")
            print()
    if not rev:
        print('Nada pendiente de revisar.')


def ver_auditoria(aud):
    print(f'{len(aud)} CORRECCIONES, cada una con la cita que la respalda:\n')
    for x in aud:
        print(f"  {x.get('caso')}  {x.get('columna')}: {x.get('antes')} -> {x.get('despues')}")
        print(f"     «{(x.get('cita') or '')[:100]}»")


def exportar(aud, rev, ruta):
    with open(ruta, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['tipo', 'caso', 'columna', 'antes', 'despues', 'lente_a', 'lente_b', 'cita'])
        for x in aud:
            w.writerow(['CORREGIDO', x.get('caso'), x.get('columna'), x.get('antes'),
                        x.get('despues'), '', '', x.get('cita')])
        for x in rev:
            w.writerow(['REVISAR', x.get('caso'), x.get('columna'), x.get('valor_actual'), '',
                        x.get('lente_a'), x.get('lente_b'), x.get('cita')])
    print(f'-> {ruta}  ({len(aud) + len(rev)} filas)')


def main():
    aud, rev = leer(F_AUD), leer(F_REV)
    if not aud and not rev:
        print('No hay auditoría todavía. Se genera al procesar PDFs con '
              'usar_ia_polaridad = true en config.ini')
        return
    a = sys.argv[1:]
    if '--caso' in a:
        c = a[a.index('--caso') + 1].upper()
        aud = [x for x in aud if str(x.get('caso', '')).upper() == c]
        rev = [x for x in rev if str(x.get('caso', '')).upper() == c]
        print(f'--- {c} ---\n')
        ver_auditoria(aud)
        print()
        ver_revision(rev)
        return
    if '--csv' in a:
        exportar(aud, rev, a[a.index('--csv') + 1])
        return
    if '--revision' in a:
        ver_revision(rev)
        return
    if '--auditoria' in a:
        ver_auditoria(aud)
        return
    resumen(aud, rev)


if __name__ == '__main__':
    main()
