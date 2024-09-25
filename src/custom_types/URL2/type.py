import json
from typing import List
from pydantic import BaseModel, Field
from trafilatura import extract
from trafilatura.settings import use_config
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil import parser

newconfig = use_config()
newconfig.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

class URL2(BaseModel):
    class Image(BaseModel):
        url: str = Field(..., description="The URL of the image.")
        alt: str = Field(..., description="The alt text of the image.")
    url: str = Field(..., description="The full URL of the web page.")
    title: str = Field(..., description="The title of the web page.")
    description: str = Field("", description="The description of the web page.")
    images: List[Image] = Field([], description="A list of image URLs from the web page.")
    text: str = Field(..., description="The raw text content of the web page.")
    html: str = Field(..., description="The raw HTML content of the web page.")
    date: str = Field(..., description="ISO 8601 formatted date of the web page.")

    @classmethod
    def init(cls, url: str, title: str = '', date: str = None) -> 'URL2':
        obj = cls(url=url, title=title, images=[], text="", html="", date="")
        if date:
            try:
                obj.date = datetime.fromisoformat(date).isoformat()
            except:
                pass
        return obj
    
    def parse_trafilatura(self):
        text = extract(self.html, include_tables = True, config=newconfig)
        if text and len(text) > 100:
            self.text = text
            self.html = ""
    
    def find_title(self):
        if self.title:
            return
        soup = BeautifulSoup(self.html, 'html.parser')
        title_tag = soup.find('title')
        if title_tag and title_tag.text and len(title_tag.text.strip()) > 0:
            self.title = title_tag.text.strip()
    
    def find_date(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        # Common places where publication date is usually found
        date_strings = []
        
        # Look for meta tags with publication date info
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            for attr in ['pubdate', 'date', 'publishdate', 'timestamp', 'dc.date.issued', 'article:published_time']:
                if tag.get('name', '').lower() == attr or tag.get('property', '').lower() == attr:
                    date_strings.append(tag.get('content'))
        
        # Look for time elements
        time_tags = soup.find_all('time')
        for tag in time_tags:
            if tag.get('datetime'):
                date_strings.append(tag.get('datetime'))
        
        # Look for specific date attributes
        date_attributes = ['pubdate', 'date', 'data-publish-date']
        for attr in date_attributes:
            for tag in soup.find_all(attrs={attr: True}):
                date_strings.append(tag[attr])
        
        # Try parsing the collected date strings
        for date_string in date_strings:
            try:
                publication_date = parser.parse(date_string)
                self.date = publication_date.isoformat()
                return
            except (ValueError, TypeError):
                continue

    def process_html(self):
        self.parse_trafilatura()
        if len(self.text) < 100:
            self.html = ""
            self.text = ""
            return
        self.find_date()
        self.find_title()
    
    def apply_html_finder(self, html_finder):
        if (self.html and len(self.html) > 100) or (self.text and len(self.text) > 100) or self.title == 'Uploaded PDF':
            return
        html = html_finder(self.url)
        if html:
            self.html = html
            self.process_html()

class Converter:
    extension = 'url2'
    @staticmethod
    def to_bytes(url : URL2) -> bytes:
        return url.model_dump_json(indent=2).encode('utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> URL2:
        return URL2.parse_obj(json.loads(b.decode('utf-8')))
    @staticmethod
    def str_preview(url: str) -> str:
        return url.model_dump_json(indent=2)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='url2',
    _class = URL2,
    converter = Converter,
    inputable  = False,
    additional_converters={
        'json':lambda x : x.__dict__,
        'txt': lambda obj: obj.model_dump_json(indent=2)
        },
    icon='/micons/url.svg'
)