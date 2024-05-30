import requests, json
from custom_types.PDF.type import PDF

class Pipeline:
    def __init__(self):
        pass 

    def __call__(self, pdf : PDF) -> str:
        headers = {
            'accept': 'application/json'
        }

        params = {
            'return_images': 'false',
        }

        files = {
            'file': ('file.pdf', pdf.file_as_bytes, 'application/pdf'),
        }

        response = requests.post('http://172.16.100.121:7177/uploadfile/', params=params, headers=headers, files=files)
        x = json.loads(response.text)
        return x.get("md", "")