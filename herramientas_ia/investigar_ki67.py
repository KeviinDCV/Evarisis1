# -*- coding: utf-8 -*-
import json
import re

# Load debug map
with open('data/debug_maps/debug_map_IHQ250044_20251011_031743.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract IHQ250044 text
text = data['ocr']['texto_original']
start = text.find('IHQ250044')
end = text.find('IHQ250045')
caso_text = text[start:end] if end > 0 else text[start:start+5000]

print("=" * 80)
print("INVESTIGACIÓN Ki-67 IHQ250044")
print("=" * 80)

# Search for all percentage mentions
print("\n### BUSCANDO '10%' en el texto:")
for match in re.finditer(r'10%', caso_text):
    start_pos = max(0, match.start() - 60)
    end_pos = min(len(caso_text), match.end() + 60)
    context = caso_text[start_pos:end_pos]
    print(f"\nEncontrado en posición {match.start()}:")
    print(f"  ...{context}...")

print("\n\n### BUSCANDO '20%' en el texto:")
for match in re.finditer(r'20%', caso_text):
    start_pos = max(0, match.start() - 60)
    end_pos = min(len(caso_text), match.end() + 60)
    context = caso_text[start_pos:end_pos]
    print(f"\nEncontrado en posición {match.start()}:")
    print(f"  ...{context}...")

print("\n\n### BUSCANDO 'Ki' (case-insensitive) en el texto:")
for match in re.finditer(r'[Kk]i[\s-]?67', caso_text, re.IGNORECASE):
    start_pos = max(0, match.start() - 80)
    end_pos = min(len(caso_text), match.end() + 80)
    context = caso_text[start_pos:end_pos]
    print(f"\nEncontrado en posición {match.start()}: '{match.group()}'")
    print(f"  ...{context}...")

print("\n" + "=" * 80)
