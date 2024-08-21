from custom_types.PROMPT.type import PROMPT
from custom_types.GRID.type import GRID, NOTATION_CRITERIA, GRID_SECTION
from typing import Literal
from pydantic import Field, BaseModel, create_model
import openai
from utils.booleans import to_bool
from pipelines.CONVERSIONS.txt_2_dict import Pipeline as TXT2DICT
import logging 
import os
logging.basicConfig(level=logging.INFO)

def clean_string(input_string):
    # Convert the string to lowercase
    cleaned_string = input_string.lower()
    
    # Remove special characters except for numbers and spaces using regex
    cleaned_string = re.sub(r'[^a-z0-9\s]', '', cleaned_string)
    
    # Replace spaces with underscores
    cleaned_string = cleaned_string.replace(' ', '_')
    
    # Check if the first character is a number and prepend an underscore if it is
    if cleaned_string[0].isdigit():
        cleaned_string = '_' + cleaned_string
    
    return cleaned_string.upper()

def question_to_BM(NC : NOTATION_CRITERIA, section : str) -> type(BaseModel):
    r = '\n'.join(f'- {x.value} : {x.definition}' for x in sorted(NC.possible_values, key = lambda _ : _.value)) + '\nJustify briefly the grade you want to give. Be fair and unbiased.'
    t = tuple(_.value for _ in NC.possible_values)
    x = {
        "section": (Literal[section], Field(..., description = "section")),
        "name": (Literal[NC.name], Field(..., description = "question name")),
        "value_justification": (str, Field(..., description = r)),
        "value": (Literal[t], Field(..., description = f'Grade for: {NC.name}'))
    }
    return create_model(clean_string(NC.name), **x)
    
def section_to_BM(NC : GRID_SECTION) -> type(BaseModel):
    prefix = clean_string(NC.name) + '_'
    x = {
    prefix + clean_string(_.name) : (question_to_BM(_, NC.name), Field(..., description = _.definition))
    for _ in NC.rows
    }
    return x

def grid_to_BM(NC : GRID) -> type(BaseModel):
    x = {
        k:v for _ in NC.rows for k,v in section_to_BM(_).items()
    }
    return create_model('GRID_NOTATION', **x)


class Pipeline:
    __env__ = ["openai_api_key"]

    def __init__(self, 
                 model : str = "gpt-4o-2024-08-06", 
                 base_url : str = "https://api.openai.com/v1",
                 temperature : int =1, 
                 retries : int =3, 
                 top_p : int =1):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.retries = retries
        self.base_url = base_url
        
    def __call__(self, 
                 p : PROMPT,
                 grid : GRID
                 ) -> dict:
        api_key = os.environ.get("openai_api_key")
        MyBaseModel = grid_to_BM(grid)
        client = openai.OpenAI(api_key=api_key, base_url=self.base_url)
        completion = client.beta.chat.completions.parse(
            model=self.model,
            messages=p.messages,
            temperature=self.temperature,
            top_p=self.top_p,
            response_format=MyBaseModel,
        )

        event = completion.choices[0].message.parsed
        if not isinstance(event, MyBaseModel):
            raise Exception("Invalid response")
        return event.dict()
    