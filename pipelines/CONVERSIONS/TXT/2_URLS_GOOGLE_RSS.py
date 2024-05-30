from typing import List
from custom_types.URL.type import URL
from urllib.parse import quote
import os 
import feedparser
import base64
from urllib.parse import urlparse
from datetime import datetime, timedelta
import requests
class Pipeline:
    __env__ = ["SCRAPING_BEE"]
    def __init__(self, n_days : int = 30):
        self.n_days = 30 

    def __call__(self, query: str) -> List[URL]:
        encoded_query = quote(query)
        SCRAPING_BEE_KEY = os.getenv('SCRAPING_BEE')
        proxies = {
                    "http": f"http://{SCRAPING_BEE_KEY}:render_js=False&premium_proxy=False@proxy.scrapingbee.com:8886",
                    "https": f"https://{SCRAPING_BEE_KEY}:render_js=False&premium_proxy=False@proxy.scrapingbee.com:8887"
                }
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&ceid=US:en&hl=en-US&gl=US"
        response = requests.get(
                    url=rss_url,
                    proxies=proxies,
                    verify=False
                )
        feed = feedparser.parse(response.text)
        
        def process_url(url):
            parsed_url = urlparse(url)
            # Check if the domain is 'news.google.com'
            if parsed_url.netloc == 'news.google.com':
                # Extract the part of the URL that seems to be encoded
                encoded_str = parsed_url.path.split('/')[-1]
                # Calculate the required padding
                padding = '=' * ((4 - len(encoded_str) % 4) % 4)
                # Decode the string with the added padding
                try:
                    decoded_bytes = str(base64.b64decode(encoded_str + padding))
                    return [_[_.find('https'):] for _ in str(decoded_bytes).split('\\') if 'https' in _][0]
                except Exception as e:
                    return url
            else:
                # Return the original URL if the domain is not 'news.google.com'
                return url
        date_format = '%a, %d %b %Y %H:%M:%S GMT'
        cutoff_date = datetime.now() - timedelta(days=self.n_days)
        feed = feed['entries']
        def process_title(title : str):
            if '-' in title:
                return '-'.join(title.split('-')[:-1])
            return title
        return [
            URL(
                process_url(_['link']),
                title=process_title(_['title']),
                date=datetime.strptime(_['published'], date_format).isoformat()
            )
            for _ in feed
            if datetime.strptime(_['published'], date_format) >= cutoff_date
        ]