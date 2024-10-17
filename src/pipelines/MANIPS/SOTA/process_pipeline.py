
from custom_types.SOTA.type import SOTA, pipelines, get_topk
from custom_types.GRID.type import GRID
from typing import List, Dict, Literal, Union, Optional
from openai import OpenAI
from pydantic import BaseModel, Field
from custom_types.JSONL.type import JSONL
from pipelines.LLMS_v2.grid_instance_output import Pipeline as GridInstanceOutput
from pipelines.LLMS_v2.grid_notation_output import Pipeline as GridNotationOutput
from pipelines.LLMS_v2.str_output import Pipeline as LLMStrOutput
from custom_types.PROMPT.type import PROMPT
import os, requests
from datetime import datetime 
from enum import Enum
import numpy as np
import re

def Attendu(
    api_key : str, 
    model : str, 
    sota : SOTA,
    information_id : int,
    ) -> JSONL:
    versions_list = sota.versions_list(-1)
    information = sota.information[information_id]
    prompt = information.text_representation(
                information_id, 
                sota, 
                versions_list, 
                include_title=True,
                include_abstract=True,
                include_annotations=True,
                include_content=True,
                include_parent_context=True,
                include_referencements=10
            )

    class TextAttendus(BaseModel):
        section_purpose: str = Field(..., description=f"The general purposes, objectives of this section.")
        section_category : Literal['descriptive', 'analytical', 'argumentative', 'dialectic', 'expository', 'narrative', 'comparative', 'cause and effect', 'problem and solution', 'process', 'definitions', 'evaluation', 'critical review', 'theorical framework', 'methodology', 'inductive reasoning', 'deductive reasoning', 'hypothetical', 'synthesis', 'summary', 'interpretative'] = Field(..., description=f"The category of the section.")
        substance_expectations: List[str] = Field(..., description=f"List of the expected content of the section.")
        form_expectations: List[str] = Field(..., description=f"List of the expected form of the section.")
        context_guidelines: str = Field(..., description=f"Give very specific and detailed guidelines relative to the context of the section to maximize continuity and coherence, and minimize redundancy.")
        def __str__(self):
            return '🎯 Objective: '+ self.section_purpose + '\n⚗️ Structure: ' + self.section_category + '\n📝 Substance:\n\t-' + '\n\t-'.join(self.substance_expectations) + '\n🖌️ Form:\n\t-' + '\n\t-'.join(self.form_expectations) + '\n' + self.context_guidelines 
    
    class ImageAttendus(BaseModel):
        image_purpose: str = Field(..., description=f"The general purpose, message we want to convey with this image.")
        image_category : Literal['graph', 'chart', 'diagram', 'image', 'other'] = Field(..., description=f"The category of the image.")
        method_to_create: str = Field(..., description=f"Describe the methodology to create the image.")
        image_source: str = Field(..., description=f"Describe the source of the image: simulation? data? bibliography?")
        def __str__(self):
            return '🎯 Objective: '+ self.image_purpose + '\n📊 Category: ' + self.image_category + '\n🔧 Methodology: ' + self.method_to_create + '\n📌 Source: ' + self.image_source
    
    class SectionAttendus(BaseModel):
        section_purpose: str = Field(..., description=f"The general purposes, objectives of this section.")
        section_category : Literal['chronological', 'spatial', 'thematic', 'topical', 'dialectical', 'causes and effects', 'problems and solutions', 'general to specific', 'specific to general', 'classification', 'questions and ansers', 'methodological', 'examples', 'definitions'] = Field(..., description=f"The category of the section.")
        substance_expectations: List[str] = Field(..., description=f"List of the expected content of the section.")
        subsections_proposition : List[str] = Field(..., description=f"List of proposed subsections.")
        context_guidelines: str = Field(..., description=f"Give very specific and detailed guidelines relative to the context of the section to maximize continuity and coherence, and minimize redundancy.")
        def __str__(self):
            return '🎯 Objective: '+ self.section_purpose + '\n🔍 Category: ' + self.section_category + '\n📝 Substance:\n\t-' + '\n\t-'.join(self.substance_expectations) + '\n📚 Subsections:\n\t-' + '\n\t-'.join(self.subsections_proposition) + '\n' + self.context_guidelines
    
    class TableAttendus(BaseModel):
        table_purpose: str = Field(..., description="The general purpose, message we want to convey with this table.")
        table_category: Literal['statistical', 'comparative', 'correlation', 'frequency', 'cross-tabulation', 'descriptive', 'inferential', 'data summary', 'other'] = Field(..., description="The category of the table.")
        variables_included: List[str] = Field(..., description="List of variables included in the table.")
        data_source: str = Field(..., description="Describe the source of data for the table: data? bibliography? simulations?")
        method_to_create: str = Field(..., description="Describe the methodology to create the table.")
        formatting_guidelines: List[str] = Field(..., description="List of expected formatting guidelines for the table.")
        
        def __str__(self):
            return (
                '🎯 Objective: ' + self.table_purpose +
                '\n📋 Category: ' + self.table_category +
                '\n🔢 Variables Included:\n\t- ' + '\n\t- '.join(self.variables_included) +
                '\n📌 Data Source: ' + self.data_source +
                '\n🔧 Methodology: ' + self.method_to_create +
                '\n🖌️ Formatting Guidelines:\n\t- ' + '\n\t- '.join(self.formatting_guidelines)
            )
    
    class_name = information.get_class_name(information.get_last_version(versions_list))
    if class_name == 'Sections':
        DynamicAttendus = SectionAttendus
    elif class_name == 'Image':
        DynamicAttendus = ImageAttendus
    elif class_name == 'Table':
        DynamicAttendus = TableAttendus
    else:
        DynamicAttendus = TextAttendus
        
    client = OpenAI(api_key = api_key)
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "Please rewrite this section's attendus (not contents!), describing precisely what is expected in terms of substance and form. Follow guidelines if any."},
            {"role": "user", "content": prompt},
        ],
        response_format=DynamicAttendus,
    )
    thoughts = completion.choices[0].message.parsed
    return JSONL(lines=[{'contents': str(thoughts), 'change': 'abstract', 'information_id': information_id}])


def replace_nested_lists(text):
    # Regex pattern to match lists like [[1], [2], ..., [n]]
    pattern = r"\[\[([0-9]+(?:\],\s*\[[0-9]+)*)\]\]"
    
    # Function to transform the matched pattern
    def replacer(match):
        # Split the inner integers and wrap them in new [[some int]] format
        inner_list = match.group(1)
        parts = inner_list.split('], [')
        return ', '.join(f'[[{part}]]' for part in parts)
    
    # Perform the substitution using the replacer function
    result = re.sub(pattern, replacer, text)
    return result

def Write(
    api_key : str, 
    model : str, 
    sota : SOTA,
    information_id : int,
    ) -> JSONL:
    versions_list = sota.versions_list(-1)
    information = sota.information[information_id]
    prompt = information.text_representation(
        information_id, 
        sota, 
        versions_list, 
        include_title=True,
        include_abstract=True,
        include_annotations=True,
        include_content=True,
        include_parent_context=True,
        include_referencements=20
    )
    client = OpenAI(api_key = api_key)
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "user", "content": "Please (re)-write this section. You may ONLY use the information provided above, nothing else. Use markdown to format your text. You may include paragraphs (####) but not sections (# ## and ###). Do not re-state the title, abstract, or annotations: pure content."},
            {"role": "user", "content": prompt},
        ]
    )
    message = completion.choices[0].message.content
    message = replace_nested_lists(message)
    return JSONL(lines=[{'contents': message, 'change': 'content-str', 'information_id': information_id}])

def FindReferencesInLucario(
    api_key : str, 
    model : str, 
    cheap_model : str,
    sota : SOTA,
    information_id : int,
    iterate_only : bool = False
    ) -> JSONL:
    uuid_to_information_id_dic = {}
    versions_list = sota.versions_list(-1)
    for _information_id, information in sota.information.items():
        last_version = information.get_last_version(versions_list)
        if information.get_class_name(last_version) != 'External' or last_version.external_db != 'file':
            continue
        uuid_to_information_id_dic[last_version.external_id] = _information_id
    
    information = sota.information[information_id]
    query = information.text_representation(
        information_id,
        sota,
        versions_list,
        include_title=True,
        include_abstract=True,
        include_content=True,
        mode = 'reference'
    )
    file_uuids = []
    if iterate_only:
        references = sota.get_last(information.referencement_versions, versions_list)
        references = references if references else []
        references = [information.referencements[_] for _ in references]
        for ref in references:
            info = sota.information[ref.information_id]
            info_last = info.get_last_version(versions_list)
            if info.get_class_name(info_last) == 'External' and info_last.external_db == 'file':
                file_uuids.append(info_last.external_id)
    top_k = get_topk(
        project_id = sota.file_id,
        query_text = query,
        k = 10,
        drop_url = sota.drop_url,
        file_uuids = file_uuids,
        max_per_information=5
    )
    results = []
    for top_k_document in top_k.top_k_documents:
        if len(top_k_document.chunks) == 0:
            continue
        referenced_information_id = uuid_to_information_id_dic[top_k_document.main_document.file_uuid]
        reference_id = information.retrieve_reference_id(referenced_information_id)
        pertinence = max(0,5*(1+np.mean([_.score for _ in top_k_document.chunks])))
        detail = ','.join([str(_.file_id) for _ in top_k_document.chunks])
        results.append({
            'contents': {
                'referencement_id': reference_id,
                'information_id': referenced_information_id,
                'detail': detail,
                'pertinence': pertinence,
                'analysis': ''
            },
            'change': 'references',
            'information_id': information_id
        })
    return JSONL(lines=results)
   
def AnalyseReference(
    api_key : str, 
    model : str, 
    cheap_model : str,
    sota : SOTA,
    information_id : int,
    referencement_id : int
    ) -> JSONL:
    versions_list = sota.versions_list(-1)
    active_ids = sota.information[sota.mother_id].get_all_children_ids(sota, sota.mother_id, versions_list)
    active_ids[sota.mother_id] = None
    active_ids = list(active_ids.keys())
    title = sota.get_last(sota.information[information_id].title.versions, versions_list)
    abstract = sota.get_last(sota.information[information_id].abstract.versions, versions_list)
    # 1. find candidates
    information = sota.information[information_id]
    reference = information.referencements[referencement_id]
    _prompts = PROMPT()
    
    information_id = reference.information_id
    referenced_information = sota.information[information_id]
    
    r_text = referenced_information.text_representation(
        information_id,
        sota,
        versions_list,
        detail=reference.detail,
        include_title=True,
        include_content=True,
        include_annotations=True
    )
    _prompts.add('Here is a description of the current section we are working on', role = 'system')
    _prompts.add(f'Title: {title}\nAbstract: {abstract}', role = 'user')
    _prompts.add('Please analyse very precisely, with great detail and fine reasoning, what the reference below may bring to the current section of interest. Be both factual (listing facts and figures) and analytical.', role = 'system')
    _prompts.add(r_text, role = 'user')
    _p = LLMStrOutput(model=model)
    analysis = _p(_prompts)
    return JSONL(lines=[{
        'contents': {
            'information_id': reference.information_id,
            'analysis': analysis,
            'detail': reference.detail,
            'pertinence': reference.pertinence,
            'referencement_id': referencement_id
        },
        'change': 'references',
        'information_id': information_id
    }])     

def Sections(
    model : str, 
    sota : SOTA,
    information_id : int,
) -> JSONL:
    versions_list = sota.versions_list(-1)
    information = sota.information[information_id]
    prompt = information.text_representation(
        information_id, 
        sota, 
        versions_list, 
        include_title=True,
        include_abstract=True,
        include_annotations=True,
        include_content=True,
        include_parent_context=True,
        include_referencements=10
    )
    api_key = os.getenv('openai_api_key')
    client = OpenAI(api_key = api_key)
    class SectionsNew(BaseModel):
        class SubSection(BaseModel):
            title: str = Field(..., description="The title of the subsection.")
            attendus: str = Field(..., description="The expected content of the subsection, in terms of substance and form. NOT the content itself.")
            reference_as : str = Field(..., description="A short 3 words max string that will be used to refer to this subsection.")
        analysis : str = Field(..., description="Think, analyse on which structure would be the most relevant for this chapter.")
        sections: List[SubSection] = Field(..., description="List of proposed subsections.")
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "system", "content": "Above is a highly detailed description of the current chapter, with its expected contents, its context (of any), references (if any), and annotations. We now want to divide this chapter in subsections. Propose ths most relevant structure, the most likely to be accepted by highly demanding experts."},
        ],
        response_format=SectionsNew,
    )
    response = completion.choices[0].message.parsed
    return JSONL(lines=[
        {'contents': [
            {'title': _.title, 'abstract': _.attendus, 'reference_as': _.reference_as}
            for _ in response.sections
            ], 
         'change': 'sections', 
         'information_id': information_id}])

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 json_model : str = 'gpt-4o-2024-08-06',
                 redaction_model : str = 'o1-preview',
                 cheap_model : str = 'gpt-4o-mini',
                 ):
        self.json_model = json_model
        self.redaction_model = redaction_model
        self.cheap_model = cheap_model

    def __call__(self, sota : SOTA, task : dict) -> JSONL:
        api_key = os.getenv('openai_api_key')
        information_id, task_name = task['information'], task['task']
        if task_name == 'Attendu':
            return  Attendu(
                api_key = api_key, 
                model = self.json_model, 
                sota = sota,
                information_id = information_id
            )
        elif task_name == 'Write':
            return  Write(
                api_key = api_key, 
                model = self.redaction_model, 
                sota = sota,
                information_id = information_id
            )
        elif task_name == 'Find references':
            return  FindReferencesInLucario(
                api_key = api_key, 
                model = self.json_model, 
                cheap_model = self.cheap_model,
                sota = sota,
                information_id = information_id
            )
        elif task_name == 'Iterate References':
            return  FindReferencesInLucario(
                api_key = api_key, 
                model = self.json_model, 
                cheap_model = self.cheap_model,
                sota = sota,
                information_id = information_id,
                iterate_only = True
            )
        elif task_name == 'Analyse Reference':
            referencement_id = task.get('referencement_id', None)
            return  AnalyseReference(
                api_key = api_key, 
                model = self.json_model, 
                cheap_model = self.cheap_model,
                sota = sota,
                information_id = information_id,
                referencement_id = referencement_id
            )
        elif task_name in {'Rewrite subsections', 'Create subsections'}:
            return Sections(
                model = self.json_model, 
                sota = sota,
                information_id = information_id
            )
        elif task_name == 'Suggest AI pipelines':
            return JSONL(lines=[{'contents': ['Attendu', 'Suggest AI pipelines'], 'change': 'ai-pipelines-to-run', 'information_id': information_id}])
        else:
            print(f"Task {task_name} not found")
            return JSONL(lines=[])