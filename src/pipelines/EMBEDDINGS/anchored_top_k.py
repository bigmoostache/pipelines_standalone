from typing import List 
import openai, os, numpy as np
from custom_types.JSONL.type import JSONL
import pulp

def solve_affinity_assignment(affinity_matrix, list_of_elements, M, N, P):
    """
    Solve the assignment problem:
    
    - affinity_matrix: 2D list (or NumPy array) of shape [num_elements, m_groups].
    - list_of_elements: 1D list of length num_elements indicating which list each element is in.
    - M: max number of groups each element can be assigned to.
    - N: number of elements each group must receive.
    - P: minimum total assignments required from each list.
    
    Returns:
        A dictionary with:
          - 'status': solver status (str)
          - 'objective_value': maximum total affinity (float)
          - 'assignments': list of (i, j) pairs where x_{i j} = 1
    """
    num_elements = len(affinity_matrix)
    if num_elements == 0:
        return {"status": "NoData", "objective_value": 0, "assignments": []}
    
    m = len(affinity_matrix[0])  # number of groups
    
    # Create PuLP problem
    problem = pulp.LpProblem("AffinityAssignment", pulp.LpMaximize)
    
    # Decision variables: x[i,j] in {0,1}
    x = {}
    for i in range(num_elements):
        for j in range(m):
            x[(i, j)] = pulp.LpVariable(name=f"x_{i}_{j}", cat=pulp.LpBinary)
    
    # Objective: maximize sum of a_{i j} * x_{i j}
    problem += pulp.lpSum(affinity_matrix[i][j] * x[(i, j)]
                          for i in range(num_elements)
                          for j in range(m)), "TotalAffinity"
    
    # 1) Each element i can be assigned to at most M groups
    for i in range(num_elements):
        problem += pulp.lpSum(x[(i, j)] for j in range(m)) <= M, f"ElementMaxGroups_{i}"
    
    # 2) Each group j must have exactly N elements
    for j in range(m):
        problem += pulp.lpSum(x[(i, j)] for i in range(num_elements)) == N, f"GroupSize_{j}"
    
    # 3) Each list k must have at least P assigned elements
    all_lists = set(list_of_elements)
    for k in all_lists:
        indices_in_list_k = [i for i in range(num_elements) if list_of_elements[i] == k]
        problem += pulp.lpSum(x[(i, j)] for i in indices_in_list_k for j in range(m)) >= P, f"ListAtLeastP_{k}"
    
    # Solve
    solver = pulp.PULP_CBC_CMD(msg=0)
    result_status = problem.solve(solver)
    status_str = pulp.LpStatus[result_status]
    
    objective_value = pulp.value(problem.objective)
    chosen_assignments = []
    if status_str in ("Optimal", "Feasible"):
        for i in range(num_elements):
            for j in range(m):
                if pulp.value(x[(i, j)]) == 1:
                    chosen_assignments.append(
                        {
                            'chunk_id' : i,
                            'group_id' : j,
                            'document_id' : list_of_elements[i]
                        }
                    )
    
    return {
        "status": status_str,
        "objective_value": objective_value,
        "assignments": chosen_assignments
    }


class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self,
                embedding_model : str = 'text-embedding-3-large',
                anchor_key : str = 'anchors',
                anchor_expect_lists : bool = True,
                chunk_key : str = 'text',
                chunk_document_id_key : str = 'document_id',
                max_groups_per_element : int = 1,
                elements_per_group : int = 1,
                min_elements_per_list : int = 1,
                assigned_to_key : str = 'assigned_to',
                max_total_assignments : int = 0,
                additional_id_key : str = None, 
                **kwargs : dict
                ):
        self.__dict__.update(locals())
        self.__dict__.pop("self")

    def __call__(self, 
                sections : JSONL,
                chunks : JSONL
                ) -> JSONL:
        _chunks = chunks # Save the original chunks
        # Client and utility functions
        client = openai.OpenAI(api_key=os.environ.get("openai_api_key"))
        def get_embeddings_in_chunks(texts, model, chunk_size=1024):
            embeddings = []
            for i in range(0, len(texts), chunk_size):
                chunk = texts[i:i + chunk_size]
                try:
                    response = client.embeddings.create(input=chunk, model=model).data
                except:
                    response = client.embeddings.create(input=['no data here'] * len(chunk), model=model).data
                embeddings.extend(response)
            return np.array([x.embedding for x in embeddings])
        # Embedding the chunks
        document_indexes = [_[self.chunk_document_id_key] for _ in chunks.lines]
        chunks = [e[self.chunk_key] for e in chunks.lines]
        embeddings = get_embeddings_in_chunks(chunks, self.embedding_model)
        
        # Embedding the sections
        elements = [
            (i, e)
            for i,_ in enumerate(sections.lines)
            for e in _.get(self.anchor_key, [])
        ]
        embeddings_bullet_points = get_embeddings_in_chunks([e[1] for e in elements], self.embedding_model)
        dot_product_matrix = np.dot(embeddings, embeddings_bullet_points.T)
        bullet_points_idx = [_[0] for _ in elements]
        unique_groups = np.unique(bullet_points_idx)
        n_groups = len(unique_groups)
        result_matrix = np.zeros((dot_product_matrix.shape[0], n_groups))

        # Aggregate by taking the mean for each group
        for i, group in enumerate(unique_groups):
            group_mask = (bullet_points_idx == group)  # Mask for columns belonging to the current group
            group_mean = dot_product_matrix[:, group_mask].mean(axis=1)
            result_matrix[:, i] = group_mean

        # Solving the assignment problem
        assignments = solve_affinity_assignment(
            result_matrix, 
            list_of_elements=document_indexes,
            M=self.max_groups_per_element,
            N=self.elements_per_group,
            P=self.min_elements_per_list
        )
        for chunk in _chunks.lines:
            chunk[self.assigned_to_key] = None
        if self.max_total_assignments > 0:
            # only keep the ones with max affinity
            scores = [result_matrix[assignment['chunk_id']][assignment['group_id']] for assignment in assignments['assignments']]
            sorted_indexes = np.argsort(scores)[::-1][:self.max_total_assignments]
            assignments['assignments'] = [assignments['assignments'][i] for i in sorted_indexes]
        
        for assignment in assignments['assignments']:
            chunk_id = assignment['chunk_id']
            group_id = assignment['group_id']
            _chunks.lines[chunk_id][self.assigned_to_key] = group_id
            _chunks.lines[chunk_id][self.assigned_to_key+'_score'] = result_matrix[chunk_id][group_id]
            if self.additional_id_key:
                _chunks.lines[chunk_id][self.additional_id_key] = sections.lines[group_id][self.additional_id_key]
        return _chunks