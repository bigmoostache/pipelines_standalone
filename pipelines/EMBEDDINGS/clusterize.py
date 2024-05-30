from typing import List 
import openai, os, numpy as np
from custom_types.JSONL.type import JSONL
from sklearn.cluster import KMeans

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self,
                text_param : str,
                 num_clusters: int = 30,
                 n_rerolls : int = 10,
                model : str = "text-embedding-ada-002"
                 ):
        self.num_clusters = num_clusters
        self.model = model
        self.text_param = text_param
        self.n_rerolls = n_rerolls

    def __call__(self, 
                 jsonl : JSONL
                 ) -> List[JSONL]:
        api_key = os.environ.get("openai_api_key")
        x = jsonl.lines
        client = openai.OpenAI(api_key=api_key)
        _texts = [_[self.text_param] for _ in x]
        embeddings = client.embeddings.create(input = _texts, model='text-embedding-ada-002').data
        embeddings = np.array([x.embedding for x in embeddings])
        best = np.inf
        best_labels = None
        for _ in range(self.n_rerolls):
            kmeans = KMeans(
                n_clusters=self.num_clusters, 
                random_state=0, 
                max_iter = 2000
                ).fit(embeddings)
            labels = kmeans.labels_
            n_per_label = np.bincount(labels)
            var = np.var(n_per_label)
            if var < best:
                best = var
                best_labels = labels

        labels = best_labels
        clusters = {label:[] for label in range(self.num_clusters)}

        for dic, label in zip(x, labels):
            dic["label"] = str(label)
            clusters[label].append(dic)

        return [JSONL(lines = clusters[label]) for label in range(self.num_clusters)]
