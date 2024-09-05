from custom_types.JSONL.type import JSONL
from typing import List
import requests
import json



class Pipeline:

    ''' 
    This pipeline will call the endpoint "download-and-get-s3url" transform the JSONL
    as a python object, then process it using the service, and then it will return
    back a JSONL type
    '''

    def __init__(self, retrieve_pdf : bool = False):
        self.retrieve_pdf = retrieve_pdf



    def __call__(self, jsonl : JSONL) -> JSONL:

        # loads the whole dataset as a python object
        data = [line for line in jsonl.lines]

        # do a post request to the "download-and-get-s3url" endpoint
        url = "http://172.16.100.121:5566/pdfservices/download-and-get-s3url"
        params = {'retrieve_pdf': self.retrieve_pdf}
        response = requests.post(url,params=params,json=data)

        try:
            json_out = response.json()
            return JSONL([_ for _ in json_out])
        except: 
            raise