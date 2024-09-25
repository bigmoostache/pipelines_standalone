from custom_types.URL2.type import URL2
import requests
from typing import Literal
import os 
import datetime as dt
import time  # Import time module for sleep functionality

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
                        'wait_browser': self.wait, 
                    }
            if 'google.com' in _url:
                params['custom_google'] = "true"
            if self.premium:
                params['premium_proxy'] = "true"
            if self.block_ads:
                params['block_ads'] = "true"
            if not self.render_js:
                params['render_js'] = "false"
            if self.country:
                params['country_code'] = self.country

            max_retries = 10  # Maximum number of retries
            retries = 0
            while retries < max_retries:
                try:
                    response = requests.get(url='https://app.scrapingbee.com/api/v1/', params=params)
                    response.raise_for_status()
                    return response.text  # Success, return the response text
                except requests.exceptions.HTTPError as e:
                    # Check for the specific 429 error and URL
                    if (e.response.status_code == 429 and
                        'TOO MANY REQUESTS' in str(e) and
                        'search_type=news' in e.response.url):
                        retries += 1
                        time.sleep(5)  # Wait before retrying
                        continue  # Retry the request
                    else:
                        return None  # Other errors, do not retry
            return None  # Return None if max retries exceeded
        url.apply_html_finder(html_finder)
        return url
