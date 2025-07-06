import json, re
from typing import List, Union, Literal, Optional, Dict
from pydantic import BaseModel, Field

class PipelineGroupExecutionReport(BaseModel):
    pipeline_group_id: str
    pipeline_name: str
    pipeline_code: str
    pipeline_parameters: Dict[str, Union[str, int, float, bool]]
    pipeline_inputs: Dict[str, str]
    
    count: int
    
class UserExecutionReport(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    user_image: str

class ExecutionReport(BaseModel):
    factory_id: str
    project_id: str
    solution_url: str
    
    rocket_cost: float
    
    start_time: int # Unix timestamp in seconds
    end_time: int # Unix timestamp in seconds
    
    user: UserExecutionReport
    
    pipelines_standalone_repo: str # URL of the pipelines_standalone repository from which pipelines' codes are fetched
    pipelines_standalone_commit: str # Commit hash of the pipelines_standalone repository

    pipelines: List[PipelineGroupExecutionReport]

class Converter:
    @staticmethod
    def to_bytes(article : ExecutionReport) -> bytes:
        return bytes(json.dumps(article.model_dump(), indent = 2), encoding = 'utf-8')

    @staticmethod
    def from_bytes(b: bytes) -> ExecutionReport:
        return Plan.parse_obj(json.loads(b.decode('utf-8')))

    @staticmethod
    def len(article : ExecutionReport) -> int:
        return 1
    
from custom_types.wrapper import TYPE

wraped = TYPE(
    extension='report',
    _class=ExecutionReport,
    converter=Converter,
    additional_converters={
        'json': lambda x: x.model_dump(),
    },
    visualiser="https://vis.deepdocs.net/report",
    icon='/icons/graph.svg'
)