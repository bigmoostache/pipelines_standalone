from trafilatura import fetch_url, extract
from trafilatura.settings import use_config
from custom_types.URL.type import URL
import requests
import os

newconfig = use_config()
newconfig.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

class Pipeline:
    __env__ = ["SCRAPING_BEE"]
    def __init__(self, ignore_if_success:bool = True):
        self.ignore_if_success = ignore_if_success

        self.wait = "networkidle0"
        self.premium = False
        self.block_ads = False
        self.render_js = True
        self.country = 'us'

    def __call__(self, url : URL) -> URL:
        if url.text and len(url.text.split()) > 100:
            return url
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
                        'TOO MANY REQUESTS' in str(e)):
                        retries += 1
                        time.sleep(5)  # Wait before retrying
                        continue  # Retry the request
                    else:
                        return None  # Other errors, do not retry
            return None  # Return None if max retries exceeded
        
        html = html_finder(url.url)
        if html:
            try:
                result = extract(html, include_tables = True, config=newconfig)
                if result:
                    url.success = True
                    url.text = result
                else:
                    return url
            except TypeError as e:
                return url
        else:
            return url