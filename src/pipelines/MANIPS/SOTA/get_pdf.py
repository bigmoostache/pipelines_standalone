from custom_types.SOTA.type import SOTA, pipelines, VersionedInformation
from typing import List 
from custom_types.PDF.type import PDF
import requests

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, sota : SOTA, dico : dict) -> PDF:
        information_id = dico.get('information_id', None)
        assert information_id is not None, "information_id is required"
        assert dico.get('pipeline') == 'pdf'
        info = sota.information.get(information_id, None)
        assert info is not None, "information_id is corrupted: informaiton not found"
        versions_list = sota.versions_list(-1)
        assert info.exists_in_stack(versions_list), "information_id is corrupted: information not in stack"
        last = sota.get_last(info.versions, versions_list)
        assert VersionedInformation.get_class_name(last) == 'External', "information_id is corrupted: information not external"
        assert last.external_db == 'file', "information_id is corrupted: information not file"
        
        url = f'{sota.drop_url}?file={last.external_id}'
        response = requests.get(url)
        response.raise_for_status()
        file_bytes = response.content
        return PDF(file_bytes)
        
        
        
        