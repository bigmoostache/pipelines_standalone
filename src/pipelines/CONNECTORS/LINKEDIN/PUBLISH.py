import os, requests
from typing import List
from urllib.parse import urlparse

class Pipeline:
    __env__ = ["medium_token", "medium_user_id"]
    def __init__(self, markdown : bool = True):
        """
        You will need 
        1. To have a linkedin app
        2. fetch the client id and the primary client secret in th Auth tab
        3. add https://oauth.pstmn.io/v1/callback and https://oauth.pstmn.io/v1/browser-callback to callback urls, same page
        """
        pass
    def __call__(self, 
                 title : str,
                 content : str,
                 tags : List[str],
                 canonical_url : str
                 ) -> dict:
        pass