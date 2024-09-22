
from custom_types.SOTA.type import SOTA, pipelines, VersionedText, VersionedInformation
from custom_types.JSONL.type import JSONL
from typing import List 

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, 
                 sota : SOTA,
                 pipeline_results: JSONL
                 ) -> SOTA:
        for pipeline_result in pipeline_results.lines:
            information_id = pipeline_result['information_id']
            information = sota.information[information_id]
            versions_list = sota.versions_list(-1)
            change = pipeline_result['change']
            if change == 'abstract':
                contents = pipeline_result['contents']
                information.abstract.versions[-1] = contents
            elif change == 'content-str':
                contents = pipeline_result['contents']
                information.versions[-1] = contents
            elif change == 'title':
                contents = pipeline_result['contents']
                information.title.versions[-1] = contents
            elif change == 'reference-as':
                contents = pipeline_result['contents']
                information.reference_as.versions[-1] = contents
            elif change == 'annotation':
                contents = pipeline_result['contents']
                new_id = sota.get_new_id(information.annotations)
                information.annotations[new_id] = VersionedText(versions={-1: contents})
                active_id = sota.get_last(information.active_annotations, versions_list, return_id=True)
                if active_id is None:
                    information.active_annotations[-1] = [new_id]
                elif active_id != -1:
                    information.active_annotations[-1] = information.active_annotations[active_id].copy()
                    information.active_annotations[-1].append(new_id)
                else:
                    information.active_annotations[-1].append(new_id)
            elif change == 'ai-pipelines-to-run':
                contents = pipeline_result['contents']
                information.ai_pipelines_to_run = contents
            elif change == 'references':
                contents = pipeline_result['contents']
                target_information_id = contents['information_id']
                detail = contents['detail']
                pertinence = contents['pertinence']
                analysis = contents['analysis']
                referencement_id = contents['referencement_id']
                if referencement_id is None:
                    referencement_id = sota.get_new_id(information.referencements)
                information.referencements[referencement_id] = VersionedInformation.Referencement(
                    information_id = target_information_id,
                    detail = detail,
                    pertinence = pertinence,
                    analysis = analysis
                )
                last_reference_list = sota.get_last(information.referencement_versions, versions_list, return_id=True)
                if last_reference_list is None:
                    information.referencement_versions[-1] = [referencement_id]
                elif last_reference_list != -1:
                    information.referencement_versions[-1] = information.referencement_versions[last_reference_list].copy()
                    information.referencement_versions[-1].append(referencement_id)
                    information.referencement_versions[-1] = list(set(information.referencement_versions[-1]))
                else:
                    information.referencement_versions[-1].append(referencement_id)
                    information.referencement_versions[-1] = list(set(information.referencement_versions[-1]))
            elif change == 'sections':
                contents = pipeline_result['contents']
                section_ids = []
                for section in contents:
                    old_section_id = section.get('information_id', None)
                    if old_section_id is None:
                        new_section = VersionedInformation.create_text(
                            title = section['title'],
                            abstract = section['abstract'],
                            reference_as= section['reference_as']
                        )
                        new_section_id = sota.get_new_id(information.information)
                    else:
                        new_section = sota.information[old_section_id]
                        new_section_id = old_section_id
                    section_ids.append(new_section_id)
                    information.information[new_section_id] = new_section
                information.versions[-1] = VersionedInformation.Sections(
                    enumeration = "Numbers enumeration",
                    sections = [(True, _) for _ in section_ids]
                )
        return sota