import pdfkit
import tempfile
from custom_types.HTML.type import HTML
from custom_types.PDF.type import PDF


class Pipeline:
    def __init__(self):
        self.config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

    def __call__(self, html : HTML) -> PDF:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
            # Convert HTML to PDF and save to the temporary file
            pdfkit.from_string(html.html, temp_file.name, configuration=self.config)
            # Read the PDF file content and return as bytes
            temp_file.seek(0)
            pdf_bytes = temp_file.read()
        return PDF(pdf_bytes)