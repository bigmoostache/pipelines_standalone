from custom_types.URL.type import URL
import requests
from typing import Literal
import os 
from trafilatura import  extract

class Pipeline:
    __env__ = ["SCRAPING_BEE"]
    def __init__(self, 
                 ignore_if_success :bool= True,
                 skip_if_scraping_be_not_provided : bool = True,
                 premium : bool = False,
                 country : Literal["us", "ru", "fr"] = "us",
                 wait : Literal["networkidle0", "networkidle2", "load", "domcontentloaded"] = "networkidle0",
                 ):
        self.ignore_if_success = ignore_if_success
        self.premium = "true" if premium else "false"
        self.wait = wait
        self.country = country
        self.skip_if_scraping_be_not_provided = skip_if_scraping_be_not_provided
        if not premium:
            self.country = "us"

    def __call__(self, url : URL) -> URL:
        if self.ignore_if_success and url.success:
            return url
        SCRAPING_BEE = os.environ.get("SCRAPING_BEE")
        if not SCRAPING_BEE:
            if self.skip_if_scraping_be_not_provided:
                return url
            raise ValueError("Scraping Bee API key not provided")
        try:
            response = requests.get(
                url='https://app.scrapingbee.com/api/v1/',
                params={
                    'api_key': SCRAPING_BEE,
                    'url': url.url, 
                    'custom_google': "true" if "google.com" in url.url else "false",
                    'wait_browser': self.wait,
                    'premium_proxy': self.premium, 
                    'country_code':self.country
                },
                
            )
            if response.status_code != 200:
                return url
            text = extract(response.text)
            url.text = text
            url.success = True
        except:
            pass 
        return url