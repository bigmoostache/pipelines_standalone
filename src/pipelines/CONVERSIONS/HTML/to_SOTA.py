from custom_types.PDF.type import PDF, Converter
from pydantic import BaseModel, Field
from typing import Union, List
import bs4
from bs4 import BeautifulSoup
from custom_types.SOTA.type import SOTA, VersionedText, Version, Author, VersionedInformation, Language, VersionedListVersionedText, Converter as SOTAConverter, Sections
from custom_types.LUCARIO.type import LUCARIO
from custom_types.HTML.type import HTML
import datetime, os, json

vt = lambda x: VersionedText(versions={-1: x})

class HTML_H_TREE(BaseModel):
    title: str = Field(..., description="Title of the HTML node")
    contents: Union[str, List["HTML_H_TREE"]] = Field(..., description="Contents of the HTML node")
    def num_chars(self) -> int:
        if isinstance(self.contents, str):
            return len(self.title) + len(self.contents)
        else:
            return sum([c.num_chars() for c in self.contents]) + len(self.title)

def extract_node_sequence(html_body: str) -> List[str]:
    soup = BeautifulSoup(html_body, 'html.parser')
    body_tag = soup.body if soup.body else soup
    nodes = []
    for child in body_tag.children:
        node_str = str(child).strip()
        if node_str:
            nodes.append(node_str)
    return nodes

def process_nodes(input_nodes: List[str]) -> HTML_H_TREE:
    nodes = {0: HTML_H_TREE(title='root', contents=[])}  # root node
    for n in input_nodes:
        tag = BeautifulSoup(n, 'html.parser').contents[0].name
        print(tag, n)
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            depth = int(tag[1])
            if depth in nodes:
                for d in range(depth+1, 7):
                    if d in nodes:
                        nodes.pop(d)
                nodes[depth] = HTML_H_TREE(title=n, contents='')
            assert depth - 1 in nodes, f"Depth {depth-1} not found in nodes"
            if isinstance(nodes[depth-1].contents, str):
                nodes[depth-1].contents = [HTML_H_TREE(title='', contents=nodes[depth-1].contents)]
            nodes[depth] = HTML_H_TREE(title=n, contents='')
            nodes[depth-1].contents.append(nodes[depth])
        else:
            max_depth = max(nodes.keys())
            assert isinstance(nodes[max_depth].contents, str), f"Contents of node {max_depth} is not a string"
            nodes[max_depth].contents += n
    return nodes[0]

def merge_nodes_below_threshold(node: HTML_H_TREE, char_th: int = 3000, depth : int = 0) -> HTML_H_TREE:
    if isinstance(node.contents, str):
        return node
    else:
        for i,n in enumerate(node.contents):
            node.contents[i] = merge_nodes_below_threshold(n, char_th, depth + 1)
    if depth <= 1:
        return node # level 0 and 1 have to remain sections
    if node.num_chars() > char_th:
        return node
    else:
        def merge_subtree(node: HTML_H_TREE) -> HTML_H_TREE:
            if isinstance(node.contents, str):
                return node
            merged_contents = ''
            for child in node.contents:
                merged_contents += merge_subtree(child).title + merge_subtree(child).contents
            return HTML_H_TREE(title=node.title, contents=merged_contents)
        return merge_subtree(node)
    
def transfer(sota, node, information_id: int = None, root: bool = False, hardcoded_prompt: str = ''):
    if root:
        sota.information[sota.mother_id] = VersionedInformation.create_text(node.title, Sections(sections=[]), node.title, node.title)
        assert not isinstance(node.contents, str), "Root node contents should not be a string"
        assert len(node.contents) == 1, "Root node should have only one child"
        node = node.contents[0]
        assert not isinstance(node.contents, str), "Root node child contents should not be a string"
        sota.title = vt(node.title)
        for n in node.contents:
            transfer(sota, n, hardcoded_prompt=hardcoded_prompt)
        return
    information_id = information_id if information_id else sota.mother_id
    information = sota.get_last(sota.information[information_id].versions, sota.versions_list(-1))
    if not isinstance(node.contents, str):
        new_info = VersionedInformation.create_text(node.title, Sections(sections=[]), node.title, node.title)
        new_id = sota.get_new_id(sota.information) if not root else sota.mother_id
        sota.information[new_id] = new_info
        for n in node.contents:
            transfer(sota, n, information_id = new_id, hardcoded_prompt = hardcoded_prompt)
    else:
        # append new sections info
        abstract = f'<p><em>Below is the TEMPLATE for that section. </em></p><hr><p>{node.contents}</p>'
        new_info = VersionedInformation.create_text(node.title, node.contents, node.contents, node.title)
        new_info.ai_pipelines_to_run = [json.dumps({
            'name': 'rewrite', 
            'params': {
                'references_mode': 'allow', 
                'additional_instructions': hardcoded_prompt, 
                'final_comment': False
            }
            })]
        new_id = sota.get_new_id(sota.information)
        sota.information[new_id] = new_info
    information.sections.append(new_id)

class Pipeline:
    def __init__(self, 
                 char_th: int = 5000,
                 hardcoded_prompt: str = 'Please rewrite this section, filling the missing information using the provided context and data. Preserve the structure of the section, your role is to fill the template. Is there is any missing information, please specify it, embedded in the text, in red. If everything is already filled, then your task is trivial: just rewrite everything verbatim. Be AS EXHAUSTIVE AS POSSIBLE., any missing data will be heavily punished.'
                 ):
        self.char_th = char_th
        self.hardcoded_prompt = hardcoded_prompt
    def __call__(self, html: HTML) -> SOTA:
        new_sota = SOTA.get_empty()
        transfer(
            new_sota, 
            merge_nodes_below_threshold(
                process_nodes(extract_node_sequence(html.html)), 
                char_th = self.char_th
                ), 
            root = True,
            hardcoded_prompt = self.hardcoded_prompt
            )
        return new_sota