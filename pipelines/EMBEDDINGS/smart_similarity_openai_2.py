import openai, os, re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

class Pipeline:
    __env__ = ["openai_api_key"]

    def __init__(self,    
                 top_k : int = 10,
                 text_key:str = "texts",                 
                 model : str = "text-embedding-ada-002"):
        self.model = model
        self.top_k = top_k
        self.text_key = text_key
        

    def __call__(self, 
                 segments : List[dict], 
                 question : str) -> List[dict]:
        client = openai.OpenAI(api_key=api_key)
        
        api_key = os.environ.get("openai_api_key")
        
        _texts = [re.sub(r'\s+', ' ', item[self.text_key]) for item in segments]

        embeddings = client.embeddings.create(input = _texts, model=self.model).data
        embeddings = np.array([x.embedding for x in embeddings])

        question_embedding = client.embeddings.create(input = [question], model=self.model).data[0].embedding
        question_embedding_reshaped = np.array(question_embedding).reshape(1, -1)
        cosine_similarities = cosine_similarity(question_embedding_reshaped, embeddings)
        top_k_indices = np.argsort(cosine_similarities[0])[-self.top_k:][::-1]

        return [segments[i] for i in top_k_indices]
        

