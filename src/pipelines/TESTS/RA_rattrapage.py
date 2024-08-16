
from custom_types.RA.type import RA
from custom_types.AUTHOR.type import AUTHOR
from custom_types.JSONL.type import JSONL

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



    """

    Welcome to RA request pipeline, please pass the parameters as:

    Example of inputs

        - redirecting: (str parsable as python list): ['crawler-rattrapage', 'search'] -> this will be parsed as /crawler-rattrapage/search


    - Example of request parameters:

        {'start_date': '2024/01/01','end_date': '2024/04/01','max_results': 100,'references': True}

        note: the dict must be in the first line of the JSONL file

    
    - Example of the body of the request (have to be a json file):

    ################################
    {
    "pubmed_queries": [
        "'toll-like receptor 4'[MeSH Terms] AND ('agonist'[tiab] OR 'agonists'[tiab])",
        "'Tuberculosis'[Mesh] OR 'Tuberculosis'[tiab]"
    ],
    "crossref_queries": [
        "tuberculosis",
        "Pyrazinamide"
    ]
    }
    ################################

    """

    # Add necessary env variables
    #__env__ = ["openai_api_key"]

    def __init__(self, 
                 redirecting : str, # List of redirection paths
                 start_date : str = '2024/01/01', 
                 end_date : str = '2024/01/30',
                 max_results : int = 100,
                 #references: bool = True,
                 protocol : Literal["http", "https"] = "https",
                 host_port : str = "tools.blends.fr"
                 #verify: str = False
                 ):
        

        self.request_body = None
        self.start_date = start_date
        self.end_date = end_date
        self.max_results = max_results
        #self.references = references

        # if not verify:
        #     self.verify = []
        # else:
        #     self.verify = [x.strip() for x in verify.split(',')]

        # Assert that the redirecting can be parsed into a list 
        try:
            # Parse the string into a dictionary
            self.redirecting = ast.literal_eval(redirecting)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing request_parameters dictionary string into a python list: {e}")
            raise

        self.host_port = host_port
        self.protocol = protocol



        request_url = f"{self.protocol}://{self.host_port}"
        # Add the redirecting in order
        for i in range(len(self.redirecting)):
                request_url = os.path.join(request_url,self.redirecting[i])
        

        self.request_url = request_url

    def __call__(self, body: str) -> List[RA]:

        # env variables
        #api_key = os.environ.get("openai_api_key")
            

        request_params =   {
                        'start_date': self.start_date,
                        'end_date': self.end_date,
                        'max_results': self.max_results,
                        #'references': self.references
            }

        # Attempt to parse the body as a json

        try : 
            self.request_body = json.loads(body)
        except Exception as e:
            print(f"Error parsing the body of the request a python dictionary: {e}")
            raise

        try:

            response = requests.post(self.request_url, params=request_params, json = self.request_body)

            json_response = response.json()

            # delete
            print(json_response)

            if response.status_code != 200:
                print(response)
                raise Exception('problem with crawler rattrapage')



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
                    abstract= data['abstract'],
                    doi= data['doi'],
                    publication_date= data['publication_date'],
                    journal= data['title'],
                    authors= authors,
                    country= None, # Implement this
                    # we can define a new subtype for the info below here so we can handle the type better
                    data=None,
                    type=None,
                    keywords=None,
                    method=None,
                    full_entry_type=data['source'].upper(), # Literal["CROSSREF", "PUBMED", "OTHER"]
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
            

        except Exception as e:
            
            raise e
        
        #print(json_response)


        # Add a converter JSONL to BIBV2
        # dic = TXT2DICT()(res)
        # for k in self.verify:
        #     assert k in dic
        return ra_list