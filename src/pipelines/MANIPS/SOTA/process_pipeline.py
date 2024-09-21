
from custom_types.SOTA.type import SOTA, pipelines
from typing import List, Dict, Literal
from openai import OpenAI
from pydantic import BaseModel, Field

def Attendu(
    api_key : str, 
    model : str, 
    sota : SOTA,
    information_id : int,
    ) -> dict:
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
    return {'abstract': str(thoughts)}

def Write(
    api_key : str, 
    model : str, 
    sota : SOTA,
    information_id : int,
    ) -> dict:
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
            {"role": "user", "content": "Please (re)-write this section. You may ONLY use the information provided above, nothing else."},
            {"role": "user", "content": prompt},
        ]
    )
    message = completion.choices[0].message.content
    return {'text': message}

class Pipeline:
    def __init__(self, 
                 api_key : str,
                 json_model : str = 'gpt-4o-2024-08-06',
                 redaction_model : str = 'o1-preview',
                 ):
        self.api_key = api_key
        self.json_model = json_model
        self.redaction_model = redaction_model

    def __call__(self, sota : SOTA, task : dict) -> dict:
        information_id, task_name = task['information'], task['task']
        if task_name == 'Attendu':
            return  Attendu(
                api_key = self.api_key, 
                model = self.json_model, 
                sota = sota,
                information_id = information_id
            )
        elif task_name == 'Write':
            return  Attendu(
                api_key = self.api_key, 
                model = self.redaction_model, 
                sota = sota,
                information_id = information_id
            )
        else:
            return  Write(
                api_key = self.api_key, 
                model = self.redaction_model, 
                sota = sota,
                information_id = information_id
            )