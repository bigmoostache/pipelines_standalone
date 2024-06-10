from custom_types.URL.type import URL, HTML
from bs4 import BeautifulSoup
from typing import List

def parse_html(html: str) -> List[URL]:
    soup = BeautifulSoup(html, 'html.parser')
    urls = []

    for article in soup.find_all('td', class_='article'):
        a_tag = article.find('a')
        if not a_tag:
            continue
        
        url = a_tag['href']
        title = a_tag.text.strip()
        text = article.find_next_sibling('div', class_='styleenfulltext').get_text(strip=True)
        clean_text = ' '.join(text.split())
        date_meta = article.find_next_sibling('div', class_='styleenfulltextmeta')
        date = date_meta.find('p', class_='articleMeta').text.split(',')[1].strip() if date_meta else ""

        images = []
        for img in article.find_all('img'):
            images.append(img['src'])

        urls.append(URL(url=url, title=title, images=images, success=True, text=text, clean_text=clean_text, date=date))

    return urls

class Pipeline:

    def __init__(self):
        pass
    def __call__(self, html : HTML) -> List[URL]:
        return parse_html(html)