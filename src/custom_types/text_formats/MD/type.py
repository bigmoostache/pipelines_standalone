from pydantic import BaseModel
class MD(BaseModel):
    md: str
    
class Converter:
    @staticmethod
    def to_bytes(MD) -> bytes:
        return bytes(MD.md, 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> MD:
        return MD(md=b.decode('utf-8'))
    @staticmethod
    def len(txt : MD) -> int:
        return max(1, len(MD.md) // 1048576)
    
    
import pdfkit
import tempfile
from custom_types.PDF.type import PDF
import markdown2

class Pipeline:
    def __init__(self):
        self.config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

    def __call__(self, md : MD) -> PDF:
        # Create a temporary file
        html = markdown2.markdown(md.md)
        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
            # Convert HTML to PDF and save to the temporary file
            pdfkit.from_string(html.html, temp_file.name, configuration=self.config)
            # Read the PDF file content and return as bytes
            temp_file.seek(0)
            pdf_bytes = temp_file.read()
        return PDF(pdf_bytes)
        
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='md',
    _class = MD,
    converter = Converter,
    additional_converters={
        'json':lambda x : {'__text__':x},
        'txt': lambda x : x.md,
        'pdf': lambda x : Pipeline()(x),
        },
    visualiser = "https://vis.deepdocs.net/md"
)
