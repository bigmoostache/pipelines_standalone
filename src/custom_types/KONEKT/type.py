from typing import List, Union, Dict, Literal, Tuple, Optional
from pydantic import BaseModel, Field, create_model, ValidationError
from openai import OpenAI
import json 
import re
import unicodedata

class StrictBaseModel(BaseModel):
    class Config:
        extra = 'forbid'
        
class Reference(StrictBaseModel):
    url: str = Field(..., description="URL of the reference")
    label: str = Field(..., description="Title of the reference")
    description: str = Field(..., description="Short description of the reference")
    image : Union[str, None] = Field(..., description="URL of an image to display with the reference")
    def to_markdown(self, depth=0):
        if not self.image:
            return f"[{self.label}]({self.url}) - {self.description}"
        return f"![image]({self.image}) [{self.label}]({self.url}) - {self.description}"
    @staticmethod
    def to_markdown_list(references : List['Reference']):
        return "\t- " + "\n\t- ".join([r.to_markdown() for r in references])

class Metric(BaseModel):
    metric_definition: str = Field(..., description="Define precisely what is expected in this metric")
    metric_units: str = Field(..., description="Units of the metric")
    def to_markdown(self, depth=0):
        return f"**[Metric]\n{self.metric_definition}**\n*Unit* : {self.metric_units}\n\n"
class MetricI(StrictBaseModel):
    metric_value: str = Field(..., description="Metric value")
    metric_reference_upper_value: str = Field(..., description="Upper reference value for the metric, used for rendering")
    metric_unit: str = Field(..., description="Unit of the metric")
    description: str = Field(..., description="Short description and analysis of the metric and its sources")
    kind : Literal['negative', 'neutral', 'positive'] = Field(..., description="Kind of metric")
    title: str = Field(..., description="Label of the metric")
    info_type: Literal['metric'] = Field(..., description="Just put 'metric'")
    references: List[Reference] = Field(..., description="List of references used in the information. Pick in the provided sources, and ALWAYS provide at least one reference, but more is better. Be Careful, one reference may only be used once, as first reference, once as second reference, etc. If you break this rule, you will be flagged for huge bias and your article will be rejected.")
    
    def to_markdown(self, depth=0):
        emoji = {'negative': '📉', 'positive': '📈', 'neural': '🗞️'}[self.kind]
        return f'{self.title} : {emoji} {self.metric_value} {self.metric_unit} {emoji}\n{self.description}\n\n' + Reference.to_markdown_list(self.references)
     
class Image(BaseModel):
    image_definition: str = Field(..., description="Definition of what is expected in the image")
    def to_markdown(self, depth=0):
        return f"[Image]\n**{self.image_definition}**\n\n"
class ImageI(StrictBaseModel):
    image_url: Union[str, None] = Field(..., description="URL of the image")
    title: str = Field(..., description="Label of the image")
    info_type: Literal['image'] = Field(..., description="Just put 'image'")
    references: List[Reference] = Field(..., description="List of references used in the information. Pick in the provided sources, and ALWAYS provide at least one reference, but more is better. Be Careful, one reference may only be used once, as first reference, once as second reference, etc. If you break this rule, you will be flagged for huge bias and your article will be rejected.")
    def to_markdown(self, depth=0):
        return f"![{self.title}]({self.image_url})" + Reference.to_markdown_list(self.references)


class ChampTxt(BaseModel):
    txt_definition: str = Field(..., description="Definition of what information is expected here")
    sentences_aimed: int = Field(..., description="Number of sentences aimed at for the text")
    def to_markdown(self, depth=0):
        return f"[Text]\n**{self.txt_definition}**\nApproximate number of sentences : {self.sentences_aimed}\n\n"
class ChampTxtI(StrictBaseModel):
    text_contents: str = Field(..., description="Text contents; do NOT apply markdown formatting")
    title : str = Field(..., description="Title of the text")
    info_type: Literal['text'] = Field(..., description="Just put 'text'")
    references: List[Reference] = Field(..., description="List of references used in the information. Pick in the provided sources, and ALWAYS provide at least one reference, but more is better. Be Careful, one reference may only be used once, as first reference, once as second reference, etc. If you break this rule, you will be flagged for huge bias and your article will be rejected.")
    
    def to_markdown(self, depth=0):
        prefix = {0:'#', 1:'##', 2:'###', 3:'####'}.get(depth, '####')
        return f'{prefix} {self.title}\n\n{self.text_contents}\n" + Reference.to_markdown_list(self.references)'

class BulletPoints(BaseModel):
    bullets_points_definition: str = Field(..., description="Definition of what information is expected in the bullet points.")
    bullet_points_aimed : int = Field(..., description = "Number of bullet points aimed for the field")
    enumerate : bool = Field(..., description = "Whether to enumerate or itemize")
    def to_markdown(self, depth=0):
        return f"[Bullet Points]\n**{self.bullets_points_definition}**\nApproximate number of bullet points : {self.bullet_points_aimed}\n\n"
class BulletPointsI(StrictBaseModel):
    bullet_points: List[str] = Field(..., description="List of bullet points. Do NOT apply markdown formatting")
    enumerate: bool = Field(..., description="Whether to enumerate or itemize")
    title : str = Field(..., description="Title of the bullet points")
    info_type: Literal['bullet_points'] = Field(..., description="Just put 'bullet_points'")
    references: List[Reference] = Field(..., description="List of references used in the information. Pick in the provided sources, and ALWAYS provide at least one reference, but more is better. Be Careful, one reference may only be used once, as first reference, once as second reference, etc. If you break this rule, you will be flagged for huge bias and your article will be rejected.")
    
    def to_markdown(self, depth=0):
        prefix = {0:'#', 1:'##', 2:'###', 3:'####'}.get(depth, '####')
        return f"{prefix} {self.title}\n\n" + ("\n".join([f"- {bp}" for bp in self.bullet_points])) + Reference.to_markdown_list(self.references)

   
class Table(BaseModel):
    columns: List[str] = Field(..., description="List of columns in the table")
    def to_markdown(self, depth=0):
        return f"[Table]\n**Columns** : {', '.join(self.columns)}\n\n"
class TableI(StrictBaseModel):
    columns: List[str] = Field(..., description="List of columns in the table")
    table: List[List[str]] = Field(..., description="Table contents")
    title: str = Field(..., description="Title of the table")
    info_type: Literal['table'] = Field(..., description="Just put 'table'")
    references: List[Reference] = Field(..., description="List of references used in the information. Pick in the provided sources, and ALWAYS provide at least one reference, but more is better. Be Careful, one reference may only be used once, as first reference, once as second reference, etc. If you break this rule, you will be flagged for huge bias and your article will be rejected.")
    
    def to_markdown(self, depth=0):
        prefix = {0:'#', 1:'##', 2:'###', 3:'####'}.get(depth, '####')
        r = f"{prefix} {self.title}\n\n"
        r += "|".join(self.columns) + "\n"
        r += "|".join(["---" for _ in self.columns]) + "\n"
        for row in self.table:
            r += "|".join(row) + "\n"
        return r + Reference.to_markdown_list(self.references)
    
class XYGraph(BaseModel):
    x_axis: str = Field(..., description="Label and unit for the x-axis")
    y_axis: str = Field(..., description="Label and unit for the y-axis")
    kind : Literal['line', 'h-bar', 'v-bar', 'pie', 'radar'] = Field(..., description="Kind of graph")
    def to_markdown(self, depth=0):
        return f"[XY Graph]\n**{self.x_axis}** | **{self.y_axis}**\nKind : {self.kind}\n\n"
class XYGraphI(StrictBaseModel):
    x_axis: str = Field(..., description="Label and unit for the x-axis")
    y_axis: str = Field(..., description="Label and unit for the y-axis")
    x_values : List[Union[str, float]] = Field(..., description="List of x values. If dates, put them in ISO-8601 format")
    y_values : List[float] = Field(..., description="List of y values")
    kind : Literal['line', 'h-bar', 'v-bar', 'pie', 'radar'] = Field(..., description="Kind of graph")
    title: str = Field(..., description="Title of the graph")
    info_type: Literal['xy_graph'] = Field(..., description="Just put 'xy_graph'")
    references: List[Reference] = Field(..., description="List of references used in the information. Pick in the provided sources, and ALWAYS provide at least one reference, but more is better. Be Careful, one reference may only be used once, as first reference, once as second reference, etc. If you break this rule, you will be flagged for huge bias and your article will be rejected.")
    
    def to_markdown(self, depth=0):
        prefix = {0:'#', 1:'##', 2:'###', 3:'####'}.get(depth, '####')
        r = f"{prefix} {self.title}\n\n"
        r += f"**{self.x_axis}** | **{self.y_axis}**\n"
        r += "|".join(["---" for _ in range(2)]) + "\n"
        for x, y in zip(self.x_values, self.y_values):
            r += f"{x} | {y}\n"
        return r + Reference.to_markdown_list(self.references)



class XYGraphsStacked(BaseModel):
    entries : List[str]  = Field(..., description="List of rows, of y values to stack. Should be each 3 words or less")
    x_axis: str = Field(..., description="Label and unit for the x-axis")
    y_axis: str = Field(..., description="Label and unit for the y-axis")
    kind : Literal['line', 'h-bar', 'v-bar', 'pie', 'radar'] = Field(..., description="Kind of graph")
    def to_markdown(self, depth=0):
        return f"[XY Graph Stacked]\n**{self.x_axis}** | **{self.y_axis}**\nKind : {self.kind}\n\n"
class XYGraphsStackedI(StrictBaseModel):
    ys_values : Dict[str, List[float]] = Field(..., description="Dictionary of y values to stack. Key is the label of the stack")
    x_values : List[Union[str, float]] = Field(..., description="List of x values. If dates, put them in ISO-8601 format")
    x_axis: str = Field(..., description="Label and unit for the x-axis")
    y_axis: str = Field(..., description="Label and unit for the y-axis")
    kind : Literal['line', 'h-bar', 'v-bar', 'pie', 'radar'] = Field(..., description="Kind of graph")
    title: str = Field(..., description="Title of the graph")
    info_type: Literal['xy_graph_stacked'] = Field(..., description="Just put 'xy_graph'")
    references: List[Reference] = Field(..., description="List of references used in the information. Pick in the provided sources, and ALWAYS provide at least one reference, but more is better. Be Careful, one reference may only be used once, as first reference, once as second reference, etc. If you break this rule, you will be flagged for huge bias and your article will be rejected.")
    
    def to_markdown(self, depth=0):
        prefix = {0:'#', 1:'##', 2:'###', 3:'####'}.get(depth, '####')
        r = f"{prefix} {self.title}\n\n"
        r += f"**{self.x_axis}** | **{self.y_axis}**\n"
        r += "|".join(["---" for _ in range(2)]) + "\n"
        for x in self.x_values:
            r += f"{x} | " + " | ".join([str(y) for y in [self.ys_values[entry] for entry in self.entries]]) + "\n"
        return r + Reference.to_markdown_list(self.references)


class GenericType(BaseModel):
    title: str = Field(..., description="Title of the information")
    description: str = Field(..., description="Description of the information, or of its content if nested.")
    contents : str = Field(..., description = "Are we expecting a table? a graph? a text? a bullet points? an image? a metric? Or subsections of these?")
    info_type: Union[Metric, Image, ChampTxt, BulletPoints, Table, XYGraph, XYGraphsStacked, List['GenericType']] = Field(..., description="Type of information, can be a text, number, bullet points, source, or nested generic types"
    )
    def to_markdown(self, depth=0):
        prefix = {0:'#', 1:'##', 2:'###', 3:'####'}.get(depth, '####')
        r = f"{prefix} {self.title}\n\n{self.description}\n\n"
        if isinstance(self.info_type, List):
            for content in self.info_type:
                r += content.to_markdown(depth+1)
        else:
            r += self.info_type.to_markdown(depth+1)
        return r

matches = {
    "Metric": MetricI,
    "Image": ImageI,
    "ChampTxt": ChampTxtI,
    "BulletPoints": BulletPointsI,
    "Table": TableI,
    "XYGraph": XYGraphI,
    "XYGraphsStacked": XYGraphsStackedI
}
from custom_types.PROMPT.type import PROMPT

def GET_STRUCTURE_FROM_LLM(prompt : PROMPT, api_key : str, model : str) -> GenericType:
    completion = OpenAI(api_key=api_key).beta.chat.completions.parse(
        model=model,
        messages=prompt.messages,
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
        L['title'] = (str, Field(..., description=f"The proposed title was {gt.title}. Pick a better suiting name for this section, fine-tuned to the content. Also, make sure it is in english"))
        L['info_type'] = (Literal['sections'], Field(..., description="Just put 'sections'"))
        L['references'] = (List[Reference], Field(..., description="List of references used in the information. Pick in the provided sources, and ALWAYS provide at least one reference, but more is better. Be Careful, one reference may only be used once, as first reference, once as second reference, etc. If you break this rule, you will be flagged for huge bias and your article will be rejected."))
        L['header_image_url'] = (Union[str, None], Field(..., description="URL of the header image"))
        for _, gt_ in enumerate(gt.info_type):
            one = U(gt_.title)[:50]
            var_name = f'{one}_{_}'
            print(f'Adding {var_name} to the model')
            L[var_name] = (generic_type_instance_to_pydantic_basemodel(gt_), Field(..., description=gt_.description))
        Config = type('Config', (), {'extra': 'forbid'})
        return create_model(U(gt.title), __config__=Config, **L)
    else:
        return matches[_type.__name__]

class Result(BaseModel):
    title : str = Field(..., description="Title of the information")
    info_type : str = Field(..., description="Type of information, can be a text, number, bullet points, source, or nested generic types")
    contents : List[Union[MetricI, ImageI, ChampTxtI, BulletPointsI, TableI, XYGraphI, XYGraphsStackedI, 'Result']] = Field(..., description="Contents of the information")
    references: List[Reference] = Field(..., description="List of references used in the information")
    header_image_url: Union[str, None] = Field(..., description="URL of the header image")
    
    def to_markdown(self, depth=0):
        prefix = {0:'#', 1:'##', 2:'###'}.get(depth, '###')
        r = f"{prefix} {self.title}\n\n"
        for content in self.contents:
            r += content.to_markdown(depth+1) + "\n\n"
        return r + '\n\n' + Reference.to_markdown_list(self.references)
    
def GET_RESULT_FROM_LLM(api_key : str, event : GenericType, model : str, prompts : PROMPT) -> Result:
    client = OpenAI(api_key=api_key)
    response_format = generic_type_instance_to_pydantic_basemodel(event)
    import json
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=prompts.messages,
        response_format=response_format
    )
    ntype = completion.choices[0].message.parsed
    def process_event(ntype) -> Result:
        if ntype.info_type == "sections":
            contents = []
            for k, v in ntype.__dict__.items():
                if k not in ['title', 'info_type', 'references', 'header_image_url']:
                    contents.append(process_event(v))
            return Result(title=ntype.title, info_type="sections", contents=contents, references=ntype.references, header_image_url=ntype.header_image_url)
        return ntype
    return process_event(ntype)

class ConverterResult:
    @staticmethod
    def to_bytes(obj : Result) -> bytes:
        return obj.model_dump_json(indent=2).encode('utf-8')
         
    @staticmethod
    def from_bytes(b : bytes) -> Result:
        return Result.parse_obj(json.loads(b.decode('utf-8')))
    
from custom_types.wrapper import TYPE
wraped_result = TYPE(
    extension='konekt',
    _class = Result,
    converter = ConverterResult,
    additional_converters={
        'json':lambda x : x.model_dump()
        },
    icon='/micons/deepsource.svg',
    visualiser='https://konekt.croquo.com'
)

class ConverterGeneric:
    @staticmethod
    def to_bytes(obj : GenericType) -> bytes:
        return obj.model_dump_json(indent=2).encode('utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> GenericType:
        return GenericType.parse_obj(json.loads(obj.decode('utf-8')))
    
wraped_generic = TYPE(
    extension='konektstrukt',
    _class = GenericType,
    converter = ConverterGeneric,
    additional_converters={
        'json':lambda x : x.model_dump(),
        'txt': lambda x : x.model_dump_json(indent=2)
        },
    icon='/micons/deepsource.svg',
)