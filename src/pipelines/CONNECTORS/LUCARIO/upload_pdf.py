from typing import List
from custom_types.URL2.type import URL2
from custom_types.PDF.type import PDF
from googleapiclient.discovery import build
import os 
import requests
from PyPDF2 import PdfReader
from datetime import datetime
import io

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, pdf: PDF) -> URL2:
        headers = {
            'accept': 'application/json',
        }

        files = {
            'file': ('article.pdf', pdf.file_as_bytes, 'application/pdf')
        }

        response = requests.post('https://lucario.croquo.com/files', headers=headers, files=files)
        response.raise_for_status()
        url = response.json()['file_name']
        
        pdf_stream = io.BytesIO(pdf.file_as_bytes)
        reader = PdfReader(pdf_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
        return URL2(
            url=url, 
            title='Uploaded PDF', 
            description='Uploaded PDF',
            images=[],
            text=text,
            html="", 
            date=datetime.now().isoformat()
            )