#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

text = '-RECEPTOR DE ESTROGENOS: Negativo.'

# Patrón actual (NO funciona)
pattern1 = r'(?i)-\s*RECEPTORES?\s+DE\s+ESTR[ÓO]GENO[S]?\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?'
match1 = re.search(pattern1, text)
print('Patrón 1 (actual):', match1)

# Patrón corregido
pattern2 = r'(?i)-\s*RECEPTOR(?:ES)?\s+DE\s+ESTR[ÓO]GENO[S]?\s*:\s*(POSITIV[OA]S?|NEGATIV[OA]S?)\.?'
match2 = re.search(pattern2, text)
print('Patrón 2 (corregido):', match2)
if match2:
    print('Groups:', match2.groups())
    print('Group 1:', match2.group(1))
