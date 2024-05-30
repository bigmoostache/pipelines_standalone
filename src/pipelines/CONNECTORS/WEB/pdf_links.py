import os, openai, requests
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urlparse

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self):
        pass
    def __call__(self, url : str) -> List[str]:
        headers = {
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Windows; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-ch-ua": "\".Not/A)Brand\";v=\"99\", \"Google Chrome\";v=\"103\", \"Chromium\";v=\"103\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-site": "none",
            "sec-fetch-mod": "",
            "sec-fetch-user": "?1",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "bg-BG,bg;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        def get_complete_link(base, url):
            base = urlparse(base)
            url = urlparse(url)
            if url.netloc == '':
                return f'{base.scheme}://{base.netloc}{url.path}'
            return f'{url.scheme}://{url.netloc}{url.path}'
        def get_links(url):
            # Send a GET request to the URL
            response = requests.get(url, headers = headers)
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the content of the page with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                # Find all the 'a' tags, which contain the links
                links = soup.find_all('a')
                # Extract the href attribute from each link
                urls = []
                for type in ['a', 'h1', 'h2', 'h3', 'h4', 'div', 'p']:
                    try:
                        _urls = [link.get('href') for link in soup.find_all(type) if link.get('href')]
                    except:
                        _urls = []
                    urls = urls + _urls
                urls = list(set(urls))
                urls = [_ for _ in urls if 'pdf' in _]
                return [get_complete_link(url, _) for _ in urls]
            else:
                return []
        try:
            return get_links(url)
        except:
            return []