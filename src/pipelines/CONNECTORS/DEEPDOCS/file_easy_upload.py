from custom_types.URL2.type import URL2
import requests
from datetime import datetime
import io, os

class Pipeline:
    def __init__(self,
                 directory: str = '/Uploads/'  # Default directory for uploads
                 ):
        self.directory = directory

    def __call__(self, 
                 doc: bytes, 
                 doc_name : str) -> URL2:
        FILES_URL = os.environ['FILES_URL']
        PIPELINE_ID = os.environ['FACTORY_ID']
        TOKEN_HASH = os.environ['TOKEN_HASH']
        FILE_TOKEN_HASH = os.environ['FILE_TOKEN_HASH']
        
        headers = {
            'accept': 'application/json',
        }

        params = {
            'factory_id': PIPELINE_ID,
            'token_sha_256': TOKEN_HASH,
            'file_token_sha_256': FILE_TOKEN_HASH,
            'directory': self.directory,
        }

        files = {
            'file': (doc_name, doc, 'application/octet-stream')
        }

        response = requests.post(f'{FILES_URL}/file/pipelines/post_file', params=params, headers=headers, files=files)
        
        response.raise_for_status()
        
        dic = response.json()
        return URL2.init(url=dic['url'])