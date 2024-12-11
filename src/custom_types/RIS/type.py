from dataclasses import dataclass
from typing import List
from custom_types.BIB.type import BIB
from datetime import datetime
import json

convs = {
    'A1': 'authors',
    'A2': 'authors',
    'A3': 'authors',
    'A4': 'authors',
    'A5': 'authors',
    'A6': 'editor',
    'AB': 'abstract',
    'AU': 'authors',
    'BT': 'title',
    'DA': 'date',
    'DI': 'doi',
    'DO': 'doi',
    'DOI': 'doi',
    'JF': 'journal',
    'K1': 'keywords',
    'KW': 'keywords',
    'M3': 'type',
    'N2': 'abstract',
    'PB': 'publisher',
    'T1': 'title',
    'T2': 'title',
    'T3': 'title',
    'TI': 'title',
    'U3': 'date',
    'U4': 'date',
    'Y1': 'date',
}
abbreviation_to_category = {
    "ABST": "Journal Article",
    "ADVS": "Audiovisual Material",
    "AGGR": "Aggregated Database",
    "ANCIENT": "Ancient Text",
    "ART": "Artwork",
    "BILL": "Bill (was Bill, Unenacted Bill)",
    "BLOG": "Blog",
    "BOOK": "Book",
    "CASE": "Case",
    "CHAP": "Book Section",
    "CHART": "Chart",
    "CLSWK": "Classical Work",
    "COMP": "Computer Program",
    "CONF": "Conference Proceedings",
    "CPAPER": "Conference Paper",
    "CTLG": "Catalog",
    "DATA": "Dataset (was Data File) AND Computer Program",
    "DBASE": "Online Database",
    "DICT": "Dictionary",
    "EBOOK": "Electronic Book",
    "ECHAP": "Electronic Book Section",
    "EDBOOK": "Edited Book",
    "EJOUR": "Electronic Article",
    "ELEC": "Web Page",
    "ENCYC": "Encyclopedia",
    "EQUA": "Equation",
    "FIGURE": "Figure",
    "GEN": "Generic",
    "GOVDOC": "Government Document",
    "GRNT": "Grant",
    "HEAR": "Hearing",
    "ICOMM": "Personal Communication",
    "INPR": "Journal Article",
    "INTV": "Interview",
    "JFULL": "Journal Article",
    "JOUR": "Journal Article",
    "LEGAL": "Legal Rule",
    "MANSCPT": "Manuscript",
    "MAP": "Map",
    "MGZN": "Magazine Article",
    "MPCT": "Film or Broadcast",
    "MULTI": "Online Multimedia",
    "MUSIC": "Music",
    "NEWS": "Newspaper Article",
    "PAMP": "Pamphlet",
    "PAT": "Patent",
    "PCOMM": "Personal Communication",
    "POD": "Podcast",
    "PRESS": "Press Release",
    "RPRT": "Report",
    "SER": "Serial",
    "SLIDE": "Audiovisual Material",
    "SOUND": "Audiovisual Material",
    "STAND": "Standard",
    "STAT": "Statute",
    "STD": "Generic",
    "THES": "Thesis",
    "UNBILL": "Bill (was Bill, Unenacted Bill)",
    "UNPB": "Unpublished Work",
    "UNPD": "Unpublished Work",
    "VIDEO": "Audiovisual Material",
    "WEB": "Web page"
}

@dataclass
class RisBibs:
    entries : List[BIB]
    
class Converter:
    extension = 'ris'
    @staticmethod
    def to_bytes(ris : RisBibs) -> bytes:
        def to_ris_text(bib : BIB):
            if bib.full_entry_type == 'RIS':
                return bib.full_entry['ris']
            else:
                base = ''
                if bib.title:
                    base += f'\T1  - {bib.title}'
                if bib.abstract:
                    base += f'\nAB  - {bib.abstract}'
                if bib.doi:
                    base += f'DOI  - {bib.doi}'
                if bib.date:
                    base += f'\nDA  - {bib.date}'
                if bib.journal:
                    base += f'\nJF  - {bib.journal}'
                for _ in bib.authors:
                    base += f'\nA1  - {_}'
                for _ in bib.type:
                    base += f'\nM3  - {_}'
                for _ in bib.keywords:
                    base += f'\nKW  - {_}'
                return base
        text = '\n\n'.join(to_ris_text(bib) for bib in ris.entries)
        return bytes(text, 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> RisBibs:
        t = b.decode('utf-8')
        entries = t.split('ER  -')
        bibs = []
        for entry in entries:
            if not entry.strip():
                continue
            lines = entry.split('\n')
            real_lines = []
            for l in lines:
                repl = l.replace(' ', '')
                if (repl[:2].isupper() and repl[2] == '-'):
                    real_lines.append(l)
                elif len(real_lines) > 0:
                    real_lines[-1]+=f'\n{l}'
                else:
                    continue
            dic = {}
            raw = {}
            for l in lines:
                _ = l.split('-')
                k = _[0].strip()
                v = ('-'.join(_[1:])).strip()
                raw[k] = raw.get(k, []) + [v]
                if k in convs:
                    _k = convs[k]
                    dic[_k] = dic.get(_k, []) + [v]
                if k == 'TY':
                    dic['type'] = dic.get('type', []) + [abbreviation_to_category[v]]
            for k in dic.keys():
                dic[k] = list(set(dic[k]))

            longest_string = lambda strings: max(strings, key=len, default='') if strings else ''

            bib = BIB(
                title = longest_string(dic.get('title', [])),
                abstract = longest_string(dic.get('abstract', [])),
                doi = longest_string(dic.get('doi', [])),
                date = longest_string(dic.get('date', [])),
                journal = longest_string(dic.get('journal', [])),
                authors = dic.get('authors', []),
                type = dic.get('type', []),
                keywords = dic.get('keywords', []),
                affiliations = [],
                full_entry_type = 'RIS',
                full_entry = {'ris': entry+'\nER  - '}
            )
            bibs.append(bib)
        return RisBibs(entries=bibs)
            
    @staticmethod
    def str_preview(ris : RisBibs) -> str:
        return ''
    @staticmethod
    def len(ris: RisBibs) -> int:
        return len(ris.entries)


from custom_types.wrapper import TYPE
from custom_types.JSONL.type import JSONL

wraped = TYPE(
    extension='ris',
    _class = RisBibs,
    converter = Converter,
    inputable  = False,
    additional_converters={
        'jsonl':lambda x : JSONL([_.__dict__ for _ in x.entries])
    }
)