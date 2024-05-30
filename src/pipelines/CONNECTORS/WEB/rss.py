import feedparser
from typing import List
import tldextract
from datetime import datetime, timedelta

class Pipeline:

    def __init__(self,
                 num_hours: int = 48):
        self.num_hours = num_hours  

    def __call__(self, rss_url: str) -> List[dict]:
        feed = feedparser.parse(rss_url)
        items_list = []
        current_time = datetime.now()
        for entry in feed.entries:
            try:
                published_date = datetime(*entry.published_parsed[:6])
                is_recent = (current_time - published_date) < timedelta(hours=self.num_hours)
            except:
                is_recent = False
            if not is_recent:
                continue
            try:
                link = entry.link
            except:
                link = ""
            item = {
                'link': link,
                'published': entry.published,
                'is_recent': is_recent
            }
            try:
                item["summary"] = entry.summary.strip()
            except:
                item["summary"] = ""
            try:
                item["title"] = entry.title.strip()
            except:
                item["title"] = ""
            item["full"] = f"{item['title']} - {item['summary']}".replace("\n", " ").replace("null", "")
            item["full"] = ' '.join(item["full"].split()[:200])
            # Append the item dictionary to the list
            def get_domain(url):
                extracted = tldextract.extract(url)
                domain = f"{extracted.domain}"
                # Upper case first letter
                if domain:
                    domain = domain[0].upper() + domain[1:]
                return domain
            item["source"] = get_domain(item["link"])
            s = item["source"]
            f = item["full"]
            item["with_source"] = f"{s} {f}"
            items_list.append(item)

        return items_list