from custom_types.NEWSLETTER.type import NEWSLETTER, SummaryParagraph, Article, Metric, SummaryEntry
from custom_types.JSONL.type import JSONL
from typing import List
from datetime import datetime

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 summary : List[dict],
                 articles : JSONL,
                 metrics : JSONL,
                 summary_analysis : str
                 ) -> NEWSLETTER:
        return NEWSLETTER(
            summary = [
                SummaryParagraph(**{
                    "title" : _.get("title", ""),
                    "entries" : [SummaryEntry(
                        title = __.get("title", ""),
                        analysis = __.get("analysis", ""),
                        reference_id = __.get("reference_id", "")
                        ) for __ in _.get("entries", [])]
                })
                for _ in summary
            ],
            articles = [
                Article(**{
                    "reference_id" : _.get("reference_id", ""),
                    "title" : _.get("title", ""),
                    "pertinence_score" : _.get("pertinence_score", 0),
                    "analysis" : _.get("analysis", []),
                    "summary" : _.get("summary", ""),
                    "complete_entry" : _.get("text", ""),
                    "tags" : _.get("tags", []),
                    "localization" : _.get("localization", "World"),
                    "source" : _.get("source", ""),
                    "author" : _.get("author", ""),
                    "sentiment" : _.get("sentiment", "neutral"),
                    "url" : _.get("url", "#"),
                    "image" : b''
                })
                for _ in articles.lines
            ],
            metrics = [
                Metric(**{
                    "metric" : _.get("metric", ""),
                    "value" : _.get("value", 0),
                    "unit" : _.get("unit", ""),
                    "previous_value" : _.get("previous_value", 0),
                    "previous_relative_time" : _.get("previous_value_relative_time", ""),
                })
                for _ in metrics.lines
            ],
            timestamp = str(datetime.now()),
            summary_analysis = summary_analysis
        )