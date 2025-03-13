from custom_types.SOTA.type import SOTA, VersionedInformation, VersionedText, Sections, Referencement, extract_references
from typing import List
import json
from pipelines.CUSTOM_TYPES.SOTA.call import text_pipelines, sections_pipelines

def add_reference(sota, information, reference_id, chunk_id: int = None):
    versions = sota.versions_list(-1)
    reference_id_to_reference_id = {r.information_id:i for i,r in information.referencements.items()}
    if reference_id not in reference_id_to_reference_id:
        new_local_ref_id = SOTA.get_new_id(information.referencements)
        information.referencements[new_local_ref_id] = Referencement(
            information_id=reference_id,
            detail=str(chunk_id) if chunk_id is not None else '',
            analysis=''
        )
        reference_list = sota.get_last(information.referencement_versions, versions)
        reference_list = reference_list if reference_list else []
        reference_list.append(new_local_ref_id)
        information.referencement_versions[-1] = reference_list
    else:
        reference_list = sota.get_last(information.referencement_versions, versions)
        if reference_id_to_reference_id[reference_id] not in reference_list:
            reference_list.append(reference_id_to_reference_id[reference_id])
            information.referencement_versions[-1] = reference_list
        referencement = information.referencements[reference_id_to_reference_id[reference_id]]
        if str(chunk_id) not in referencement.detail.split(','):
            referencement = information.referencements[reference_id_to_reference_id[reference_id]]
            referencement.detail = str(chunk_id) if not referencement.detail else referencement.detail + f",{chunk_id}"
            information.referencements[reference_id_to_reference_id[reference_id]] = referencement

def update_references(sota, information_id, references_mode):
    if references_mode == 'restrict': # No changing of references
        return
    elif references_mode == 'free': # Reset
        for referencement in sota.information[information_id].referencements.values():
            referencement.detail = ''
        sota.information[information_id].referencement_versions[-1] = []
    text = sota.build_text(-1, information_id, information_id)
    references = extract_references(text)
    for r in references:
        add_reference(sota, sota.information[information_id], r['informationid'], r['position'])

def bibliography(sota, information_id, contents, params):
    info = sota.information[information_id]
    version = sota.versions_list(-1)
    last = info.get_last_version(version)
    assert info.get_class_name(last) == 'Sections', f"Expected last version to be of class Sections, got {info.get_class_name(last)}"
    new_info_id = SOTA.get_new_id(sota.information)
    new_info = VersionedInformation.create_text(title=contents["bibliography_title"], abstract='References', contents=contents['html_bibliography'])
    sota.information[new_info_id] = new_info
    new_list = last.sections.copy()
    new_list.append(new_info_id)
    info.versions[-1] = Sections(sections=new_list)

def text(sota, information_id, contents, params):
    info = sota.information[information_id]
    if params['act_on_title']:
        info.title.versions[-1] = contents['title']
    if params['act_on_expectations']:
        info.abstract.versions[-1] = contents['html_expectations']
    if params['act_on_contents']:
        info.versions[-1] = contents['html_content']
    if params['act_on_comments']:
        new_contents_id = SOTA.get_new_id(info.annotations)
        info.annotations[new_contents_id] = VersionedText(versions={-1: contents['html_a_posteriori_comment']})
        versions = sota.versions_list(-1)
        active_annotations = sota.get_last(info.active_annotations, versions)
        active_annotations = active_annotations if active_annotations else []
        active_annotations.append(new_contents_id)
        info.active_annotations[-1] = active_annotations
    update_references(sota, information_id, params['references_mode'])
    
def sections(sota, information_id, contents, params):
    info = sota.information[information_id]
    version = sota.versions_list(-1)
    last = info.get_last_version(version)
    assert info.get_class_name(last) == 'Sections', f"Expected last version to be of class Sections, got {info.get_class_name(last)}"
    infos_id = []
    for new_section in contents['sections']:
        new_section_id = SOTA.get_new_id(sota.information)
        new_section = VersionedInformation.create_text(title=new_section['title'], abstract=new_section['expectations'], contents=new_section['contents'])
        sota.information[new_section_id] = new_section
        infos_id.append(new_section_id)
    info.versions[-1] = Sections(sections=infos_id)
    for new_section_id in infos_id:
        update_references(sota, new_section_id[1], params['references_mode'])
    
def add_references(sota, information_id, contents, params):
    for reference in contents:
        add_reference(sota, sota.information[reference['information_id']], reference['reference_id'], reference['chunk_id'])

def not_found(sota, information_id, contents, params):
    raise ValueError(f"Action not found: {action}")

def apply_change(sota, change):
    information_id = change['information_id']
    action = change['action']
    contents = change['contents']
    params = change['params']
    {
        'bibliography': bibliography, 
        'text': text, 
        'sections': sections, 
        'add_references': add_references
    }.get(action, not_found)(sota, information_id, contents, params)

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
            sota : SOTA,
            changes: List[dict]
            ) -> SOTA:
        for change in changes:
            apply_change(sota, change)
        return sota