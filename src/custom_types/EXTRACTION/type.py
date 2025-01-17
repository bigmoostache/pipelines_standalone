from enum import Enum
from pydantic import BaseModel, Field, create_model
from typing import List, Union

class ValueType(Enum):
    STR = 'str'
    INT = 'int'
    FLOAT = 'float'
    BOOLEAN = 'boolean'
    DATE = 'date'
    DURATION = 'duration'
    
ValueTypeToType = {
    "str" : str,
    "int" : int,
    "float": float,
    "boolean" : bool,
    "date" : str,
    "duration" : str
}
    
class ValueMultiplicity(Enum):
    SINGLE = 'Single'
    LIST = 'List'

class Entry(BaseModel):
    name: str = Field(..., description="Uppercase and underscores, but no spaces, not special characters and no numbers")
    description: str = Field(..., description="Precise description of this value")
    examples: List[Union[str,int,float,bool]] = Field(..., description="Examples of values")
    value: ValueType = Field(..., description = "Type of the value")
    multiple : ValueMultiplicity = Field(..., description = "Whether to find a list or a single value. Examples: CHILDREN_NAMES would have LIST, while FAMILY_NAME would have SINGLE")
    unit: str = Field(..., description = "Unit of the value. For str, boolean, date and duration values, just give na. For int and float, you MUST provide a unit")

class Entries(BaseModel):
    entries : List[Entry]
    one_entry_per_document_justification : bool = Field(..., description = "Justify your answer to: will each provided document to analyse have one, or multiple rows to extract? (one, or multiple rows?)")
    one_entry_only_per_document : bool = Field(..., description = "Will each provided document to analyse have one, or multiple rows to extract? (one, or multiple rows?)")
    entry_definition : str = Field(..., description = "In case one_entry_only_per_document = false, describe here precisely how to properly define a single row of entries. With this definition alone, it should be clear to anyone with the document at hand which and how many rows of entries to extract from the document. If one_entry_only_per_document = true, just return 'na' here")
    
    def get_model(self):
        x = {}
        for e in self.entries:
            # x[e.name+'_JUSTIFICATION'] = (str, Field(..., description = f'Justifiy briefly the answer you want to give to {e.name} ({e.description}). Be fair and unbiased. Your reflexion should aim at avoiding traps, making sure not to miss data, and avoid errors.'))
            x[e.name] = (
                    (ValueTypeToType[e.value.value] if e.multiple == ValueMultiplicity.SINGLE else List[ValueTypeToType[e.value.value]])
                    , Field(..., description = e.description)
            )
        return create_model("Data", **x)
    
    def get_nested_model(self):
        basemodel = self.get_model()
        if self.one_entry_only_per_document:
            return basemodel
        else:
            x = {
                "rows_analysis" : (str, Field(..., description = f'{self.entry_definition}. In this field, analyse and determine all the rows you can extract from the document. Be precise and exhaustive. Make sure to differentiate the rows properly, not to forget any, and to avoid errors.')),
                "rows" : (List[basemodel], Field(..., description = f'Extract the rows you defined above. Be careful to extract the right amount of rows, and to differentiate them properly.'))
            }
            return create_model("Data", **x)
        
    def get_result_dict(self, parsed_data, keep_justifications : bool = False) -> List[dict]:
        x = []
        if self.one_entry_only_per_document:
            dico = parsed_data.model_dump()
            if not keep_justifications:
                dico = {k:v for k,v in dico.items() if not k.endswith('_JUSTIFICATION')}
            x.append(dico)
        else:
            for row in parsed_data.rows:
                dico = row.model_dump()
                if not keep_justifications:
                    dico = {k:v for k,v in dico.items() if not k.endswith('_JUSTIFICATION')}
                x.append(dico)
        return x

# Things to make it work in our framework
import json
class Converter:
    @staticmethod
    def to_bytes(obj : Entries) -> bytes:
        return bytes(obj.model_dump_json(), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> 'Entries':
        return Entries.parse_obj(json.loads(obj.decode('utf-8')))
    
    @staticmethod
    def len(obj : Entries) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='extraction',
    _class = Entries,
    converter = Converter,
    additional_converters={
        'json':lambda x : x.model_dump()
        },
    visualiser = "https://vis.deepdocs.net/extraction",
    icon = '/micons/pnpm_light.svg'
)