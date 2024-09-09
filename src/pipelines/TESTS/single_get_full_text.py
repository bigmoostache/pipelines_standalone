from custom_types.JSON.type import JSON
from typing import List
import requests
import json



class Pipeline:

    ''' 
    This pipeline will call the endpoint "download-and-get-s3url" transform the JSONL
    as a python object, then process it using the service, and then it will return
    back a JSONL type
    '''

    def __init__(self, model : str = 'pymupdf4llm'):
        self.model = model


    def __call__(self, json_in : JSON) -> JSON:

        # loads the whole dataset as a python object
        data = json_in

        # do a post request to the "download-and-get-s3url" endpoint

        # In prod: 
        url = "http://172.16.100.121:5566/pdfservices/single-get-full-text"

        params = {'model': self.model}
        response = requests.post(url,params=params,json=data)

        try:
            json_out = response.json()
            return JSON(json_out)
        except: 
            raise