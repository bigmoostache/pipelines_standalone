import os

class Pipeline:

    def __init__(self, 
                 ):
        pass
        

    def __call__(self, scores : dict, dict : dict) -> dict:
        score = int(scores.get('fit_score', 0)) - int(scores.get('fit_other_score', 100)) + int(scores.get('coverage_score', 0))
        return {**dict, **scores, 'total_score' : score}
        