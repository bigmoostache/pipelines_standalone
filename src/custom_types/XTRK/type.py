from enum import Enum
from pydantic import BaseModel, Field, create_model
from typing import List, Union, Literal, Tuple


# This is aside, but its a good idea to have it here
class ParameterEvaluation(BaseModel):
    param_name : str = Field(..., description="The name of the parameter, VERBATIM. Basically just copy-paste the name of the parameter.")
    param_description : str = Field(..., description="The description of the parameter, VERBATIM. Basically just copy-paste the description of the parameter.")
    note: str = Field(..., description="Your thoughts about this parameter")
    value: float = Field(..., description="The value between 0 and 1 for this parameter")
    keep: bool = Field(..., description="Whether to keep this parameter or not")
class ParametersEvaluation(BaseModel):
    evaluations: List[ParameterEvaluation] = Field(..., description="A list of evaluations for the parameters")
# End of aside


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
    
    def get_field(self, field_name: str) -> 'Fields':
        for f in self.fields:
            if f.object_name == field_name:
                return f
        all_fields = [f.object_name for f in self.fields]
        raise ValueError(f"Field {field_name} not found in DataStructure. Available fields: {all_fields}")
    
    def at_least_one_field_is_a_data_structure(self):
        return any(hasattr(f.object_type, 'object_list') for f in self.fields)
    
    def create_evaluation_model(self):
        params =  [_ for f in self.fields for _ in f.get_params_list()]
        params = '\n'.join([f"* {p[0]}: {p[1]}" for p in params])
        return create_model(
            'ParametersEvaluation',
            **{
                'evaluations': (List[ParameterEvaluation], Field(..., description=f"Please provide a list of evaluations for the following parameters:\n{params}")),
            }
        )
        
    def recursive_sheet_order(self) -> List[str]:
        """
        Returns a list of all the sheets in the data structure, including sub-sheets.
        """
        sheets = []
        for f in self.fields:
            if hasattr(f.object_type, 'object_list'):
                sheets.append(f.object_name)
                sheets += f.object_type.recursive_sheet_order()
        return sheets
    
    @classmethod
    def filter_fields(cls, self: 'DataStructure', fields: List[str]) -> 'DataStructure':
        return cls(
            object_list = 'object_list',
            fields = [
                Fields(
                    object_name = f.object_name,
                    object_description = f.object_description,
                    object_required = f.object_required,
                    object_type = cls.filter_fields(f.object_type, fields)
                )
                if f.object_is_a_data_structure()
                else Fields(
                    object_name = f.object_name,
                    object_description = f.object_description,
                    object_required = f.object_required,
                    object_type = f.object_type
                )
                for f in self.fields if ((f.object_name in fields) or f.object_required or f.object_is_a_data_structure())
            ]
        )

class Fields(BaseModel):
    object_name: str = Field(...)
    object_description: str = Field(...)
    object_required: bool = Field(...)
    object_type: Union[Boolean, Integer, Number, String, Enumeration, Date, DataStructure] = Field(...)
    
    def get_params_list(self) -> List[Tuple[str, str]]: #(param_name, param_description)
        params = []
        if hasattr(self.object_type, 'object_list'):
            for f in self.object_type.fields:
                params.append((f.object_name, f.object_description))
        else:
            params.append((self.object_name, self.object_description))
        return params
    def object_is_a_data_structure(self) -> bool:
        return hasattr(self.object_type, 'object_list')
    
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
    
    @staticmethod
    def len(obj : DataStructure) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='xtrk',
    _class = DataStructure,
    converter = Converter,
    additional_converters={
        'json':lambda x : x.model_dump()
        },
    visualiser = "https://vis.deepdocs.net/xtrk",
    icon = '/micons/pnpm_light.svg'
)