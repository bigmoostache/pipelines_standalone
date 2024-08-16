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


    def __call__(self,  article : str) -> bool :

        # Recieves the txt that comes out of a pdf extractor

        keep = True

        # if the number of charactes without spaces is less than 5000 the paper is problematic
        article = article.replace(' ', '') # removes all spaces
        length = len(article)
        if length <= self.min_chars:
            keep = False

        # Checking if the number of line is less than a specified number
        line_count = len(article.splitlines())
        if line_count <= self.min_line_count:
            keep = False


        # Returns a flag indicating whether the pdf was parsed correctly or not
        return keep
    
        