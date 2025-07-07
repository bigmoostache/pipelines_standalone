from custom_types.PROMPT.type import PROMPT
from custom_types.LUCARIO.type import LUCARIO

class Pipeline:
    def __init__(self,
                query: str,
                max_groups_per_element : int = 1,
                elements_per_group : int = 30,
                min_elements_per_list : int = 0,
                ):
        self.query = query
        self.max_groups_per_element = max_groups_per_element
        self.elements_per_group = elements_per_group
        self.min_elements_per_list = min_elements_per_list

    def __call__(self, 
                lucario : LUCARIO
                ) -> PROMPT:
        lucario.update()
        res = lucario.anchored_top_k(
            queries = [
                self.query,
            ],
            group_ids = [0],
            max_groups_per_element = self.max_groups_per_element,
            elements_per_group = self.elements_per_group,
            min_elements_per_list = self.min_elements_per_list,
        )
        
        def find(file_id):
            local_id = lucario.file_id_2_position[file_id]
            file= lucario.elements[local_id]
            try:
                x = json.loads(file.description)
                return x['title']
            except:
                return file.file_name
        
        prompt = [f'Chunk ID: {res["file_id"]}\nFrom: {find(res["direct_parent_file_id"])})\n\n{res["text"]}' for res in res]
        prompt = '\n\n=================================\n\n'.join(prompt)
        p = PROMPT()
        p.add(prompt, role='user')
        return p