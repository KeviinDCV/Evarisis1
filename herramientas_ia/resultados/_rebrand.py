# -*- coding: utf-8 -*-
"""Rebrand Evarisis -> Onconova. Alcance: app activa + documentacion.
Respeta el casing (EVARISIS->ONCONOVA, Evarisis->Onconova, evarisis->onconova,
mixto->Onconova). Excluye backups, venv0, .git, .claude (worktree), VERSION_MAC,
pyside6_ui, datos. Reporta cada archivo cambiado (auditoria)."""
import os, re, json

ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
OUT = ROOT + r"\herramientas_ia\resultados\_rebrand_report.json"

EXCLUDE_DIRS = {'venv0', '.git', '.claude', 'VERSION_MAC', 'pyside6_ui',
                '__pycache__', 'node_modules', '.vscode', 'EXCEL',
                'pdfs_patologia', 'debug_maps', 'backups', 'resultados'}
EXCLUDE_FILE_SUBSTR = ['.backup', 'ui copy.py', 'main_pyside6.py', 'requirements_pyside6.txt']
ALLOWED_EXT = {'.py', '.bat', '.txt', '.md', '.js', '.html'}

pat = re.compile(r'evarisis', re.IGNORECASE)

def repl(m):
    s = m.group(0)
    if s.isupper():
        return 'ONCONOVA'
    if s.islower():
        return 'onconova'
    if s[0].isupper():
        return 'Onconova'
    return 'Onconova'

report = {'changed': [], 'errors': [], 'skipped_excluded_with_match': []}
total_files = 0
total_repl = 0

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower()
        if ext not in ALLOWED_EXT:
            continue
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT)
        try:
            with open(full, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            try:
                with open(full, 'r', encoding='cp1252') as f:
                    content = f.read()
            except Exception as e:
                report['errors'].append({'file': rel, 'error': str(e)[:120]})
                continue
        if not pat.search(content):
            continue
        if any(sub in fn for sub in EXCLUDE_FILE_SUBSTR):
            report['skipped_excluded_with_match'].append(rel)
            continue
        new, n = pat.subn(repl, content)
        if new != content:
            try:
                with open(full, 'w', encoding='utf-8') as f:
                    f.write(new)
                report['changed'].append({'file': rel, 'replacements': n})
                total_files += 1
                total_repl += n
            except Exception as e:
                report['errors'].append({'file': rel, 'error': str(e)[:120]})

report['total_files'] = total_files
report['total_replacements'] = total_repl
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(json.dumps({'total_files': total_files, 'total_replacements': total_repl,
                  'changed': report['changed'],
                  'skipped_excluded_with_match': report['skipped_excluded_with_match'],
                  'errors': report['errors']}, ensure_ascii=False, indent=2))
