from custom_types.URL2.type import URL2
import requests
from custom_types.PDF.type import PDF
from pypdf import PdfReader
from datetime import datetime
import io

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, pdf: PDF, project_id : str) -> URL2:
        headers = {
            'accept': 'application/json',
        }

        files = {
            'file': ('article.pdf', pdf.file_as_bytes, 'application/pdf')
        }

        
        params= {
                "project_id": project_id 
            } 
        

        response = requests.post('https://lucario.deepdocs.net/files', headers=headers, files=files, params=params)
        response.raise_for_status()
        url = response.json()['file_name']
        
        pdf_stream = io.BytesIO(pdf.file_as_bytes)
        reader = PdfReader(pdf_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
        return URL2.init(url=f'https://lucario.deepdocs.net/files?file={url}', title='Uploaded PDF', date=datetime.now().isoformat())