from custom_types.SOTA.type import SOTA, Converter, VersionedInformation, VersionedText, Sections, Referencement
from custom_types.PLAN.type import Plan, Converter as PlanConverter, LucarioElement
from custom_types.LUCARIO.type import LUCARIO, Document
import itertools
import re
import json
import markdown2
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
                local_id = int(m.group(1))
                chunk_id = m.group(2) if m.group(2) is not None else ""
                # Only add the referencement if the reference was created.
                if (local_id, chunk_id) not in referencements_map:
                    new_key = len(referencements) + 1
                    referencements[new_key] = Referencement(
                        information_id=ref_mapping[local_id],
                        detail=chunk_id,
                        analysis="" if m.group(2) is None else lucario.fetch_text(ref_id, int(chunk_id)),
                    )
                    referencements_map[(local_id, chunk_id)] = new_key
                    ref_id_2_local_id[ref_id] = new_key
            
            # Convert the markdown to HTML.
            html_content = markdown2.markdown(raw_content)
            
            # Replace <ref i/> and <ref i:j/> in the HTML with
            # <reference refid="refid"></reference>.
            def ref_repl(match):
                local_id = int(m.group(1))
                chunk_id = m.group(2) if m.group(2) is not None else ""
                refid = referencements_map[(local_id, chunk_id)]
                return f'<reference refid="{refid}"></reference>'
            
            html_content = re.sub(pattern, ref_repl, html_content)
            
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