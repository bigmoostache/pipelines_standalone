from custom_types.LUCARIO.type import LUCARIO
from custom_types.PDF.type import PDF
from typing import List
from time import sleep
class Pipeline:
    def __init__(self,
                lucario_url: str = 'https://lucario.deepdocs.net'
                 ):
        self.lucario_url = lucario_url
    
    def __call__(self, 
                 pdfs: List[PDF]) -> LUCARIO:
        l = LUCARIO.get_new(self.lucario_url)
        for pdf in pdfs:
            l.post_file(pdf.file_as_bytes, pdf.file_name)
        l.update()
        return l 