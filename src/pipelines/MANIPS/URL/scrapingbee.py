from custom_types.URL2.type import URL2
import requests
from typing import Literal
import os 
from trafilatura import  extract
from bs4 import BeautifulSoup
from dateutil import parser
import datetime as dt

class Pipeline:
    __env__ = ["SCRAPING_BEE"]
    def __init__(self, 
                 premium : bool = False,
                 block_ads : bool = False,
                 render_js : bool = False,
                 block_resources : bool = False,
                 country : Literal["us", "ru", "fr"] = "us",
                 wait : Literal["networkidle0", "networkidle2", "load", "domcontentloaded"] = "networkidle0",
                 ):
        self.premium = premium
        self.block_ads = block_ads
        self.render_js = render_js
        self.block_resources = block_resources
        self.country = country
        self.wait = wait
        if not premium:
            self.country = "us"

    def __call__(self, url : URL2) -> URL2:
        def html_finder(_url):
            SCRAPING_BEE = os.environ.get("SCRAPING_BEE")
            if not SCRAPING_BEE:
                return None
            params={
                        'api_key': SCRAPING_BEE,
                        'url': _url, 
                        'custom_google': "true" if "google.com" in _url else "false",
                        'wait_browser': self.wait, 
                    }
            if self.premium:
                params['premium_proxy'] = "true"
            if self.block_ads:
                params['block_ads'] = "true"
            if self.render_js:
                params['render_js'] = "true"
            if self.country:
                params['country_code'] = self.country
            try:
                response = requests.get(url='https://app.scrapingbee.com/api/v1/', params=params)
                response.raise_for_status()
                text = extract(response.text)
                if len(text.strip()) < 100:
                    raise ValueError("Text is too short")
                return text
            except:
                pass 
            return None
        url.apply_html_finder(html_finder)
        return url