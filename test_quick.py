import re

# Texto SIN acentos (como queda después de limpiar Unicode)
texto = "Sin embargo se reconoce un foco de 1 mm ( corresponde a 3 glandulas) con perdida de expresion para CK34 BETA E12 y P63 con marcacion positiva para Racemasa."

print("Texto:", texto)
print()

# Test patrón complejo
pattern = r'(?i)(?:p[e]rdida|ausencia)\s+de\s+expresi[oa]n\s+para[:\s]+(.+?)\s+con\s+marcaci[oa]n\s+(positiva|negativa)\s+para[:\s]+(.+?)(?:\.|$)'
match = re.search(pattern, texto, re.DOTALL)

print("Patron complejo:", pattern)
print("Match encontrado:", match is not None)

if match:
    print("\nGrupos:")
    print("  Grupo 1 (negativos):", match.group(1))
    print("  Grupo 2 (estado):", match.group(2))
    print("  Grupo 3 (positivos):", match.group(3))
else:
    print("\nNO MATCH - Intentando patron simple de 'perdida'")

    # Test patrón simple
    pattern_simple = r'(?i)(?:p[e]rdida|ausencia|sin)\s+de\s+expresi[oa]n\s+para[:\s]+(.+?)(?:\s+con\s+marcaci[oa]n|\.|$)'
    match_simple = re.search(pattern_simple, texto, re.DOTALL)

    print("Patron simple:", pattern_simple)
    print("Match encontrado:", match_simple is not None)

    if match_simple:
        print("  Grupo 1:", match_simple.group(1))
