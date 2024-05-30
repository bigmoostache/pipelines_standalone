from custom_types.URL.type import URL
import os, openai, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class Pipeline:
    def __init__(self, ignore_if_success :bool = True):
        self.ignore_if_success = ignore_if_success

    def __call__(self, url : URL) -> URL:
        if self.ignore_if_success and url.success:
            return url
        try:
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
            _url = urlparse(url.url)
            location = _url.netloc
            if 'forbes.com' in location:
                _url = f'{_url.scheme}://{_url.netloc}{_url.path}?api=true'
                response = requests.get(url, headers = headers).json()['article']['body']
                response.raise_for_status()
                html = response.json()['article']['body']
            else:
                pass
            soup = BeautifulSoup(html, 'html.parser')
            tags_of_interest = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'blockquote', 'table', 'tr', 'td', 'th', 'ul', 'ol']
            text_content = []
            for tag in soup.find_all(tags_of_interest):
                if tag.name.startswith('h'):
                    text_content.append(f'\n{tag.get_text()}\n')
                else:
                    text_content.append(tag.get_text())
            content = ' '.join(text_content).strip()
        except:
            content = ''
        if content.strip():
            url.text = content 
            url.success = True 
        return url