from custom_types.framework_formats.BLUEPRINTS.type import Blueprints
import os, json
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from enum import Enum

class EntrypointType(str, Enum):
    SINGLE = "SINGLE"
    MULTI = "MULTI"

class InputOutput(BaseModel):
    """Model for input and output configurations"""
    NAME: str
    URL_SAFE_NAME: str
    DESC: str
    TYPE: EntrypointType
    EXT: str
    COST: Optional[float] = 0.0

# Raw formats, as seed of the final compiled factory

class RawFactoryStep(BaseModel):
    pipeline: str
    parameters: Dict[str, Any] = {}
    entrypoints: Dict[str, str] = {}
    duplicates: int = 1
    description: str = ""

class RawFactory(BaseModel):
    factoryName: str
    entrypoints: Dict[str, InputOutput]
    factory: Dict[str, RawFactoryStep]
    outputs: Dict[str, InputOutput]
    description: Optional[str] = ""

# Compiled factory, ready to be used in the framework

class FactoryStep(BaseModel):
    """Model for individual factory pipeline steps"""
    pipeline: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    entrypoints: Dict[str, str] = Field(default_factory=dict)
    description: str
    scope: Optional[Dict[int, str]] = None
    entrypoint_types: Dict[str, EntrypointType] = Field(default_factory=dict)
    output_type: EntrypointType
    step: int
    creates: List[str] = Field(default_factory=list)
    unlocks: List[str] = Field(default_factory=list)
    arrival_scope: Optional[Dict[int, str]] = None
    
    @classmethod
    def from_raw_step(cls, raw_step: RawFactoryStep) -> 'FactoryStep':
        """Create a FactoryStep from a RawFactoryStep"""
        return cls(
            pipeline=raw_step.pipeline,
            parameters=raw_step.parameters,
            entrypoints=raw_step.entrypoints,
            description=raw_step.description,
            scope={},
            entrypoint_types={},
            output_type=EntrypointType.SINGLE,  # Default, can be overridden later
            step=0,  # Default, can be overridden later
            creates=[],
            unlocks=[],
            arrival_scope={}
        )

class CompiledFactory(BaseModel):
    """Main factory configuration model"""
    entrypoints: Dict[str, EntrypointType]
    inputs: Dict[str, InputOutput]
    factory: Dict[str, FactoryStep]
    output: Dict[str, str]
    outputs: Dict[str, InputOutput]
    factoryName: str
    description: Optional[str] = ""
    env: List[str] = Field(default_factory=list)
    
    # New entries, meant to render the factory basically standalone
    raw: Optional[RawFactory] = None
    blueprints: Optional[Blueprints] = None
    sub_factories: Optional[Dict[str, RawFactory]] = {}
   
class Converter:
    @staticmethod
    def to_bytes(obj : CompiledFactory) -> bytes:
        return bytes(obj.model_dump_json(indent = 4), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> CompiledFactory:
        return CompiledFactory.model_validate(json.loads(obj.decode('utf-8')))
    
    @staticmethod
    def len(obj : CompiledFactory) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='factory',
    _class = CompiledFactory,
    converter = Converter,
    additional_converters={},
    visualiser = "https://vis.deepdocs.net/factory",
)
