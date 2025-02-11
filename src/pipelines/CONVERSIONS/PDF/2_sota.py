from custom_types.SOTA.type import SOTA, VersionedInformation, VersionedText, Sections
import json 
from pydantic import BaseModel, Field
from typing import Union, List, Optional
from openai import OpenAI
import re
import Levenshtein
import os

def deconstruct(text : str):
    x = text.split('\n')
    skipped_words = 0
    res = ''
    titles = {}
    titles_list = []
    for i_line, line in enumerate(x):
        if not line.strip():
            continue
        if len(line.split(' '))> 20 or line.startswith('|'):
            skipped_words += len(line.split(' '))
        else:
            if skipped_words > 0:
                res += f'... {skipped_words} words skipped\n'
                skipped_words = 0
            shown_line = line.replace('#####', '####').replace('####', '###').replace('###', '##').replace('##', '#')
            res += shown_line + '\n'
            titles[len(titles_list)] = i_line
            titles_list.append(shown_line.replace('#', ''))
    return x, titles_list, titles, res
    
def get_node(res, api_key):
    class Subsections(BaseModel):
        subsections_list : str = Field(..., description = "Enumerate subsections.")
        missing_sections : str = Field(..., description = "Analyse whether there seems to be holes in that list of sections. If so, propose fills from the text.")
        sections : List['Node'] = Field(..., description = "The list of subsections, corrected if necessary.")
    
    class Node(BaseModel):
        prefix : Union[str, None] = Field(..., description = "Prefix to the title")
        title : str = Field(..., description = "Section title")
    #    depth : int = Field(..., description = "Depth of parent section, plus 1. Starts at 0")
        contains_subsections : bool = Field(..., description = "Is this is a leaf section, only containing text/ images/ etc., or is it a section containing subsections, subsubsections, or titled paragraphs?")
        subsections : Optional[Subsections] = Field(..., description = "Subsections, present if contains_subsections = true.")
        
    client = OpenAI(api_key=api_key)
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Structure the article using the provided scheme."},
            {"role": "user", "content": res},
            {"role": "user", "content" : "If you make ANY mistake (inventing sections, forgettings sections, or mistaking the tag numbers), this will break my AI pipelines and will lead to catastrophic consequences on my laboratory research and patients."}
        ],
        response_format=Node,
        temperature = 0.5,
    )
    
    event = completion.choices[0].message.parsed
    return event

def clean_text(text):
    # Remove special characters and numbers
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    cleaned_text = cleaned_text.lower().strip()
    return cleaned_text

def process_node(node, all_nodes = {}, i = 0):
    all_nodes[i] = node
    i += 1
    if node.contains_subsections and node.subsections:
        for subnode in node.subsections.sections:
            all_nodes, i = process_node(subnode, all_nodes, i)
    return all_nodes, i

def get_range(i_node, titles_list, matches):
    minimum, maximum = 0, len(titles_list)
    for _i_node, _i_title in matches.items():
        if _i_node < i_node:
            minimum = max(minimum, _i_title+1)
        else:
            maximum = min(maximum, _i_title)
    return minimum, maximum
    
def find_match(all_nodes, matches, right_titles_simple, titles_list, titles_list_simple):
    to_process_nodes = [i for i in all_nodes.keys() if i not in matches]
    to_process_nodes.sort(key = lambda x:-len(all_nodes[x].title))
    for i_node in to_process_nodes:
        n = all_nodes[i_node]
        right_title = right_titles_simple[i_node]
        minimum, maximum = get_range(i_node, titles_list, matches)
        left_list = titles_list_simple[minimum:maximum]
        if left_list.count(right_title) == 1:
            matches[i_node] = minimum + left_list.index(right_title)
    return False
    
def find_closest_matches(all_nodes, matches, right_titles_simple, titles_list, titles_list_simple):
    to_process_nodes = [i for i in all_nodes.keys() if i not in matches]
    to_process_nodes.sort(key = lambda x:-len(all_nodes[x].title))
    
    for i_node in to_process_nodes:
        right_title = right_titles_simple[i_node]
        minimum, maximum = get_range(i_node, titles_list, matches)
        left_list = titles_list_simple[minimum:maximum]
        closest_match = None
        closest_distance = float('inf')
        closest_index = None
        
        for i, left_title in enumerate(left_list):
            distance = Levenshtein.distance(right_title, left_title)
            if distance < closest_distance:
                closest_distance = distance
                closest_match = left_title
                closest_index = i
        
        # Assign the closest match if one was found
        if closest_match is not None:
            matches[i_node] = minimum + closest_index

def build_starts(node, matches, titles, starts = [], i = -1):
    i += 1
    my_title_id = matches[i]
    starts.append(titles[my_title_id])
    if node.contains_subsections and node.subsections:
        for subnode in node.subsections.sections:
            i, starts = build_starts(subnode, matches, titles, starts, i)
    return i, starts

def gather_text(x, i, j):
    return '\n'.join(x[i:j]).strip()

def build_sota(x, matches, sota, starts, node, i = -1, start = 0, end = None, use_information_id = None, base_reference = ''):
    if end is None:
        end = len(x)
    i += 1
    my_title_id = matches[i]
    my_start = starts[i]
    next_start = starts[i+1] if i<len(starts)-1 else len(starts)
    if node.contains_subsections:
        children = []
        if next_start > my_start + 1:
            _text = gather_text(x, my_start+1, next_start)
            if _text:
                versioned_info = VersionedInformation.create_text(contents = _text, reference_as = f'{base_reference}0.')
                __information_id = SOTA.get_new_id(sota.information)
                sota.information[__information_id] = versioned_info
                children.append((True, __information_id))
        enumeration = 1
        for subnode in node.subsections.sections:
            i, _information_id = build_sota(x, matches, sota, starts, subnode, i,base_reference = f'{base_reference}{enumeration}.')
            enumeration += 1
            children.append((True, _information_id))
        versioned_info = VersionedInformation.create_text(contents = Sections(enumeration='Numbers enumeration', sections = children), title = node.title, reference_as = base_reference)
    else:
        versioned_info = VersionedInformation.create_text(contents = gather_text(x, my_start+1, next_start), title = node.title, reference_as = base_reference)
    information_id = use_information_id if use_information_id is not None else SOTA.get_new_id(sota.information)
    sota.information[information_id] = versioned_info
    return i, information_id


class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self):
        pass
    def __call__(self, text : str) -> SOTA:
        api_key = os.environ.get("openai_api_key")
        x, titles_list, titles , res = deconstruct(text)
        root = get_node(res, api_key)
        all_nodes, _ = process_node(root)
        right_titles = [n.title for n in all_nodes.values()]
        right_titles_simple = [clean_text(_) for _ in right_titles]
        titles_list_simple = [clean_text(_) for _ in titles_list]
        matches = {}
        for _ in range(3):
            find_match(all_nodes, matches, right_titles_simple, titles_list, titles_list_simple)
        find_closest_matches(all_nodes, matches, right_titles_simple, titles_list, titles_list_simple)
        sota = SOTA.get_empty()
        _, starts = build_starts(root, matches, titles)
        _, main_id = build_sota(x, matches, sota, starts, root, use_information_id = 1)
        sota.title = VersionedText(versions={-1:root.title})
        return sota