from custom_types.URL.type import URL
import requests

class Pipeline:
    def __init__(self, ignore_if_success :bool= True):
        self.ignore_if_success = ignore_if_success

    def __call__(self, url : URL) -> URL:
        try:
            response = requests.get(url.url, allow_redirects=True)
            if response.url:
                url.url = response.url
        except:
            pass 
        return url