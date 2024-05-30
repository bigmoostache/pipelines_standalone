import os
from typing import List

class Pipeline:
    def __init__(self, 
                 ):
        pass
        
    def __call__(self, xs : List[dict]) -> str:
        xs.sort(key = lambda x : x.get('index', ''))
        def process(x):
            x.sort(key = lambda x : x.get('index', ''))
            return '\n\n'.join([f"### {i+1}. {y['title']}\nAbstract: {y['abstract']}\nDetails:\n\t-{'_/|_'.join(y['contents'])}" for i,y in enumerate(x)]).replace('_/|_', '\n\t-')
        r = '\n\n'.join([f"## {i+1}. {x['title']}\n{process(x['subsections'])}" for i,x in enumerate(xs)])
        return r