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
