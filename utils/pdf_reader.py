from typing import List
from PyPDF2 import PdfReader

def extract_text_from_pdfs(paths: List[str]) -> str:
    chunks = []
    for p in paths:
        try:
            reader = PdfReader(p)
            pages = [pg.extract_text() or "" for pg in reader.pages]
            chunks.append("\n".join(pages))
        except Exception as e:
            chunks.append(f"[ERROR leyendo {p}: {e}]")
    return "\n\n".join(chunks)
