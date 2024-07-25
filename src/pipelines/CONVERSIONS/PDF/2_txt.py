from custom_types.PDF.type import PDF
from pypdf import PdfReader
import io

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, pdf : PDF) -> str:
        pdf_stream = io.BytesIO(pdf.file_as_bytes)
        reader = PdfReader(pdf_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text