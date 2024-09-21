
from custom_types.SOTA.type import SOTA, pipelines, Embedder
from custom_types.JSONL.type import JSONL
from typing import List 

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, sota : SOTA, embeddings: JSONL) -> SOTA:
        embedders = [Embedder(**_) for _ in embeddings.lines]
        sota.embed(embedders)
        information_id_to_embedders = {}
        versions_list = sota.versions_list(-1)
        for embedder in embedders:
            information_id_to_embedders[embedder.information_id] = information_id_to_embedders.get(embedder.information_id, [])
            information_id_to_embedders[embedder.information_id].append(embedder)
        for information_id, embedders in information_id_to_embedders.items():
            information = sota.information[information_id]
            last_id = sota.get_last(information.versions, versions_list, return_id=True)
            information.embeddings = {last_id : [_.section_id for _ in embedders]}  
        return sota