from custom_types.SOTA.type import SOTA, VersionedInformation, VersionedText, Sections, Referencement, extract_references
from pipelines.CUSTOM_TYPES.SOTA.call import text_pipelines, sections_pipelines
from typing import List
import json
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
        for comment in contents['comments']:
            _id = int(comment['comment_id'])
            if _id not in info.annotations:
                info.annotations[_id] = VersionedText(versions={-1: comment['comment_html']})
                versions = sota.versions_list(-1)
                active_annotations = sota.get_last(info.active_annotations, versions)
                active_annotations = active_annotations if active_annotations else []
                active_annotations.append(_id)
                info.active_annotations[-1] = active_annotations
            else:
                info.annotations[_id].versions[-1] = comment['comment_html']
                versions = sota.versions_list(-1)
                active_annotations = sota.get_last(info.active_annotations, versions)
                active_annotations = active_annotations if active_annotations else []
                if _id not in active_annotations:
                    active_annotations.append(_id)
                    info.active_annotations[-1] = active_annotations

    if contents.get('referencements', None) is not None:
        for reference in contents['referencements']:
            refid, informationid, position, html_contents = int(reference['refid']), int(reference['informationid']), reference['position'], reference['html_contents']
            if refid not in info.referencements:
                sota.information[informationid].referencements[refid] = Referencement(
                    information_id=informationid,
                    detail=str(position),
                    analysis=html_contents
                )
            referencement_versions = sota.get_last(sota.information[informationid].referencement_versions, sota.versions_list(-1))
            if refid not in referencement_versions:
                referencement_versions = referencement_versions if referencement_versions else []
                referencement_versions.append(refid)
                sota.information[informationid].referencement_versions[-1] = referencement_versions
    
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