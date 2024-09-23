import openai, os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self,top_k : int,
                 model : str = "text-embedding-3-large"):
        self.model = model
        self.top_k = top_k

    def __call__(self, 
                 texts : List[str], 
                 question : str
                 ) -> str:
        api_key = os.environ.get("openai_api_key")
        client = openai.OpenAI(api_key=api_key)
        _texts = [text.replace("\n", " ") for text in texts]
        embeddings = client.embeddings.create(input = _texts, model=self.model).data
        embeddings = np.array([x.embedding for x in embeddings])

        question_embedding = client.embeddings.create(input = [question], model=self.model).data[0].embedding
        question_embedding_reshaped = np.array(question_embedding).reshape(1, -1)
        cosine_similarities = cosine_similarity(question_embedding_reshaped, embeddings)
        top_k_indices = np.argsort(cosine_similarities[0])[-self.top_k:][::-1]

        pre_output = [texts[i] for i in top_k_indices]
        return "\n".join(pre_output)