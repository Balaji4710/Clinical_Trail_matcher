import pdfplumber
def extract_text_from_pdf(file_path: str) -> str:
    chunks: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                chunks.append(page_text)
    return "\n\n".join(chunks).strip()
