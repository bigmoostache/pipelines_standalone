from dataclasses import dataclass
from typing import List, Literal, Union
import json

@dataclass
class Entry:
    name: str
    description: str
    value_type: Literal['int', 'str', 'float', 'bool', 'List[int]', 'List[str]', 'List[float]', 'List[bool]']
    required: bool = False
    supported_types = {'int', 'str', 'float', 'bool', 'List[int]', 'List[str]', 'List[float]', 'List[bool]'}
    
    def __post_init__(self):
        if self.value_type not in self.supported_types:
            raise ValueError(f"Unsupported value_type '{self.value_type}' provided. Supported types are: {', '.join(self.supported_types)}")
        assert isinstance(self.name, str), "name should be a valid string"
        assert isinstance(self.description, str), "description should be a valid string"
        assert isinstance(self.required, bool), "required should be True or False"
        assert len(self.name) > 0, "Variable name should not be empty"
        for c in [':',',',';','#','/']:
            assert c not in self.name, f"'{c}' should not be in variable name"
    
    def check(self, value) -> bool:
        if value is None:
            return not self.required
        
        if self.value_type == 'int':
            return isinstance(value, int)
        elif self.value_type == 'str':
            return isinstance(value, str)
        elif self.value_type == 'float':
            return isinstance(value, float)
        elif self.value_type == 'bool':
            return isinstance(value, bool)
        elif self.value_type == 'List[int]':
            return isinstance(value, list) and all(isinstance(x, int) for x in value)
        elif self.value_type == 'List[str]':
            return isinstance(value, list) and all(isinstance(x, str) for x in value)
        elif self.value_type == 'List[float]':
            return isinstance(value, list) and all(isinstance(x, float) for x in value)
        elif self.value_type == 'List[bool]':
            return isinstance(value, list) and all(isinstance(x, bool) for x in value)
        else:
            return False

class PDICT:
    def __init__(self, entries):
        self.entries = entries
        
    def __str__(self):
        result = "{\n"
        for i, e in enumerate(self.entries):
            virgule = "," if i != len(self.entries) - 1 else ""
            result += f'\t"{e.name}" : {e.value_type}{virgule} # {e.description}\n'
        result += "}"
        return result

    def to_dict(self):
        return [e.__dict__ for e in self.entries]

    def to_bytes(self):
        return bytes(json.dumps(self.to_dict(), indent = 2), 'utf-8')

    @classmethod
    def new(cls):
        return cls([])

    @classmethod
    def from_bytes(cls, b : bytes):
        return cls.from_dicts(json.loads(b.decode("utf-8")))

    @classmethod
    def from_dicts(cls, dicts: List[dict]):
        return cls([Entry(**_) for _ in dicts])

    def verify(self, dic: dict) -> None:
        # Create a dictionary for quick lookup of Entry by name
        entry_dict = {entry.name: entry for entry in self.entries}
        
        # Verify if the types of values match the expected types
        for key, value in dic.items():
            if key not in entry_dict:
                continue
            entry = entry_dict[key]
            if not entry.check(value):
                raise ValueError(f"Value for key '{key}' is not of type '{entry.value_type}'")
        
        # Optionally, verify if all required fields are present
        for entry in self.entries:
            if entry.required and entry.name not in dic:
                raise ValueError(f"Required key '{entry.name}' is missing")
    @classmethod
    def instructions(cls):
        vals = [f'"{x}"' for x in list(Entry.supported_types)]
        vals.sort(key=len)
        x = ', '.join(vals)
        
        r = f"""
        {{
            "variables" : [{{
            "name": str, # variable name, no special characters, not empty
            "description": str, # precise definition of the variable
            "value_type": str, Literal[{x}] # this should be a string picked in the available values,
            "required": bool
            }}]
        }}
        """
        return r
    
    def str_preview(self):
        return json.dumps(self.to_dict(), indent = 2)


from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='pdict',
    _class = PDICT,
    converter = PDICT,
)
