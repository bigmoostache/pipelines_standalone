# How to Write Types

Types define the shape and serialization format of data flowing through the pipelines.

## Overview
- All types are declared in `src/custom_types/<TYPE_NAME>/type.py`.
- Types must define a Python class and a `Converter` class to handle bytes serialization/deserialization.
- Each type should be registered in `converter.py` for the system to recognize it.

## Defining a Type
- Use Python’s `@dataclass` for simple, clear definitions.
- Make sure every field has a clear and stable representation.
- Provide a `Converter` class with `to_bytes` and `from_bytes` methods.
- Optionally provide `additional_converters` for conversions to JSON or other formats.

## Example
```python
from typing import List
from dataclasses import dataclass
import json

@dataclass
class ExampleType:
    title: str
    values: List[int]

class Converter:
    @staticmethod
    def to_bytes(obj: ExampleType) -> bytes:
        return json.dumps(obj.__dict__).encode('utf-8')

    @staticmethod
    def from_bytes(b: bytes) -> ExampleType:
        data = json.loads(b.decode('utf-8'))
        return ExampleType(**data)

from custom_types.wrapper import TYPE
wrapped = TYPE(
    extension='example',
    _class=ExampleType,
    converter=Converter,
    additional_converters={
      'json': lambda x: x.__dict__
    }
)
```

## Guidelines
- Keep your type stable: Do not frequently change fields or their meanings.
- Ensure `from_bytes` and `to_bytes` are inverse operations.
- Add the type to `converter.py` so the system knows how to handle it.
