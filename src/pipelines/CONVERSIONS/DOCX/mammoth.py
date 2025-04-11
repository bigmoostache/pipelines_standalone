import mammoth
 
from custom_types.DOCX.type import DOCX
from custom_types.HTML.type import HTML
import io
from bs4 import BeautifulSoup
class Pipeline:
    def __init__(self,
                 body_only: bool = False,
                 ):
        self.body_only = body_only
        
    def __call__(self, docx: DOCX) -> HTML:
        with io.BytesIO(docx.file_as_bytes) as file_like:
            result = mammoth.convert_to_html(file_like)
            html_content = result.value
        if not self.body_only:
            return HTML(html=html_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        body = soup.body
        if body is None:
            return HTML(html=html_content)
        return HTML(html=str(body))