import io
 
import fitz
from docx import Document
 
 
def extract_text_from_pdf(data):
    pdf = fitz.open(stream=data, filetype="pdf")
    text = "\n".join(page.get_text() for page in pdf)
    pdf.close()
    return text
 
 
def extract_text_from_docx(data):
    document = Document(io.BytesIO(data))
    parts = [paragraph.text for paragraph in document.paragraphs]
 
    # Many resume templates use tables, so read them too.
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.append(cell.text)
 
    return "\n".join(parts)
 
 
def extract_text(filename, data):
    """Read a PDF or DOCX given its file name and raw bytes."""
    name = (filename or "").lower()
 
    if name.endswith(".pdf"):
        return extract_text_from_pdf(data)
    if name.endswith(".docx"):
        return extract_text_from_docx(data)
 
    raise ValueError("Unsupported file type. Upload a PDF or DOCX.")
 