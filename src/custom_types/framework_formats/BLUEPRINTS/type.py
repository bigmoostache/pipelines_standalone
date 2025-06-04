from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any
from enum import Enum
import json, os, converter,  importlib, inspect

def analyse(dump_res_here: dict, folder: str):
    ignore = {
        '_duplicate',
        '_multi_feed_pipeline',
        '_single_feed_pipeline',
        '__pycache__'
    }
    for pipeline_name in [x[:-3] for x in os.listdir(folder) if x.endswith(".py") and x[:-3] not in ignore]:
        print(f"Analysing {pipeline_name} in {folder.replace('/', '.')}")
        pipeline_full_name = f"{folder.replace('/', '.')}.{pipeline_name}"
        pipeline = importlib.import_module(pipeline_full_name, '').Pipeline
        
        init_args = inspect.getfullargspec(pipeline.__init__)
        defaults = init_args.defaults
        defaults = defaults if defaults is not None else []
        OPTIONAL_PARAMETERS = {k:v for k,v in zip(init_args.args[-len(defaults):], defaults)}
        if init_args.defaults is not None:
            REQUIRED_PARAMETERS = init_args.args[1:-len(defaults)]
        else:
            REQUIRED_PARAMETERS = init_args.args[1:]

         # let's build parameter types
        PARAMETER_TYPES = {}
        for k in REQUIRED_PARAMETERS:
            PARAMETER_TYPES[k] = converter.CLASS_TO_EXT(init_args.annotations.get(k, str))[0]
        for k in OPTIONAL_PARAMETERS:
            PARAMETER_TYPES[k] = converter.CLASS_TO_EXT(init_args.annotations.get(k, str))[0]

        # entrypoints
        call_args = inspect.getfullargspec(pipeline.__call__)
        RESULT_TYPE = converter.CLASS_TO_EXT(call_args.annotations.get("return", str))[0]
        INPUT_TYPES = {k:converter.CLASS_TO_EXT(call_args.annotations.get(k, str))[1] for k in call_args.args[1:]}
        assert set(call_args.args[1:]) == set(INPUT_TYPES.keys()), f"Pipeline {pipeline_name} does not have the correct parameters: {call_args.args[1:]} != {INPUT_TYPES.keys()}"
        # used to perform bytes -> file conversion and vice versa
        ENTRYPOINT_TYPES = {k:converter.CLASS_TO_EXT(call_args.annotations.get(k, str))[0] for k in INPUT_TYPES.keys()}
        OUTPUT_TYPE = converter.CLASS_TO_EXT(call_args.annotations.get("return", str))[1]

        res = {
            "result_type": RESULT_TYPE,
            "output_type": OUTPUT_TYPE,
            "parameters": {
                k:{
                    "type":v,
                    "isRequired": k in REQUIRED_PARAMETERS,
                    "defaultValue": OPTIONAL_PARAMETERS.get(k, None)
                } for k,v in PARAMETER_TYPES.items()
            },
            "inputs": {
                k:{
                    "ext":ENTRYPOINT_TYPES[k],
                    "allowed_inputs" : converter._allowed_inputs[ENTRYPOINT_TYPES[k]],
                    "type": v
                } for k,v in INPUT_TYPES.items()
            }
        }
        dump_res_here[pipeline_full_name] = res
    
    folders = [os.path.join(folder, x) for x in os.listdir(folder) if os.path.isdir(os.path.join(folder, x)) and x not in ignore]
    for folder in folders:
        analyse(dump_res_here, folder)
        
class OutputType(str, Enum):
    """Enum for output types"""
    SINGLE = "SINGLE"
    MULTI = "MULTI"

class Parameter(BaseModel):
    """Model for pipeline parameters"""
    type: str = Field(..., description="Parameter type (e.g., 'txt', 'int', 'bool', 'float', or comma-separated enum values)")
    isRequired: bool = Field(..., description="Whether the parameter is required")
    defaultValue: Optional[Any] = Field(None, description="Default value for the parameter")

class Input(BaseModel):
    """Model for pipeline inputs"""
    ext: str = Field(..., description="File extension or input type")
    allowed_inputs: List[str] = Field(..., description="List of allowed input types")
    type: OutputType = Field(..., description="Whether input accepts single or multiple values")

class Blueprint(BaseModel):
    """Model for individual pipeline blueprint"""
    result_type: str = Field(..., description="Type of result produced by the pipeline")
    output_type: OutputType = Field(..., description="Whether pipeline produces single or multiple outputs")
    parameters: Dict[str, Parameter] = Field(default_factory=dict, description="Pipeline parameters")
    inputs: Dict[str, Input] = Field(default_factory=dict, description="Pipeline inputs")

class Blueprints(BaseModel):
    """Model for collection of pipeline blueprints"""
    blueprints: Dict[str, Blueprint] = Field(..., description="Dictionary mapping pipeline names to blueprint definitions")
    
    @classmethod
    def generate(cls, folder: str = 'pipelines') -> 'Blueprints':
        """Generates blueprints from the specified folder containing pipeline definitions."""
        dump_res_here = {}
        analyse(dump_res_here, folder)
        return cls.model_validate({'blueprints': dump_res_here})
    
class Converter:
    @staticmethod
    def to_bytes(obj : Blueprints) -> bytes:
        return bytes(obj.model_dump_json(indent = 4), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> Blueprints:
        return Blueprints.model_validate(json.loads(obj.decode('utf-8')))
    
    @staticmethod
    def len(obj : Blueprints) -> int:
        return len(obj.blueprints)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='blueprints',
    _class = Blueprints,
    converter = Converter,
    additional_converters={
        'json':lambda x : x.model_dump()
    }
)
