from typing import List 
import openai, os, numpy as np, math
from custom_types.JSONL.type import JSONL
from custom_types.LUCARIO.type import LUCARIO

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self,
                embedding_model : str = 'text-embedding-3-large',
                anchor_key : str = 'anchors',
                max_groups_per_element : int = 1,
                elements_per_group : int = 1,
                min_elements_per_list : int = 1,
                **kwargs : dict
                ):
        self.__dict__.update(locals())
        self.__dict__.pop("self")

    def __call__(self, 
                sections : JSONL,
                lucario : LUCARIO
                ) -> JSONL:
        lucario.update()
        references = {_.file_id: _.description for _ in lucario.elements.values()}
        result = lucario.anchored_top_k(
            queries = [_ for section in sections.lines for _ in section[self.anchor_key]],
            group_ids = [i for i, _ in enumerate(sections.lines) for __ in section[self.anchor_key]],
            max_groups_per_element = self.max_groups_per_element,
            elements_per_group = self.elements_per_group,
            min_elements_per_list = self.min_elements_per_list
        )
        lines = [_.model_dump() for _ in result]
        # enrich the lines with the references
        for line in lines:
            line['reference'] = references.get(line['parent_file_id'], '')
        return JSONL(lines)