from custom_types.SOTA.type import SOTA, Converter, VersionedInformation, VersionedText
from custom_types.PLAN.type import Plan, Converter as PlanConverter
from custom_types.LUCARIO.type import LUCARIO, Document
import itertools
import re
import json
import markdown2
from typing import Dict, Tuple
import markdown2

def plan_to_sota(
    plan: Plan,
    drop_url: str = "https://lucario.croquo.com/files",
    pikabu_url: str = "https://pikabu.croquo.com"
) -> SOTA:
    """
    Converts a Plan object into a SOTA document.
    
    The conversion performs the following:
      1. Scans the entire Plan tree and collects all unique Reference objects.
         For each unique reference (by Reference.reference_id) a new VersionedInformation is created.
         Its external_db is set to "file", its external_id to Reference.external_id (or empty string if None)
         and its title and abstract are both set to Reference.citation.
      2. Converts the main Plan sections. For leaf sections the markdown content (either the provided
         text or a concatenation of bullet points) is converted to HTML using markdown2.
         Additionally, the function scans the markdown for reference patterns:
            - simple:  <ref (\d+) />
            - double:  <ref (\d+) : (\d+) />
         For each match the function adds a Referencement entry to the section’s VersionedInformation,
         where the first number (as integer) is used to look up the corresponding reference information id,
         the second (if present) is stored as the detail (otherwise an empty string), analysis is set to "",
         and pertinence to 0.
      3. In the resulting HTML, all <ref …/> patterns are replaced by a tag of the form 
         <reference informationid="i" details="j"/>.
      4. Combines the reference informations and the section informations into a single SOTA.information dictionary,
         and sets the mother_id to be the root section.
      5. Appends all reference information IDs to the SOTA bibliography.
      
    Args:
      plan: The Plan object to convert.
      drop_url: URL for the file drop.
      pikabu_url: URL for the Pikabu service.
      
    Returns:
      A SOTA document with the converted information.
    """
    
    # -------------------------------------------------------------------------
    # 1. Create the reference informations first.
    # -------------------------------------------------------------------------
    plan.lucario.update()
    unique_refs: Dict[int, Document] = plan.lucario.elements
    
    # We will assign new SOTA.information ids sequentially.
    next_id = 1
    # Mapping from the original Reference.reference_id to the new SOTA information id.
    ref_mapping: Dict[int, int] = {}
    ref_info_dict: Dict[int, VersionedInformation] = {}
    
    for ref_id, ref in unique_refs.items():
        # Build an External instance for this reference.
        external_inst = VersionedInformation.External(
            external_db="lucario",
            external_id=ref.file_uuid
        )
        def get_title_and_abstract(doc: Document) -> Tuple[str, str]:
            x = json.loads(doc.description)
            return x.get('reference', x.get('title', doc.file_name)), markdown2.markdown('- ' + '\n- '.join([f'{k}: {v}' for k, v in x.items()]))
        title, abstract = get_title_and_abstract(ref)
        # Create a VersionedInformation for the reference.
        ref_info = VersionedInformation(
            versions={-1: external_inst},
            referencements={},            # no referencements inside a reference information
            referencement_versions={-1: []},
            title=VersionedText(versions={-1: title}),
            abstract=VersionedText(versions={-1: abstract}),
            # use the reference id as the reference_as string
            reference_as=VersionedText(versions={-1: str(ref_id)}),
            annotations={},
            active_annotations={-1: []},
            ai_pipelines_to_run=[],
            embeddings={}
        )
        ref_mapping[ref_id] = next_id
        ref_info_dict[next_id] = ref_info
        next_id += 1
    
    # -------------------------------------------------------------------------
    # 2. Convert the Plan’s main sections.
    # -------------------------------------------------------------------------
    sections_info_dict: Dict[int, VersionedInformation] = {}
    counter = itertools.count(next_id)
    
    def _convert(p: Plan) -> int:
        current_id = next(counter)
        if p.section_type == 'leaf':
            # Use the explicit text if provided; otherwise join bullet points.
            raw_content: str = p.text if p.text is not None else "\n".join(p.contents.leaf_bullet_points)
            
            # Detect reference patterns in the markdown.
            # This pattern matches both:
            #   <ref 123 />          (group1=123, group2=None)
            #   <ref 123 : 456 />      (group1=123, group2=456)
            pattern = r"<ref (\d+)(?: *: *(\d+))? *\/?>"
            referencements = {}
            referencement_keys = []
            ref_id_2_local_id = {}
            for m in re.finditer(pattern, raw_content):
                ref_id_str = m.group(1)
                detail = m.group(2) if m.group(2) is not None else ""
                ref_id = int(ref_id_str)
                # Only add the referencement if the reference was created.
                if ref_id in ref_mapping and ref_id not in ref_id_2_local_id:
                    new_key = len(referencements) + 1
                    referencements[new_key] = VersionedInformation.Referencement(
                        information_id=ref_mapping[ref_id],
                        detail=detail,
                        analysis="",
                        pertinence=0.0
                    )
                    referencement_keys.append(new_key)
                    ref_id_2_local_id[ref_id] = new_key
                elif ref_id in ref_mapping and ref_id in ref_id_2_local_id:
                    # In that case, append ', {detail}' to the detail.
                    referencements[ref_id_2_local_id[ref_id]].detail += f', {detail}'
            
            # Convert the markdown to HTML.
            html_content = markdown2.markdown(raw_content)
            
            # Replace <ref i/> and <ref i:j/> in the HTML with
            # <reference informationid="i" details="j"/>.
            def ref_repl(match):
                info_id = match.group(1)
                detail = match.group(2) if match.group(2) else ""
                return f'<reference informationid="{info_id}" position="{detail}"/>'
            
            html_content = re.sub(r"<ref (\d+)(?: *: *(\d+))? *\/?>", ref_repl, html_content)
            
            info = VersionedInformation(
                versions={-1: html_content},  # content stored as HTML
                referencements=referencements,
                referencement_versions={-1: referencement_keys},
                title=VersionedText(versions={-1: p.title}),
                abstract=VersionedText(versions={-1: p.abstract}),
                reference_as=VersionedText(versions={-1: p.title}),
                annotations={},
                active_annotations={-1: []},
                ai_pipelines_to_run=[],
                embeddings={}
            )
        else:
            # For node and root sections, process all subsections recursively.
            child_ids = []
            for child in p.contents.subsections:
                child_id = _convert(child)
                child_ids.append(child_id)
            sections_instance = VersionedInformation.Sections(
                enumeration="Numbers enumeration",
                sections=[(True, cid) for cid in child_ids]
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
                ai_pipelines_to_run=[],
                embeddings={}
            )
        sections_info_dict[current_id] = info
        return current_id

    root_section_id = _convert(plan)
    
    # -------------------------------------------------------------------------
    # 3. Combine reference informations and section informations, and create SOTA.
    # -------------------------------------------------------------------------
    combined_info: Dict[int, VersionedInformation] = {}
    combined_info.update(ref_info_dict)
    combined_info.update(sections_info_dict)
    
    sota = SOTA.get_empty()
    sota.drop_url = drop_url
    sota.pikabu_url = pikabu_url
    sota.information = combined_info
    sota.mother_id = root_section_id
    sota.title = VersionedText(versions={-1: plan.title})
    
    # -------------------------------------------------------------------------
    # 4. Append the references to the SOTA bibliography.
    # -------------------------------------------------------------------------
    # Here we assume sota.bibliography is a dict mapping version_id to list of information_ids.
    # We use sota.current_version_id as the key for the current version.
    ref_ids = list(ref_info_dict.keys())
    if sota.current_version_id in sota.bibliography:
        sota.bibliography[sota.current_version_id].extend(ref_ids)
    else:
        sota.bibliography[sota.current_version_id] = ref_ids
    
    return sota

class Pipeline:
    def __init__(self,
                 ):
        pass    
    def __call__(self, 
            p : Plan
            ) -> SOTA:
        return plan_to_sota(p)