
from custom_types.URL.type import URL
from gnews import GNews

class Pipeline:
    def __init__(self, ignore_if_success :bool= True):
        self.ignore_if_success = ignore_if_success

    def __call__(self, url : URL) -> URL:
        if self.ignore_if_success and url.success:
            return url
        google_news = GNews()
        r = google_news.get_full_article(url.url)
        if r is not None:
            url.text = r.text 
            url.success = True 
        return url
        