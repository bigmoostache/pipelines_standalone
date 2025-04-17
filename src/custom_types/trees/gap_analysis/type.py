from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple, Optional, Union

class Doc(BaseModel):
    title: str = Field(..., description='The title of the document')
    children: Union[None, List['Doc']] = Field(None, description='List of child documents or sections')
    def get_tasks(self) -> List[List[int]]:
        return [
            [i] + _task 
            for i, child in enumerate(self.children) 
            for _task in child.get_tasks()
            ] if self.children else [[0]]
    def get_task_doc(self, doc = None, task = None):
        return self.get_task_doc(
            doc.children[task[0]], task[1:]
            ) if len(task) != 1 else doc
    def retrieve_things_that_map_to_me(self, doc_A_or_B, parent_titles: str):
        parent_titles.add(self.title)
        return [
            doc_A_or_B.get_task_doc(doc_A_or_B, t)
            for t in doc_A_or_B.get_tasks()
            if len(set(doc_A_or_B.get_task_doc(doc_A_or_B, t).mapping).intersection(parent_titles)) > 0
            ]
    def __str__(self):
        if self.children:
            return f'{self.title}' + ''.join([('\n'+str(c)).replace('\n', '\n\t') for c in self.children])
        else:
            return f'{self.title}'
    def build(self, sections_contents, depth: int = 1, key= []):
        diese_depth = '#' * depth
        if self.children:
            return f'{diese_depth} {self.title}\n\n' \
                + '\n\n'.join([_.build(sections_contents, depth + 1, key + [i]) for i,_ in enumerate(self.children)])
        else:
            return sections_contents[tuple(key + [0])]
    def build_parents(self, parents = set(), task = []):
        parents = set(list(parents))
        parents.add(self.title)
        res = {tuple(task + [0]): parents}
        if self.children:
            for i, c in enumerate(self.children):
                res.update(c.build_parents(parents, task + [i]))
        return res

class DocPlusPagePlusMapping(BaseModel):
    title: str = Field(..., description='The title of the document')
    page_number: int = Field(..., description='The page number of the document or section')
    children: Union[None, List['DocPlusPagePlusMapping']] = Field(None, description='List of child documents or sections')
    mapping: List[str] = Field(..., description='Titles from the denominator document this section maps to. Its elements HAVE to be titles from the denominator document. You may ONLY reference leafs of the denominator document.')
    def get_tasks(self) -> List[List[int]]:
        return [
            [i] + _task 
            for i, child in enumerate(self.children) 
            for _task in child.get_tasks()
            ] if self.children else [[0]]
    def get_task_doc(self, doc = None, task = None):
        return self.get_task_doc(
            doc.children[task[0]], task[1:]
            ) if len(task) != 1 else doc
    def __str__(self):
        if self.children:
            return f'{self.title} (p. {self.page_number})' + ''.join([('\n'+str(c)).replace('\n', '\n\t') for c in self.children])
        else:
            return f'{self.title} (p. {self.page_number})'
    def get_page_of_next(self, task):
        testing = len(task) - 1
        while testing >= 0:
            sub_task = task[:testing] + [0]
            sub_task[testing] = sub_task[testing] + 1
            try:
                return self.get_task_doc(self, sub_task).page_number
            except TypeError:
                testing -= 1
        return self.page_number
        

class ResponseType(BaseModel):
    document_denominator: Doc = Field(..., description='The new document structure')
    document_A: DocPlusPagePlusMapping = Field(..., description='Document A structure with page numbers')
    document_B: DocPlusPagePlusMapping = Field(..., description='Document B structure with page numbers')    
