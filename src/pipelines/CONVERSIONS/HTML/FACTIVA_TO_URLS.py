from custom_types.URL.type import URL
from custom_types.HTML.type import HTML
from bs4 import BeautifulSoup
from typing import List

class Pipeline:

    def __init__(self):
        pass
    def __call__(self, html : HTML) -> List[URL]:
        html = html.html
        soup = BeautifulSoup(html, 'html.parser')
        urls = []
        for article in soup.find_all('td', class_='article'):
            a_tag = article.find_all('a')
            TITLE = ""
            for x in a_tag:
                if not x.text.strip():
                    continue
                TITLE = x.text.strip()
                break
            if not TITLE:
                continue
            tags_of_interest = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'blockquote', 'table', 'tr', 'td', 'th', 'ul', 'ol']
            text_content = []
            for tag in article.find_all(tags_of_interest):
                if tag.name.startswith('h'):
                    text_content.append(f'\n{tag.get_text()}\n')
                else:
                    text_content.append(tag.get_text())
            IMAGES = [x.get('src') for x in article.find_all('img')]
            CONTENT = ' '.join(text_content).strip()
            urls.append(URL(url = "localhost", tilte = TITLE, images = IMAGES, success = True, text = CONTENT))
        return urls