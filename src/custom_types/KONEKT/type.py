from typing import List, Union, Dict, Literal, Tuple, Optional
from pydantic import BaseModel, Field, create_model, ValidationError
from openai import OpenAI
import json 
import re
import unicodedata

class Reference(BaseModel):
    url: str = Field(..., description="URL of the reference")
    label: str = Field(..., description="Title of the reference")
    description: str = Field(..., description="Short description of the reference")
    image : Optional[str] = Field(None, description="URL of an image to display with the reference")

class Metric(BaseModel):
    metric_definition: str = Field(..., description="Define precisely what is expected in this metric")
    metric_units: str = Field(..., description="Units of the metric")
class MetricI(BaseModel):
    metric_value: str = Field(..., description="Metric value")
    metric_reference_upper_value: str = Field(..., description="Upper reference value for the metric, used for rendering")
    metric_unit: str = Field(..., description="Unit of the metric")
    description: str = Field(..., description="Short description and analysis of the metric and its sources")
    kind : Literal['negative', 'neutral', 'positive'] = Field(..., description="Kind of metric")
    title: str = Field(..., description="Label of the metric")
    info_type: Literal['metric'] = Field(..., description="Just put 'metric'")
    references: List[Reference]
    
     
class Image(BaseModel):
    image_definition: str = Field(..., description="Definition of what is expected in the image")
class ImageI(BaseModel):
    image_url: str = Field(..., description="URL of the image")
    title: str = Field(..., description="Label of the image")
    info_type: Literal['image'] = Field(..., description="Just put 'image'")
    references: List[Reference]


class ChampTxt(BaseModel):
    txt_definition: str = Field(..., description="Definition of what information is expected here")
    sentences_aimed: int = Field(..., description="Number of sentences aimed at for the text")
class ChampTxtI(BaseModel):
    text_contents: str = Field(..., description="Text contents")
    title : str = Field(..., description="Title of the text")
    info_type: Literal['text'] = Field(..., description="Just put 'text'")
    references: List[Reference]

class BulletPoints(BaseModel):
    bullets_points_definition: str = Field(..., description="Definition of what information is expected in the bullet points.")
    bullet_points_aimed : int = Field(..., description = "Number of bullet points aimed for the field")
    enumerate : bool = Field(..., description = "Whether to enumerate or itemize")
class BulletPointsI(BaseModel):
    bullet_points: List[str] = Field(..., description="List of bullet points")
    enumerate: bool = Field(..., description="Whether to enumerate or itemize")
    title : str = Field(..., description="Title of the bullet points")
    info_type: Literal['bullet_points'] = Field(..., description="Just put 'bullet_points'")
    references: List[Reference]

   
class Table(BaseModel):
    columns: List[str] = Field(..., description="List of columns in the table")
class TableI(BaseModel):
    columns: List[str] = Field(..., description="List of columns in the table")
    table: List[List[str]] = Field(..., description="Table contents")
    title: str = Field(..., description="Title of the table")
    info_type: Literal['table'] = Field(..., description="Just put 'table'")
    references: List[Reference]

    
class XYGraph(BaseModel):
    x_axis: str = Field(..., description="Label and unit for the x-axis")
    y_axis: str = Field(..., description="Label and unit for the y-axis")
    kind : Literal['line', 'h-bar', 'v-bar', 'pie', 'radar'] = Field(..., description="Kind of graph")
class XYGraphI(BaseModel):
    x_axis: str = Field(..., description="Label and unit for the x-axis")
    y_axis: str = Field(..., description="Label and unit for the y-axis")
    x_values : List[Union[str, float]] = Field(..., description="List of x values. If dates, put them in ISO-8601 format")
    y_values : List[float] = Field(..., description="List of y values")
    kind : Literal['line', 'h-bar', 'v-bar', 'pie', 'radar'] = Field(..., description="Kind of graph")
    title: str = Field(..., description="Title of the graph")
    info_type: Literal['xy_graph'] = Field(..., description="Just put 'xy_graph'")
    references: List[Reference]



class XYGraphsStacked(BaseModel):
    entries : List[str]  = Field(..., description="List of rows, of y values to stack. Should be each 3 words or less")
    x_axis: str = Field(..., description="Label and unit for the x-axis")
    y_axis: str = Field(..., description="Label and unit for the y-axis")
    kind : Literal['line', 'h-bar', 'v-bar', 'pie', 'radar'] = Field(..., description="Kind of graph")
class XYGraphsStackedI(BaseModel):
    ys_values : Dict[str, List[float]] = Field(..., description="Dictionary of y values to stack. Key is the label of the stack")
    x_values : List[Union[str, float]] = Field(..., description="List of x values. If dates, put them in ISO-8601 format")
    x_axis: str = Field(..., description="Label and unit for the x-axis")
    y_axis: str = Field(..., description="Label and unit for the y-axis")
    kind : Literal['line', 'h-bar', 'v-bar', 'pie', 'radar'] = Field(..., description="Kind of graph")
    title: str = Field(..., description="Title of the graph")
    info_type: Literal['xy_graph_stacked'] = Field(..., description="Just put 'xy_graph'")
    references: List[Reference]


class GenericType(BaseModel):
    title: str = Field(..., description="Title of the information")
    description: str = Field(..., description="Description of the information, or of its content if nested.")
    contents : str = Field(..., description = "Are we expecting a table? a graph? a text? a bullet points? an image? a metric? Or subsections of these?")
    info_type: Union[Metric, Image, ChampTxt, BulletPoints, Table, XYGraph, XYGraphsStacked, List['GenericType']] = Field(
        ..., description="Type of information, can be a text, number, bullet points, source, or nested generic types"
    )

matches = {
    "Metric": MetricI,
    "Image": ImageI,
    "ChampTxt": ChampTxtI,
    "BulletPoints": BulletPointsI,
    "Table": TableI,
    "XYGraph": XYGraphI,
    "XYGraphsStacked": XYGraphsStackedI
}

def GET_STRUCTURE_FROM_LLM(prompt : str, api_key : str) -> GenericType:
    client = OpenAI(api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Provide a report structure fitting the user's request and needs."},
            {"role": "user", "content": prompt},
        ],
        response_format=GenericType,
    )
    event = completion.choices[0].message.parsed
    return event

def U(s):
    # Step 1: Normalize and remove accents
    s = unicodedata.normalize('NFD', s)
    s = ''.join(char for char in s if unicodedata.category(char) != 'Mn')
    
    # Step 2: Remove leading numbers
    s = re.sub(r'^\d+', '', s)
    
    # Step 3: Remove all special characters except spaces (to handle later)
    s = re.sub(r'[^A-Za-z0-9\s]', '', s)
    
    # Step 4: Replace spaces with underscores
    s = re.sub(r'\s+', '_', s)
    
    # Step 5: Convert to uppercase
    s = s.upper()
    
    return s

def infer_type(v : Union[Metric, Image, ChampTxt, BulletPoints, Table, XYGraph, XYGraphsStacked, List['GenericType']]) -> str:
    for v_ in [Metric, Image, ChampTxt, BulletPoints, Table, XYGraph, XYGraphsStacked]:
        if v.__class__.__name__ == v_.__name__:
            return v_
    if not isinstance(v, List):
        print(v)
    return None

def infer_typeI(v : Union[MetricI, ImageI, ChampTxtI, BulletPointsI, TableI, XYGraphI, XYGraphsStackedI]):
    for v_ in [MetricI, ImageI, ChampTxtI, BulletPointsI, TableI, XYGraphI, XYGraphsStackedI]:
        if v.__class__.__name__ == v_.__name__:
            return v_
    assert isinstance(v, List)
    return None


def generic_type_instance_to_pydantic_basemodel(gt: GenericType):
    _type = infer_type(gt.info_type)
    if _type is None:
        L = {}
        L['title'] = (str, Field(..., description=gt.title))
        L['info_type'] = (Literal['sections'], Field(..., description="Just put 'sections'"))
        for _, gt_ in enumerate(gt.info_type):
            L[f'{U(gt_.title)}_{_}'] = (generic_type_instance_to_pydantic_basemodel(gt_), ...)
        return create_model(U(gt.title), **L)
    else:
        return matches[_type.__name__]

class Result(BaseModel):
    title : str = Field(..., description="Title of the information")
    info_type : str = Field(..., description="Type of information, can be a text, number, bullet points, source, or nested generic types")
    contents : List[Union[MetricI, ImageI, ChampTxtI, BulletPointsI, TableI, XYGraphI, XYGraphsStackedI, 'Result']] = Field(..., description="Contents of the information")
    references: List[Reference]
    
def GET_RESULT_FROM_LLM(api_key : str, event : GenericType) -> Result:
    client = OpenAI(api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Generate a dummy report with dummy information"},
        ],
        response_format=generic_type_instance_to_pydantic_basemodel(event),
    )

    ntype = completion.choices[0].message.parsed
    
    def process_event(ntype) -> Result:
        if ntype.info_type == "sections":
            contents = []
            for k, v in ntype.__dict__.items():
                if k not in ['title', 'info_type']:
                    contents.append(process_event(v))
            return Result(title=ntype.title, info_type="sections", contents=contents)
        return ntype
    
    return process_event(ntype)

    
class ConverterResult:
    @staticmethod
    def to_bytes(obj : Result) -> bytes:
        return bytes(json.dumps(obj.to_dict()), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> Result:
        return Result.parse_obj(json.loads(obj.decode('utf-8')))
    
from custom_types.wrapper import TYPE
wraped_result = TYPE(
    extension='konekt',
    _class = Result,
    converter = ConverterResult,
    additional_converters={
        'json':lambda x : x.model_dump()
        },
    icon='/micons/deepsource.svg',
)


class ConverterGeneric:
    @staticmethod
    def to_bytes(obj : GenericType) -> bytes:
        return bytes(json.dumps(obj.to_dict()), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> GenericType:
        return GenericType.parse_obj(json.loads(obj.decode('utf-8')))
    
wraped_generic = TYPE(
    extension='konektstrukt',
    _class = GenericType,
    converter = ConverterGeneric,
    additional_converters={
        'json':lambda x : x.model_dump()
        },
    icon='/micons/deepsource.svg',
)