from gnews import GNews

class Pipeline:

    def __init__(self):
        pass
    def __call__(self, query: dict) -> dict:
        google_news = GNews()
        r = google_news.get_full_article(query['url'])
        if r is None:
            query["success"] = False
            return query
        query['text'] = r.text
        query["success"] = True
        return query