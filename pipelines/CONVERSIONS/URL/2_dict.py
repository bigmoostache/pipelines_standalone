from custom_types.URL.type import URL

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, url : URL) -> dict:
        return url.__dict__