import fitz  # PyMuPDF

pdf_path = r'c:\Users\drestrepo\Documents\ProyectoHUV9GESTOR_ONCOLOGIA\pdfs_patologia\IHQ DEL 108 AL 159.pdf'
search_term = "IHQ250133"

try:
    doc = fitz.open(pdf_path)
    found = False
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        if search_term in text:
            print(f"Found {search_term} on page {page_num + 1}")
            # Print some context
            start = text.find(search_term)
            print(text[max(0, start-100):min(len(text), start+500)])
            found = True
            break
    if not found:
        print(f"{search_term} not found in PDF")
    doc.close()
except Exception as e:
    print(f"Error reading PDF: {e}")
