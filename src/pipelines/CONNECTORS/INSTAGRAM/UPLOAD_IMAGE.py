import os, requests
from typing import List
from urllib.parse import urlparse

class Pipeline:
    __env__ = ["instagram_access_token", "ig_user_id"]
    def __init__(self, 
                 as_carousel : bool = False):
        self.as_carousel = as_carousel
    def __call__(self, 
                 image_url : str,
                 image_caption : str
                 ) -> dict:
        instagram_access_token = os.environ.get("instagram_access_token")
        ig_user_id = os.environ.get("ig_user_id")
        params = {
            'image_url': image_url,
            'access_token': instagram_access_token,
            'is_carousel_item' : self.as_carousel,
            'caption' : image_caption
        }
        response = requests.post(f'https://graph.facebook.com/v19.0/{ig_user_id}/media', params=params)
        return response.json()