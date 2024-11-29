from enum import Enum
from pydantic import BaseModel, Field, create_model
from typing import List, Union, Literal

class Integer(BaseModel):
    integer: Literal['integer']
    integer_minimum: Union[None, int] = None
    integer_maximum: Union[None, int] = None
    integer_unit: Union[None, str] = None
class Number(BaseModel):
    _float : Literal['_float']
    number_minimum: Union[None, float] = None
    number_maximum: Union[None, float] = None
    number_unit: Union[None, str] = None
class String(BaseModel):
    string : Literal['string']
    string_maxLength: Union[None, int] = None
class Enumeration(BaseModel):
    enum : Literal['enum']
    enumeration_choices: List[str]
class Date(BaseModel):
    date : Literal['date']
    date_format: Literal['AAAA-MM-JJTHH:MM:SS,ss-/+FF:ff', 'AAAA-MM-JJ', 'AAAA-MM-JJ']
class Boolean(BaseModel):
    boolean : Literal['boolean']
class DataStructure(BaseModel):
    object_list : Literal['object_list']
    fields : List['Fields']
    
class Fields(BaseModel):
    object_name: str = Field(...)
    object_description: str = Field(...)
    object_required: bool = Field(...)
    object_type: Union[Boolean, Integer, Number, String, Enumeration, Date, DataStructure] = Field(...)
    
    
def rep(s): return __import__('re').sub(r'[^a-z0-9_]', '', __import__('unicodedata').normalize('NFKD', s.lower().replace(' ', '_')).encode('ascii', 'ignore').decode('ascii'))

def _create_model(name: str, x: DataStructure):
    def v2t(f: Fields):
        def required(_):
            if f.object_required:
                return _
            return Union[_, None]
        if isinstance(f.object_type, Integer):
            return required(int), Field(..., description = f.object_description)
        elif isinstance(f.object_type, Boolean):
            return required(bool), Field(..., description = f.object_description)
        elif isinstance(f.object_type, Number):
            return required(float), Field(..., description = f.object_description)
        elif isinstance(f.object_type, String):
            return required(str), Field(..., description = f.object_description)
        elif isinstance(f.object_type, Enumeration):
            return required(str), Field(..., description=f"{f.object_description}. Allowed values: {f.object_type.enumeration_choices}")
        elif isinstance(f.object_type, Date):
            return required(str), Field(..., description=f"{f.object_description}. Date format: {f.object_type.date_format}")
        else:
            # required makes no sense for DataStructure: it can always be an empty fields list
            return List[_create_model(rep(f.object_name), f.object_type)], Field(..., description = f.object_description)
    dictionary = {}
    for f in x.fields:
        dictionary[rep(f.object_name)] = v2t(f)
    return create_model(name, **dictionary)

import json
class Converter:
    @staticmethod
    def to_bytes(obj : DataStructure) -> bytes:
        return bytes(obj.model_dump_json(), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> 'DataStructure':
        return DataStructure.parse_obj(json.loads(obj.decode('utf-8')))
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='xtrk',
    _class = DataStructure,
    converter = Converter,
    additional_converters={
        'json':lambda x : x.model_dump()
        },
    visualiser = "https://visualizations.croquo.com/xtrk",
    icon = '/micons/pnpm_light.svg'
)