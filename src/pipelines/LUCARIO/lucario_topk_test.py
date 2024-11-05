




from typing import Any, List 
import os
import requests
import json

from custom_types.JSONL.type import JSONL



class Pipeline:

    ''' 

    Pipeline to perform a topk search on Lucario
     -> project_id: id of an existing project in Lucario 
     -> NOTE: for now only one query_text is supported
     -> NOTE: only one project id is supported
    
    '''


    def __init__(self,
                 project_id : str, # Project name to retrieve data using Lucario
                 k : int = 10, # Number of k chunks returned for similarity
                 max_per_information : int = 3 # Max number of indexed chunks per documnet that can be returned
                 ):
        
        self.project_id = project_id
        self.k = k
        self.max_per_information = max_per_information

    
    def __call__(self, query_text: str) -> str:

        json_payload = {
            "project_id": self.project_id,
            "query_text": query_text,
            "k": self.k,
            #"file_uuids": uuids,
            "max_per_information": self.max_per_information
            }
        top_k_response = requests.post(url ='https://lucario.croquo.com/top_k', json=json_payload)
        
        if top_k_response.status_code != 200:
            raise Exception(f'Unsuccessful response: {top_k_response}')
        
        json_out = [chunk for _ in top_k_response.json()['top_k_documents'] for chunk in _['chunks']]

        return json.dumps(json_out)
        

        


