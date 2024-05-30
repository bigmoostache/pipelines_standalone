import os, requests
from typing import List
from urllib.parse import urlparse

class Pipeline:
    __env__ = ["instagram_access_token", "ig_user_id"]
    def __init__(self):
        pass
    def __call__(self, 
                 media_id : dict
                 ) -> dict:
        if 'id' not in media_id:
            return {'success' : False}
        media_id = media_id.get('id')
        instagram_access_token = os.environ.get("instagram_access_token")
        ig_user_id = os.environ.get("ig_user_id")
        params = {
            'access_token': instagram_access_token,
            'creation_id' : media_id,
        }
        response = requests.post(f'https://graph.facebook.com/v19.0/{ig_user_id}/media_publish', json=params)
        return response.json()