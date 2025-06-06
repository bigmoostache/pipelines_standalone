from custom_types.framework_formats.BLUEPRINTS.type import Blueprints
import os, converter, json
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
    
    def recursively_add_pipelines(
            self, 
            raw_factory: RawFactory, 
            pipeline_id: str, 
            prefix: str = ''
            ):
        pipeline = raw_factory.factory[pipeline_id]
        
        if pipeline.duplicates > 1:
            duplicate_id = f'{prefix}{pipeline_id}_duplicate'
            duplicate_pipeline = FactoryStep.from_raw_step(FactoryStep(
                pipeline="_duplicate",
                parameters={"n_duplicates": pipeline.duplicates},
                entrypoints=pipeline.entrypoints,
                duplicates=1,
                description=f"Duplicate of {pipeline_id} with {pipeline.duplicates} duplicates"
            ))
            pipeline_blueprint = self.blueprints.blueprints[pipeline.pipeline]
            duplicate_pipeline.entrypoint_types = {k:v.type for k,v in pipeline_blueprint.inputs.items()}
            self.factory[duplicate_id] = duplicate_pipeline
        else:
            duplicate_id = None
            
        if pipeline.pipeline in self.blueprints.blueprints:
            self.factory[f'{prefix}{pipeline_id}'] = FactoryStep.from_raw_step(RawFactoryStep(
                pipeline=pipeline.pipeline,
                parameters=pipeline.parameters,
                entrypoints={k: f'{prefix}{v}' for k, v in pipeline.entrypoints.items()},
                duplicates=1,
                description=pipeline.description
            ))
            if duplicate_id:
                self.factory[f'{prefix}{pipeline_id}'].entrypoints["__duplicate__"] = duplicate_id
        
        elif pipeline.pipeline in self.sub_factories:
            sub_factory = self.sub_factories[pipeline.pipeline]
            for sub_pipeline_id, sub_pipeline in sub_factory.factory.items():
                subprefix = f'{prefix}.{pipeline_id}'
                # If inputs of this pipeline are entrypoints of the sub-factory, we need to adjust them to use outputs of the main factory instead
                for k, v in sub_pipeline.entrypoints.items():
                    if v in sub_factory.entrypoints:
                        sub_pipeline.entrypoints[k] = pipeline.entrypoints[k]
                self.recursively_add_pipelines(sub_factory, sub_pipeline_id, prefix=subprefix)
            # TODO -> duplicate_id, connecting entrypoints, etc.
        else:
            raise ValueError(f"Pipeline {pipeline.pipeline} not found in blueprints or sub-factories.")
    
    def build_actual_factory(self):
        self.entrypoints, self.inputs, self.factory, self.output, self.outputs = {}, {}, {}, {}, {}
        
        # 1 - Import factories from blueprints, or sub-factories
        for pipeline in self.raw.factory.values():
            self.recursively_add_pipelines(self.raw, pipeline.pipeline)
        
        # 2 - create variables
        self.entrypoints = {e_id: e.TYPE for e_id, e in self.raw.entrypoints.items()}

        # 2 - add entrypoints to factory
        for entrypoint_id, entrypoint in self.raw.entrypoints.items():
            if v == "MULTI":
                self.factory[k+METADATA_EXTENSION] = FactoryStep.from_raw_step(RawFactoryStep(
                    pipeline="_multi_feed_pipeline",
                    description=f"Multi feed pipeline for {entrypoint_id}"
                ))
                next_scope = {0 : "FACTORY", 1 : k+METADATA_EXTENSION}
            elif v == "SINGLE":
                self.factory[k+METADATA_EXTENSION] = FactoryStep.from_raw_step(RawFactoryStep(
                    pipeline="_single_feed_pipeline",
                    description=f"Single feed pipeline for {entrypoint_id}"
                ))
                next_scope = {0 : "FACTORY"}
            else:
                raise HTTPException(f"Unknown entrypoint type {v}")
            
            self.factory[k] = FactoryStep.from_raw_step(RawFactoryStep(
                pipeline=f'_SFP_{entrypoint.EXT}',
                entrypoints={"metadata": k+METADATA_EXTENSION},
                description=f"Feeder for {k}"
            ))
        
        # 4 - Pipeline inputs and output types (MULTI or SINGLE)
        for k,v in self.factory.items():
            f = self.blueprints.blueprints[v.pipeline]
            if not f:
                v.entrypoint_types = {_input_name: _input.type for _input_name, _input in f.inputs.items()}
            v.output_type = f.output_type
        for k,v in self.factory.items():
            if set(v.entrypoints.keys()) - set(v.entrypoint_types.keys()) == {"__duplicate__"}:
                v.entrypoint_types["__duplicate__"] = EntrypointType.SINGLE
        
        # 5 - Resolving scopes, ie domains of execution for each pipeline
        n_iterations = 0
        order = 0
        logging.debug(f"5 - resolving scopes")
        while True in {v.scope is None for k,v in self.factory.items()}:
            n_iterations += 1
            for pipeline_id, pipeline in self.factory.items():
                if v.scope is None:
                    parent_scopes = {entrypoint: self.factory[_pipeline_id].scope for entrypoint, _pipeline_id in pipeline.entrypoints.items()}
                    if True in {v is None for v in parent_scopes.values()}:
                        continue
                    scope = {}
                    for entrypoint, entrypoint_id in pipeline.entrypoints.items():
                        stop = pipeline.entrypoint_types[entrypoint] == EntrypointType.MULTI
                        _max = max(parent_scopes[kp].keys(), default=0)
                        for s, s_id in parent_scopes[kp].items():
                            if not stop or s!=_max:
                                scope[s] = scope.get(s, set()) | {s_id}
                    if not all([len(_v) == 1 for _v in scope.values()]):
                        raise HTTPException(status_code=504, detail=f"Scope conflict for pipeline {k} with scope {scope}")
                    scope = {_k: list(_v)[0] for _k,_v in scope.items()}
                    if pipeline.output_type == EntrypointType.MULTI:
                        scope[max(scope.keys(), default=0) + 1] = k
                    pipeline.scope = scope
                    order += 1
                    pipeline.step = order
            if n_iterations > 2 * len(self.factory) + 2:
                raise HTTPException(status_code=5, detail="Cannot resolve scopes : too many iterations.")
        
        
        # 6 - resolve who creates whom
        for _, pipeline in self.factory.items():
            if pipeline.output_type == EntrypointType.MULTI:
                pipeline.scope.pop(max(pipeline.scope.keys(), default = 0), None)
        for pipeline_id, pipeline in self.factory.items():
            pipeline.creates = self.a_should_create(pipeline_id)

        # 7 - now let's create the dictionary of "unlocks"
        for pipeline_id, pipeline in self.factory.items():
            if not pipeline.output_type == EntrypointType.MULTI:
                v.unlocks = []
                continue
            scope_to_check = v.scope.copy()
            scope_to_check[max(scope_to_check.keys(), default = 0) + 1] = pipeline_id
            v.unlocks = [
                _pipeline_id for _pipeline_id, _pipeline in self.factory.items() if 
                _pipeline.scope == pipeline.scope
                and 
                any(
                    (self.factory[i].scope == scope_to_check) or (i==pipeline_id)
                    for i in _pipeline.entrypoints.values()
                )
            ]

        # 8 - now let's create the arrival scopes
        for k,v in self.factory.items():
            if v.output_type == EntrypointType.MULTI:
                v["arrival_scope"] = v["scope"].copy()
                v["arrival_scope"][max(v["arrival_scope"].keys(), default = 0) + 1] = k
            else:
                v["arrival_scope"] = v["scope"].copy()

        # 9 - now let's check that the arrival scopes of results have max depth 1
        for k,v in self.output.items():
            result_depth = max(self.factory[v]["arrival_scope"].keys(), default = 0)
            if result_depth > 1:
                raise HTTPException(status_code=408, detail=f"Result {k} has depth {result_depth} > 1")
        
        # 10 - add the description to the factory pipelines
        for k,v in self.factory.items():
            if 'description' in v and v['description']:
                continue
            elif hasattr(PIPELINES[v["pipeline"]].pipeline, "__DESCRIPTION__"):
                v['description'] = PIPELINES[v['pipeline']].pipeline.__DESCRIPTION__
            else:
                v['description'] = generate_pinguin_name()
        return 
    
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
    additional_converters={}
)
