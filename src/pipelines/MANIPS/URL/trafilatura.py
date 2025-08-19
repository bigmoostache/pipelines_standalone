from trafilatura import fetch_url, extract
from trafilatura.settings import use_config
from custom_types.URL.type import URL

newconfig = use_config()
newconfig.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

class Pipeline:
    def __init__(self, ignore_if_success:bool = True):
        self.ignore_if_success = ignore_if_success

    def __call__(self, url : URL) -> URL:
        if self.ignore_if_success and url.success:
            return url
        downloaded = fetch_url(url.url)
        try:
            result = extract(downloaded, include_tables = True, config=newconfig)
        except TypeError as e:
            return url
        if result:
            url.success = True
            url.text = result
        return url