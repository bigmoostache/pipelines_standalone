import os, requests
from typing import List
from urllib.parse import urlparse

class Pipeline:
    __env__ = ["medium_token", "medium_user_id"]
    def __init__(self, markdown : bool = True):
        self.markdown = markdown
    def __call__(self, 
                 title : str,
                 content : str,
                 tags : List[str],
                 canonical_url : str
                 ) -> dict:
        medium_token = os.environ.get("medium_token")
        medium_user_id = os.environ.get("medium_user_id")
        p = {
            "title" : title,
            "contentFormat" : 'markdown' if self.markdown else 'html',
            "content" : content,
            'tags' : tags,
            "canonicalUrl" : canonical_url
        }
        r = requests.post(
            f'https://api.medium.com/v1/users/{medium_user_id}/posts',
            params={"accessToken": medium_token}, 
            json = p)
        return r.json()