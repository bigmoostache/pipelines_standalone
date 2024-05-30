import urllib.parse
import tldextract

def get_base_domain(url):
    parsed_url = urllib.parse.urlparse(url)
    extracted = tldextract.extract(parsed_url.netloc)
    base_domain = "{}.{}".format(extracted.domain, extracted.suffix)
    return base_domain


class Pipeline:
    def __init__(self):
        pass        
    def __call__(self, url : str) -> str:
        return get_base_domain(url)