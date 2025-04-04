from custom_types.SOTA.type import SOTA, VersionedInformation, VersionedText, Sections, Referencement, extract_references
from pipelines.CUSTOM_TYPES.SOTA.call import text_pipelines, sections_pipelines
from typing import List
import json
import logging
from bs4 import BeautifulSoup, NavigableString
import re

def remove_first_heading(html_string):
  if not html_string or not html_string.strip():
      return html_string
  soup = BeautifulSoup(html_string, 'html.parser')
  first_tag = None
  for element in soup.contents:
        # isinstance check is more robust than .find(True) if the root contains multiple items
        if not isinstance(element, NavigableString) and element.name:
            first_tag = element
            break # Found the first tag
  if first_tag and re.match(r'^h[1-6]$', first_tag.name):
        first_tag.decompose()
        return str(soup)
  else:
    return str(soup)

def make_sure_mentions_start_with_arobas(html_string):
    # custom tag <mention>'s contents should always start with @
    soup = BeautifulSoup(html_string, 'html.parser')
    for mention in soup.find_all('mention'):
        if mention.string and not mention.string.startswith('@ '):
            mention.string = '@ ' + mention.string
    return str(soup)

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

def make_sure_ref_exists_in_text(text, refid):
    soup = BeautifulSoup(text, 'html.parser')
    if soup.find('reference', {'refid': str(refid)}) is None:
        new_ref = soup.new_tag('reference', refid=str(refid))
        new_ref.string = f"Reference {refid}"
        soup.append(new_ref)
    return str(soup)
def delete_ref(text, refid):
    soup = BeautifulSoup(text, 'html.parser')
    ref = soup.find('reference', {'refid': str(refid)})
    if ref:
        ref.decompose()
    return str(soup)
def list_refs(text):
    soup = BeautifulSoup(text, 'html.parser')
    refs = soup.find_all('reference')
    return [int(ref['refid']) for ref in refs]

def text(sota, information_id, contents, params):
    info = sota.information[information_id]
    if params['act_on_title']:
        info.title.versions[-1] = contents['title']
    if params['act_on_expectations']:
        info.abstract.versions[-1] = contents['html_expectations']
    if params['act_on_contents']:
        c = contents['html_content']
        c = make_sure_mentions_start_with_arobas(c)
        info.versions[-1] = c
    versions = sota.versions_list(-1)
    last_text = sota.get_last(info.versions, versions)
    if params['act_on_comments']:
        for comment in contents['comments']:
            _id = int(comment['comment_id'])
            c = comment['comment_html']
            c = make_sure_mentions_start_with_arobas(c)
            if _id not in info.annotations:
                info.annotations[_id] = VersionedText(versions={-1: c})
                active_annotations = sota.get_last(info.active_annotations, versions)
                active_annotations = active_annotations if active_annotations else []
                active_annotations.append(_id)
                info.active_annotations[-1] = active_annotations
            else:
                info.annotations[_id].versions[-1] = c
                versions = sota.versions_list(-1)
                active_annotations = sota.get_last(info.active_annotations, versions)
                active_annotations = active_annotations if active_annotations else []
                if _id not in active_annotations:
                    active_annotations.append(_id)
                    info.active_annotations[-1] = active_annotations

    if contents.get('referencements', None) is not None:
        logging.debug(f'Existing referencements: {info.referencements.keys()}')
        for reference in contents['referencements']:
            refid, referenced_information_id, position, html_contents = int(reference['refid']), int(reference['informationid']), reference['position'], reference['html_contents']
            if referenced_information_id not in sota.information:
                logging.debug(f"Information ID {referenced_information_id} not found in SOTA.")
                info.versions[-1] = delete_ref(last_text, refid)
                last_text = info.versions[-1]
                continue
            if refid not in info.referencements:
                logging.debug(f'Adding {reference}')
                sota.information[information_id].referencements[refid] = Referencement(
                    information_id=referenced_information_id,
                    detail=str(position),
                    analysis=html_contents
                )
            info.versions[-1] = make_sure_ref_exists_in_text(last_text, refid)
            last_text = info.versions[-1]
    # Finally, update referencement_versions to match the ones that appear in the text
    refs = list_refs(last_text)
    logging.debug(f'Existing referencements: {info.referencements.keys()}')
    existing_refs = [_ for _ in refs if _ in info.referencements]
    non_existing_refs = [_ for _ in refs if _ not in info.referencements]
    for ref in non_existing_refs:
        last_text = delete_ref(last_text, ref)
        info.versions[-1] = last_text
    for ref in existing_refs:
        last_text = make_sure_ref_exists_in_text(last_text, ref)
        info.versions[-1] = last_text
    sota.information[information_id].referencement_versions[-1] = existing_refs

    
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
    
def not_found(sota, information_id, contents, params):
    raise ValueError(f"Action not found: {action}")

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
            sota : SOTA,
            changes: List[dict]
            ) -> SOTA:
        for change in changes:
            {
                'bibliography': bibliography, 
                'text': text, 
                'sections': sections
            }.get(
                change['action'], not_found
            )(
                sota, 
                change['information_id'], 
                change['contents'], 
                change['params']
            )
        return sota