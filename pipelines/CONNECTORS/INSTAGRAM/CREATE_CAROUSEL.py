import os, requests
from typing import List
from urllib.parse import urlparse

class Pipeline:
    __env__ = ["instagram_access_token", "ig_user_id"]
    def __init__(self):
        pass
    def __call__(self, 
                 ids : List[dict],
                 carousel_caption : str
                 ) -> dict:
        ids = [_.get('id') for _ in ids if 'id' in _]
        instagram_access_token = os.environ.get("instagram_access_token")
        ig_user_id = os.environ.get("ig_user_id")
        params = {
            'media_type': 'CAROUSEL',
            'access_token': instagram_access_token,
            'children' : ids,
            'caption' : carousel_caption
        }
        response = requests.post(f'https://graph.facebook.com/v19.0/{ig_user_id}/media', json=params)
        return response.json()