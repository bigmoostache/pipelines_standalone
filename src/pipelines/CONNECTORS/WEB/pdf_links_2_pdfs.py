import os, openai, requests
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urlparse
from custom_types.PDF.type import PDF

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self):
        pass
    def __call__(self, pdf_links : List[str]) -> List[PDF]:
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
        res = []
        for url in pdf_links:
            # Send a GET request to the URL
            response = requests.get(url, headers = headers)
            # Check if the request was successful
            if response.status_code == 200 and response.content.startswith(b'%PDF'):
                res.append(PDF(response.content))
            else:
                continue
        return res