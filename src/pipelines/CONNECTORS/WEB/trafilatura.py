from trafilatura import fetch_url, extract

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, url : str) -> str:
        downloaded = fetch_url(url)
        result = extract(downloaded, include_tables = True)
        return result if result else "No content found."