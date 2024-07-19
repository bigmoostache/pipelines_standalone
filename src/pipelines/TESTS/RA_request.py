
from custom_types.RA.type import RA
from custom_types.AUTHOR.type import AUTHOR

from typing import Literal
import os
import requests

from typing import Annotated, List, Optional, Union
#from custom_types.PROMPT.type import PROMPT
#from utils.booleans import to_bool
import json
import ast
import dotenv
dotenv.load_dotenv()

class Pipeline:

    # Add necessary env variables
    #__env__ = ["openai_api_key"]

    def __init__(self, 
                 redirecting : str, # List of redirection paths
                 request_params: str,
                 request_type : Literal["GET", "POST"] = "GET",
                 protocol : Literal["http", "https"] = "http",
                 host : str = "localhost", 
                 port : str = "5566"
                 #verify: str = False
                 ):
        
        # if not verify:
        #     self.verify = []
        # else:
        #     self.verify = [x.strip() for x in verify.split(',')]

        # Assert that the request parameters can be parsed as a dictionary
        try : 
            self.request_params = json.loads(request_params)
        except Exception as e:
            print(f"Error parsing request_parameters dictionary string into a python dictionary: {e}")
            raise

        # Assert that the redirecting can be parsed into a list 
        try:
            # Parse the string into a dictionary
            self.redirecting = ast.literal_eval(redirecting)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing request_parameters dictionary string into a python dictionary: {e}")
            raise

        self.request_type = request_type
        self.host = host
        self.port = port
        self.protocol = protocol



        request_url = f"{self.protocol}://{self.host}:{self.port}"
        # Add the redirecting in order
        for i in range(len(self.redirecting)):
                request_url = os.path.join(request_url,self.redirecting[i])
        

        self.request_url = request_url

    def __call__(self) -> List[RA]:

        # env variables
        #api_key = os.environ.get("openai_api_key")
            

        try:

            if self.request_type =='GET':
                response = requests.get(self.request_url, params=self.request_params)
                json_response = response.json()


                ra_list = []
                for line in json_response:

                    data = line
                    # Convert authors into AUTHOR types:
                    authors = [
                                AUTHOR(
                                        full_name=author,
                                        affiliations=None,
                                        h_index=None
                                    ) for author in data['authors']
                            ] if data.get('authors') is not None else []
                    
                    # Create a RA object
                    ra_instance = RA(
                        title= data['title'],
                        abstract= data['title'],
                        doi= data['title'],
                        publication_date= data['title'],
                        journal= data['title'],
                        authors= authors,
                        country= data['title'],
                        # we can define a new subtype for the info below here so we can handle the type better
                        data=None,
                        type=None,
                        keywords=None,
                        method=None,
                        full_entry_type=None, # Literal["CROSSREF", "PUBMED", "OTHER"]
                        full_entry=None,
                        theme_analyzis=None,
                        topics_analyzis=None,
                        references= data['references'], # liste de doi
                        citations=None, # liste de doi
                        pr = None, # pagerank calculated in a set of articles with references and citations
                        is_new=None, # if an article was in the original set of articles
                        has_pdf=None # if we have downloaded the pdf
                    ) 

                    # Append each ra instance to the list
                    ra_list.append(ra_instance)
                    





            if self.request_type == 'POST':
                raise NotImplementedError("POST request are not implemented yet.")
                response = requests.post(self.request_url, params=self.request_params)
                data = response.json()

        except Exception as e:
            raise e
        
        #print(json_response)


        # Add a converter JSONL to BIBV2
        # dic = TXT2DICT()(res)
        # for k in self.verify:
        #     assert k in dic
        return ra_list