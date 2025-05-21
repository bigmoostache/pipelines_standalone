from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
import uuid
from enum import Enum

class Relationship(Enum):
    PARENT = 'parent'
    CHILD = 'child'
    SIBLING = 'sibling'
    FRIEND = 'friend'
    COLLEAGUE = 'colleague'
    PARTNER = 'partner'

# Define the Node model
class Node(BaseModel):
    id: str
    name: str

# Define the Edge model
class Edge(BaseModel):
    source: str  # Node ID of source
    target: str  # Node ID of target
    kind: Relationship

# Define the SimpleGraph model
class SimpleGraph(BaseModel):
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)

# Define the Converter class for SimpleGraph
class Converter:
    @staticmethod
    def to_bytes(graph: SimpleGraph) -> bytes:
        """Convert SimpleGraph to bytes"""
        def default(obj):
            if isinstance(obj, Enum):
                return obj.value
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
        return bytes(json.dumps(graph.model_dump(), default=default), 'utf-8')

    @staticmethod
    def from_bytes(b: bytes) -> SimpleGraph:
        """Convert bytes to SimpleGraph"""
        data = json.loads(b.decode('utf-8'))
        return SimpleGraph.model_validate(data)
    
    @staticmethod
    def len(graph: SimpleGraph) -> int:
        """Compute the length of the graph for cost calculation"""
        return max(1, (len(graph.nodes) + len(graph.edges)) // 100)
from custom_types.wrapper import TYPE
# Wrap the type
wrapped = TYPE(
    extension='tutorial_demo',
    _class=SimpleGraph,
    converter=Converter,
    additional_converters={
        'json': lambda x: x.model_dump(),
    },
    visualiser="https://vis.deepdocs.net/tutorial_demo_vis",
    icon='/icons/graph.svg'
)