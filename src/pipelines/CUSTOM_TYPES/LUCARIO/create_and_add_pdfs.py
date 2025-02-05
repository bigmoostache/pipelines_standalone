from custom_types.LUCARIO.type import LUCARIO
from custom_types.PDF.type import PDF
from typing import List

class Pipeline:
    def __init__(self,
                lucario_url: str = 'https://lucario.croquo.com'
                 ):
        self.lucario_url = lucario_url
    
    def __call__(self, 
                 pdfs: List[PDF]) -> LUCARIO:
        l = LUCARIO.get_new(lucario_url)
        for pdf in pdfs:
            doc = l.post_file(pdf.file_as_bytes, 'document.pdf')
            l.add_document(doc)
        l.update()
        return l 