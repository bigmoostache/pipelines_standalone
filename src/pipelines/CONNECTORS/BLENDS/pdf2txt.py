import requests, json
from custom_types.PDF.type import PDF
from pypdf import PdfReader 
from io import BytesIO


class Pipeline:
    def __init__(self):
        pass 

    def __call__(self, pdf : PDF) -> str:
        try:
            bytes_io = BytesIO(pdf.file_as_bytes)
            reader = PdfReader(bytes_io)
            text = '\n'.join([_.extract_text() for _ in reader.pages])
            return text
        except:
            return "Error extracting text from PDF"