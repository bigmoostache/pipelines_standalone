from pydantic import BaseModel, Field
from typing import List, Literal, Union
from openai import OpenAI
from datetime import datetime

class Organic(BaseModel):
    google_query : str = Field(..., description = 'Google organic search to perform.')
    kind : Literal['organic'] = Field(..., description = 'Data Search Action')
class News(BaseModel):
    google_news_query : str = Field(..., description = 'Google news search to perform. Do NOT include date, year or month, it\'s integrated automatically in google API.')
    kind : Literal['news'] = Field(..., description = 'Data Search Action')

class ResearchActions(BaseModel):
    actions : List[Union[Organic, News]] = Field(..., description = 'Queries to perform')
    

from custom_types.URL2.type import URL2
import requests
from custom_types.PDF.type import PDF
from custom_types.PROMPT.type import PROMPT
from pypdf import PdfReader
from datetime import datetime
import io

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, 
                 p: PROMPT
                 ) -> JSONL:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "user", "content": t},
                {"role": "system", "content": f"Provide a list of 12 diverse, wide-covering queries to perform in order to investigate the topic above. They should each be between 2 and 5 words maximum, and not include any date. Provide 6 organic and 6 news queries."},
            ],
            response_format=ResearchActions,
        )

        event = completion.choices[0].message.parsed