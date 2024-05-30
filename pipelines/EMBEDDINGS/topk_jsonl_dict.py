from typing import List 
import openai, numpy as np
import os
from custom_types.JSONL.type import JSONL
from scipy.spatial.distance import cdist

def execute_and_replace(dic, code_string):
    # Function to safely evaluate expressions using variables from the dictionary
    
    code_string = code_string.replace('\{', '_[_').replace('\}', '_]_')
    def evaluate_expression(expression, local_vars):
        try:
            # Evaluate the expression using variables from the dictionary
            return str(eval(expression, {}, local_vars))
        except Exception as e:
            # In case of any error, return the error message
            return f"Error in expression: {expression} - {e}"

    # Detect and replace code snippets within the string
    result_string = ""
    start_idx = 0
    while True:
        start_idx = code_string.find("{", start_idx)
        if start_idx == -1:
            break
        end_idx = code_string.find("}", start_idx)
        if end_idx == -1:
            break
        # Extract the expression within the brackets
        expression = code_string[start_idx + 1:end_idx]
        # Evaluate the expression and replace it in the string
        result_string += code_string[:start_idx] + evaluate_expression(expression, dic)
        code_string = code_string[end_idx + 1:]
        start_idx = 0

    result_string += code_string
    result_string = result_string.replace('_[_', '{').replace('_]_', '}')
    return result_string

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self,
                 dict_format: str,
                 jsonl_format: str,
                 n_to_keep: int = 20,
                 model: str = "text-embedding-ada-002",
                 ):
        self.model = model
        self.dict_format = dict_format
        self.jsonl_format = jsonl_format
        self.n_to_keep = n_to_keep

    def __call__(self, 
                 jsonl: JSONL, 
                 objective: dict
                 ) -> JSONL:
        if len(jsonl.lines) == 0:
            return jsonl
        api_key = os.environ.get("openai_api_key")
        texts = [execute_and_replace(_, self.jsonl_format) for _ in jsonl.lines]
        client = openai.OpenAI(api_key=api_key)
        embeddings = client.embeddings.create(input=texts, model=self.model).data
        embeddings = np.array([x.embedding for x in embeddings])
        objectives = [execute_and_replace(objective, self.dict_format)]
        objective_embeddings = client.embeddings.create(input=objectives, model=self.model).data
        objective_embeddings = np.array([x.embedding for x in objective_embeddings])
        
        distances = cdist(embeddings, objective_embeddings, metric='cosine')
        
        min_distances = distances.min(axis=1)
        sorted_indexes = np.argsort(min_distances)
        kept_indexes = sorted_indexes[:self.n_to_keep]
        
        return JSONL(lines=[jsonl.lines[_] for _ in kept_indexes])
