from pypdf import PdfReader
import io

class PDF:
    def __init__(self, file_as_bytes):
        self.file_as_bytes = file_as_bytes
    def __repr__(self):
        return self.file_as_bytes
    def __str__(self):
        return self.file_as_bytes

class Converter:
    extension = 'pdf'
    @staticmethod
    def to_bytes(pdf : PDF) -> bytes:
        return pdf.file_as_bytes
    @staticmethod
    def from_bytes(b: bytes) -> PDF:
        return PDF(b)
    @staticmethod
    def str_preview(pdf: PDF) -> str:
        return f"File of {len(pdf.file_as_bytes)} bytes"
    @staticmethod
    def len(pdf : PDF) -> int:
        # number of pages
        pdf_stream = io.BytesIO(pdf.file_as_bytes)
        reader = PdfReader(pdf_stream)   
        return len(reader.pages)   

from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='pdf',
    _class = PDF,
    converter = Converter,
    icon="/icons/pdf.svg"
)