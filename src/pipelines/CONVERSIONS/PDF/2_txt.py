from custom_types.PDF.type import PDF
from pypdf import PdfReader
from typing import Literal
import io
import os
import requests
import time

class Pipeline:
    __env__ = ["surya_api_key"]
    def __init__(self,
                 method : Literal['normal', 'surya'] = 'normal',
                 surya_url : str = "https://www.datalab.to/api/v1/marker"
                 ):
        self.method = method
        self.surya_url = surya_url
    def __call__(self, pdf : PDF) -> str:
        if self.method == 'surya':
            form_data = {
                'file': ('document.pdf', pdf.file_as_bytes, 'application/pdf'),
                'langs': (None, "English"),
                "force_ocr": (None, False),
                "paginate": (None, False)
            }
            headers = {"X-Api-Key": os.environ.get("surya_api_key")}
            response = requests.post(self.surya_url, files=form_data, headers=headers)
            data = response.json()
            max_polls = 300
            check_url = data["request_check_url"]

            for i in range(max_polls):
                time.sleep(2)
                response = requests.get(check_url, headers=headers)
                data = response.json()

                if data["status"] == "complete":
                    break
            text = data['markdown']
            return text
        else:
            pdf_stream = io.BytesIO(pdf.file_as_bytes)
            reader = PdfReader(pdf_stream)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text