
from typing import Literal, List
import os


from typing import List
import os
#import dotenv



# Hello, this pipeline will used as QA (quality assurance) for the pdf extractor


class Pipeline:

    """
    
    This pipeline will return True if the article was parsed successfully, and False otherwise depending on two cases:

    1. False if the paper has a less than min_chars characters after removing espaces
    2. False if the paper has less than 30 lines
    """

    def __init__(self, min_line_count: int = 30, min_chars : int = 5000):
        
        self.min_line_count = min_line_count
        self.min_chars = min_chars





    # Recieves the txt that comes out of a pdf extractor
    def __call__(self,  articles : List[str]) -> List[str] :

        filtered_articles = [article for article in articles if flag_article(article, min_line_count= self.min_line_count, min_chars=self.min_chars)]

        return filtered_articles
    

def flag_article(article, min_line_count, min_chars):
            
            # Returns true if we want to keep the article

            keep = True

            # if the number of charactes without spaces is less than 5000 the paper is problematic
            article = article.replace(' ', '') # removes all spaces
            length = len(article)
            if length <= min_chars:
                keep = False

            # Checking if the number of line is less than a specified number
            line_count = len(article.splitlines())
            if line_count <= min_line_count:
                keep = False

            return keep
        
