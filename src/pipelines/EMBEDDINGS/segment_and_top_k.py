import openai, os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self,top_k : int,
                segment_max_chars: int = 2000,
                 model : str = "text-embedding-3-large"):
        self.model = model
        self.top_k = top_k
        self.max_chars = segment_max_chars

    def __call__(self, 
                question : str,
                article : str
                 ) -> str:
        
        matches = [[m.group(0), (m.start(), m.end() - 1)] for m in re.finditer(r'(?!\\n\\n)([^\n]|\\n(?!\\n))+', article)]
        chunked_text, split_idx = zip(*matches)
        new_chunked_text = []
        new_split_idx = []
        for i, chunk in enumerate(chunked_text):
            length = len(chunk)
            diff = length - self.max_chars

            if diff>0:
                new_chunked_text.append(chunk[0:self.max_chars])
                start, end = split_idx[i][0], split_idx[i][1]
                new_split_idx.append((start, end +1 - diff))
            else: 
                new_chunked_text.append(chunk)
                start, end = split_idx[i][0], split_idx[i][1]
                new_split_idx.append((start, end+1))
        

        texts = new_chunked_text

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
    







from typing import List
import re

class Pipeline:

    def __init__(self,
                 ):
        

    def __call__(self, article :str) -> List[str]:
        matches = [[m.group(0), (m.start(), m.end() - 1)] for m in re.finditer(r'(?!\\n\\n)([^\n]|\\n(?!\\n))+', article)]
        chunked_text, split_idx = zip(*matches)
        new_chunked_text = []
        new_split_idx = []
        for i, chunk in enumerate(chunked_text):
            length = len(chunk)
            diff = length - self.max_chars

            if diff>0:
                new_chunked_text.append(chunk[0:self.max_chars])
                start, end = split_idx[i][0], split_idx[i][1]
                new_split_idx.append((start, end +1 - diff))
            else: 
                new_chunked_text.append(chunk)
                start, end = split_idx[i][0], split_idx[i][1]
                new_split_idx.append((start, end+1))
        return new_chunked_text
