from custom_types.SOTA.type import SOTA, Converter, VersionedInformation, VersionedText, Sections, Referencement, LucarioElement
from custom_types.PLAN.type import Plan, Converter as PlanConverter
from custom_types.LUCARIO.type import LUCARIO, Document, FileTypes
import itertools
import re
import json
import mistune
from random import randint
from typing import Dict, Tuple

def plan_to_sota(
    plan: Plan
    ) -> SOTA:
    # -------------------------------------------------------------------------
    # 1. Create the reference informations first.
    # -------------------------------------------------------------------------
    sota = SOTA.get_empty(plan.lucario)
    sota.title = VersionedText(versions={-1: plan.title})
    lucario, ref_mapping = sota.update_lucario()
    # -------------------------------------------------------------------------
    # 2. Convert the Plan’s main sections.
    # -------------------------------------------------------------------------
    sections_info_dict: Dict[int, VersionedInformation] = {}
    
    def _convert(p: Plan) -> int:
        if p.section_type == 'leaf':
            raw_content: str = p.text if p.text is not None else "\n".join(p.contents.leaf_bullet_points)
            
            # Detect reference patterns in the markdown.
            # This pattern matches both:
            #   <ref 123 />          (group1=123, group2=None)
            #   <ref 123 : 456 />      (group1=123, group2=456)
            pattern = r"<ref (\d+)(?: *: *(\d+))? *\/?>"

            referencements_map = {} # tuple -> reference_id
            referencements = {}
            
            for m in re.finditer(pattern, raw_content):
                #print the match
                print(m)
                local_id = int(m.group(1))
                chunk_id = m.group(2) if m.group(2) is not None else ""
                # Only add the referencement if the reference was created.
                refdoc = lucario.fetch_single(local_id, int(chunk_id) if chunk_id != "" else None)
                information = sota.find_or_create_lucario_element(LucarioElement(lucario_id = sota.main_lucario_id, local_document_identifier = local_id))
                information = sota.information[information]
                title = sota.get_last(information.title.versions, [-1])
                
                if refdoc.file_ext in {FileTypes.jpg, FileTypes.png, FileTypes.jpeg, FileTypes.webp}:
                    analysis = f'<p>Image reference</p><p><img src="{refdoc.raw_url}" alt="{refdoc.file_name}" /></p>'
                elif refdoc.file_ext in {FileTypes.image_desc, FileTypes.text_chunk, FileTypes.csv_desc}:
                    analysis = mistune.html(refdoc.text)
                    analysis = f'<p><a href="{refdoc.raw_url}">[source]</a></p>' + analysis
                else:
                    analysis = f'<p>{refdoc.file_ext.value} file</p><p><a href="{refdoc.raw_url}">[source]</a></p>'
                analysis = f'<p>Raw text used, from <strong>{title}</strong></p><blockquote>{analysis}<p></p></blockquote>'
                if (local_id, chunk_id) not in referencements_map:
                    new_key = None
                    while (new_key is None or new_key in referencements):
                        new_key = randint(1000, 9999)
                    print(new_key)
                    referencements[new_key] = Referencement(
                        information_id=ref_mapping[local_id],
                        detail=chunk_id,
                        analysis=analysis
                    )
                    referencements_map[(local_id, chunk_id)] = new_key
            # Convert the markdown to HTML.
            
            html_content = raw_content
            
            # Replace <ref i/> and <ref i:j/> in the HTML with
            # <reference refid="refid"></reference>.
            def ref_repl(match):
                local_id = int(match.group(1))
                chunk_id = match.group(2) if match.group(2) is not None else ""
                refid = referencements_map[(local_id, chunk_id)]
                return f'REF{refid}'
            
            html_content = re.sub(pattern, ref_repl, html_content)
            html_content = mistune.html(html_content)
            
            # now, replace REF{refid} by <reference refid="refid"></reference>
            for refid, ref in referencements.items():
                html_content = html_content.replace(f'REF{refid}', f'<reference refid="{refid}"></reference>')
            
            info = VersionedInformation(
                versions={-1: html_content},  # content stored as HTML
                referencements=referencements,
                referencement_versions={-1: list(referencements.keys())},
                title=VersionedText(versions={-1: p.title}),
                abstract=VersionedText(versions={-1: p.abstract}),
                reference_as=VersionedText(versions={-1: p.title}),
                annotations={},
                active_annotations={-1: []},
                ai_pipelines_to_run=[]
            )
            current_id = SOTA.get_new_id(sota.information)
            sota.information[current_id] = info
        else:
            # For node and root sections, process all subsections recursively.
            child_ids = []
            for child in p.contents.subsections:
                child_id = _convert(child)
                child_ids.append(child_id)
            sections_instance = Sections(
                sections=[cid for cid in child_ids]
            )
            info = VersionedInformation(
                versions={-1: sections_instance},
                referencements={},
                referencement_versions={-1: []},
                title=VersionedText(versions={-1: p.title}),
                abstract=VersionedText(versions={-1: p.abstract}),
                reference_as=VersionedText(versions={-1: p.title}),
                annotations={},
                active_annotations={-1: []},
                ai_pipelines_to_run=[]
            )
            current_id = SOTA.get_new_id(sota.information)
            sota.information[current_id] = info
        return current_id

    root_section_id = _convert(plan)
    
    # -------------------------------------------------------------------------
    # 3. Combine reference informations and section informations, and create SOTA.
    # -------------------------------------------------------------------------
    del sota.information[sota.mother_id] # remove the placeholder
    sota.mother_id = root_section_id
    return sota

class Pipeline:
    def __init__(self,
                 ):
        pass    
    def __call__(self, 
            p : Plan
            ) -> SOTA:
        return plan_to_sota(p)