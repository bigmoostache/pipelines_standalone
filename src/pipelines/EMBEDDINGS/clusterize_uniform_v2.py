import openai, numpy as np, os
from typing import List
from custom_types.JSONL.type import JSONL
from sklearn.cluster import KMeans

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 n_per_cluster : int, 
                 to_embed_param : str,
                 n_rerolls : int = 4,
                 model : str = 'text-embedding-ada-002'):
        self.n_per_cluster = n_per_cluster
        self.model = model
        self.to_embed_param = to_embed_param
        self.n_rerolls = n_rerolls

    def __call__(self, 
                 elements : JSONL
                 ) -> List[JSONL]:
        elements = elements.lines
        api_key = os.environ.get("openai_api_key")
        x = [_[self.to_embed_param] for _ in elements]    
        client = openai.OpenAI(api_key=api_key)
        embeddings = client.embeddings.create(input = x, model=self.model).data
        embeddings = np.array([x.embedding for x in embeddings])
        k = len(x)//self.n_per_cluster
        best = np.inf
        best_labels = None
        for _ in range(self.n_rerolls):
            kmeans = KMeans(n_clusters=k).fit(embeddings)
            labels = kmeans.labels_
            n_per_label = np.bincount(labels)
            var = np.var(n_per_label)
            if var < best:
                best = var
                best_labels = labels
        res = {label:[] for label in range(k)}
        for dic, label in zip(elements, best_labels):
            res[label].append(dic)
        return [JSONL(lines = res[label]) for label in range(k)]
