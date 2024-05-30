from typing import List 
import openai, numpy as np
import os

from custom_types.JSONL.type import JSONL
from scipy.spatial.distance import cdist
class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self,
                 text_param: str,
                 query_text_param : str,
                 n_to_keep: int = 20,
                 model: str = "text-embedding-3-large",
                 uniform_per_request: bool = False
                 ):
        self.model = model
        self.text_param = text_param
        self.n_to_keep = n_to_keep
        self.uniform_per_request = uniform_per_request
        self.query_text_param = query_text_param

    def __call__(self, 
                 jsonl: JSONL, 
                 objectives: JSONL
                 ) -> JSONL:
        if len(jsonl.lines) == 0:
            return jsonl
        elif len(objectives.lines) == 0:
            return JSONL(jsonl.lines[:self.n_to_keep])
        
        api_key = os.environ.get("openai_api_key")
        texts = [_[self.text_param] for _ in jsonl.lines]
        texts = [x.strip() for x in texts]
        texts = [x if x else 'no data' for x in texts]
        objectives = [_[self.query_text_param] for _ in objectives.lines]
        objectives = [x.strip() for x in objectives]
        objectives = [x if x else 'no data' for x in objectives]
        client = openai.OpenAI(api_key=api_key)
        def get_embeddings_in_chunks(texts, model, chunk_size=1024):
            embeddings = []
            for i in range(0, len(texts), chunk_size):
                chunk = texts[i:i + chunk_size]
                try:
                    response = client.embeddings.create(input=chunk, model=model).data
                except:
                    response = client.embeddings.create(input=['no data here'] * len(chunk), model=model).data
                embeddings.extend(response)
            return np.array([x.embedding for x in embeddings])
        embeddings = get_embeddings_in_chunks(texts, self.model)
        objective_embeddings = get_embeddings_in_chunks(objectives, self.model)
        keep = np.array([np.inf if len(_)<=20 else 1 for _ in texts])
        distances = cdist(embeddings, objective_embeddings, metric='cosine')
        distances = distances * keep[:, None]
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