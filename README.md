# How and Where to Work

This project uses a structured approach to ensure consistency and reliability.

## Directory Structure
- `src/custom_types/` contains type definitions and converters.
- `src/pipelines/` contains pipeline implementations.
- `docs/` contains documentation and guidelines.

## Workflow
- When adding a new pipeline or type, create a dedicated directory (if needed) and follow the established structure.
- Always write tests for your pipelines and types.
- Use clear naming conventions: snake_case for files and classes that match type or pipeline names in `PascalCase`.
- Commit frequently and write clear commit messages.

## Versioning and Changes
- Keep changes backward-compatible if possible.
- Update the documentation in `docs/` whenever you add new features or types.
- All new code should be properly typed and follow the code style guidelines.

## Communication
- Document assumptions and decisions in code comments or dedicated markdown files.
- When in doubt, ask or refer to existing examples within the repository.



# How to Write Pipelines

Pipelines are a fundamental concept in our system. Here are the guidelines:

## Overview
- Each pipeline is a Python class implementing a `__call__` method that takes specific typed inputs and returns a typed output.
- Pipelines are modular and should handle one responsibility only.

## Key Principles
- Always define a clear input and output type for each pipeline.
- Use existing types from `custom_types` or create new ones if needed.
- The pipeline should not rely on external state or global variables. Keep it pure and stateless.
- Follow the `Converter` patterns to ensure all inputs/outputs are properly serialized/deserialized.

## Structure of a Pipeline
- Pipelines usually live in `src/pipelines` directory.
- Each pipeline is a class with a `__init__` method (if needed) and a `__call__` method.
- No complex logic in the constructor. Keep initialization simple or empty.
- Document the pipeline’s purpose, inputs, and outputs in docstrings.

## Example
```python
class Pipeline:
    def __init__(self, param: str):
        self.param = param

    def __call__(self, input_data: SomeType) -> AnotherType:
        # Perform transformations
        result = ... # transform input_data
        return result
```

## Testing
- Test your pipeline with both expected and edge-case inputs.
- Ensure that all dependencies are available and no hidden assumptions are made.


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



# To build

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install the build tool
pip install build

# Navigate to your project's root directory (where pyproject.toml is)
cd my_package_project

# Run the build command
python -m build