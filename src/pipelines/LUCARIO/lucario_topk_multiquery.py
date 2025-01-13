

from typing import Any, List 
import os
import requests
import json
from custom_types.JSONL.type import JSONL
import traceback


class Pipeline:

    ''' 

    Pipeline to perform multiple topk search on Lucario on multiple queries
     -> project_id: id of an existing project in Lucario 

    -> The queries input must be a JSONL of structure: 
                {'query':'your_query_1'}
                {'query':'your_query_2'}

    '''

    def __init__(self,
                 project_id : str, # Project name to retrieve data using Lucario
                 k : int = 10, # Number of k chunks returned for similarity
                 max_per_information : int = 3, # Max number of indexed chunks per documnet that can be returned
                 ):
        
        self.project_id = project_id
        self.k = k
        self.max_per_information = max_per_information

    
    def __call__(self, queries: JSONL) -> JSONL:

        super_chunk_list = []
         
        try:

            for query in [line['query'] for line in queries.lines]:

                json_payload = {
                    "project_id": self.project_id,
                    "query_text": query,
                    "k": self.k,
                    #"file_uuids": uuids,
                    "max_per_information": self.max_per_information
                    }
                
                top_k_response = requests.post(url ='https://lucario.croquo.com/top_k', json=json_payload)
                if top_k_response.status_code != 200:
                    raise Exception(f'Unsuccessful response: {top_k_response}')
                # extract the chunks retrieved by topk
                super_chunk_list.extend([chunk for _ in top_k_response.json()['top_k_documents'] for chunk in _['chunks']])

            # delete duplicate chunks

            super_chunk_list_no_dups = []
            for item in super_chunk_list:
                # Calculate number of current ids in list 
                current_ids = [item['file_id'] for item in super_chunk_list_no_dups]

                if item['file_id'] not in current_ids:
                    super_chunk_list_no_dups.append(item)
                else:
                    pass

            # Select fields to retrieve from lucario
            # TODO: Retrieve here metadata


            # Save only the fields we want
            json_out = [
                {
                    'reference_id': item['parent_file_id'], # Is actully parent_file_id!!
                    'text': item['text'],
                    'chunk_code': item['file_id'], # Chunk
                    'raw_url': item['raw_url']

                } for item in super_chunk_list_no_dups
            ]

            return JSONL(json_out)
        except:
            error_message = traceback.format_exc()
            print(error_message)
            raise Exception(error_message)