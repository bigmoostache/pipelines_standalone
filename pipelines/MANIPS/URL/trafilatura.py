from trafilatura import fetch_url, extract
from custom_types.URL.type import URL

class Pipeline:
    def __init__(self, ignore_if_success:bool = True):
        self.ignore_if_success = ignore_if_success

    def __call__(self, url : URL) -> URL:
        if self.ignore_if_success and url.success:
            return url
        downloaded = fetch_url(url.url)
        result = extract(downloaded, include_tables = True)
        if result:
            url.success = True
            url.text = result
        return url