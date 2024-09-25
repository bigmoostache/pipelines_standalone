from custom_types.URL2.type import URL2
import requests

class Pipeline:
    def __init__(self, ignore_if_success :bool= True):
        self.ignore_if_success = ignore_if_success

    def __call__(self, url : URL2, telegraphic : str) -> URL2:
        url.telegraphic = telegraphic
        return url