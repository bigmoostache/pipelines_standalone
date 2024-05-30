from typing import List 
import openai, numpy as np
import os
from custom_types.JSONL.type import JSONL
from scipy.spatial.distance import cdist

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self,
                 text_param: str,
                 n_to_keep: int = 20,
                 model: str = "text-embedding-ada-002",
                 uniform_per_request: bool = False
                 ):
        self.model = model
        self.text_param = text_param
        self.n_to_keep = n_to_keep
        self.uniform_per_request = uniform_per_request

    def __call__(self, 
                 jsonl: JSONL, 
                 objectives: List[str]
                 ) -> JSONL:
        if len(jsonl.lines) == 0:
            return jsonl
        elif len(objectives) == 0:
            return JSONL(jsonl.lines[:self.n_to_keep])
        api_key = os.environ.get("openai_api_key")
        texts = [_[self.text_param] for _ in jsonl.lines]
        client = openai.OpenAI(api_key=api_key)
        embeddings = client.embeddings.create(input=texts, model=self.model).data
        embeddings = np.array([x.embedding for x in embeddings])
        objective_embeddings = client.embeddings.create(input=objectives, model=self.model).data
        objective_embeddings = np.array([x.embedding for x in objective_embeddings])
        
        distances = cdist(embeddings, objective_embeddings, metric='cosine')
        
        if not self.uniform_per_request:
            min_distances = distances.min(axis=1)
            sorted_indexes = np.argsort(min_distances)
            kept_indexes = sorted_indexes[:self.n_to_keep]
        else:
            n_per_objective = self.n_to_keep // len(objectives)
            kept_indexes_set = set()
            for i in range(len(objectives)):
                objective_distances = distances[:, i]
                sorted_indexes = np.argsort(objective_distances)
                count = 0
                for idx in sorted_indexes:
                    if idx not in kept_indexes_set and count < n_per_objective:
                        kept_indexes_set.add(idx)
                        count += 1
                    if count >= n_per_objective:
                        break
            kept_indexes = list(kept_indexes_set)
        
        return JSONL(lines=[jsonl.lines[_] for _ in kept_indexes])
