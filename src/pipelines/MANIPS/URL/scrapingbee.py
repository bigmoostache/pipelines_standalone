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
                 ignore_if_success :bool= True,
                 skip_if_scraping_be_not_provided : bool = True,
                 premium : bool = False,
                 block_ads : bool = False,
                 render_js : bool = False,
                 block_resources : bool = False,
                 country : Literal["us", "ru", "fr"] = "us",
                 wait : Literal["networkidle0", "networkidle2", "load", "domcontentloaded"] = "networkidle0",
                 ):
        self.ignore_if_success = ignore_if_success
        self.skip_if_scraping_be_not_provided = skip_if_scraping_be_not_provided
        self.premium = premium
        self.block_ads = block_ads
        self.render_js = render_js
        self.block_resources = block_resources
        self.country = country
        self.wait = wait
        if not premium:
            self.country = "us"

    def __call__(self, url : URL2) -> URL2:
        if self.ignore_if_success and url.success:
            return url
        SCRAPING_BEE = os.environ.get("SCRAPING_BEE")
        if not SCRAPING_BEE:
            if self.skip_if_scraping_be_not_provided:
                return url
            raise ValueError("Scraping Bee API key not provided")
        params={
                    'api_key': SCRAPING_BEE,
                    'url': url.url, 
                    'custom_google': "true" if "google.com" in url.url else "false",
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
            url.text = text
            url.success = True
            if not url.date:
                date = extract_publication_date(response.text)
                if date:
                    url.date = date.isoformat()
        except:
            pass 
        return url