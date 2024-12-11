from dataclasses import dataclass
from typing import List
from custom_types.BIB.type import BIB
from datetime import datetime
import json

@dataclass
class PUBMED_BIBS:
    entries : List[BIB]
    
class Converter:
    extension = 'pubmed'
    @staticmethod
    def to_bytes(pubmed : PUBMED_BIBS) -> bytes:
        def to_pubmed_text(bib : BIB):
            if bib.full_entry_type == 'PUBMED':
                return '\n'.join(f'{k} - {vv}' for k,v in bib.full_entry.items() for vv in v)
            else:
                base = ''
                convert_date = lambda iso_date: datetime.fromisoformat(iso_date).strftime('%Y %B %d')
                if bib.title:
                    base += f'\nTI - {bib.title}'
                if bib.abstract:
                    base += f'\nAB - {bib.abstract}'
                if bib.doi:
                    base += f'\nLID - {bib.doi} [doi]'
                base += f'\nDP - {convert_date(bib.date)}'
                if bib.journal:
                    base += f'\nJT - {bib.journal}'
                for _ in bib.authors:
                    base += f'\nAU - {_}'
                for _ in bib.affiliations:
                    base += f'\nAD - {_}'
                for _ in bib.type:
                    base += f'\nPT - {_}'
                for _ in bib.keywords:
                    base += f'\nOT - {_}'
                return base
        text = '\n\n'.join(to_pubmed_text(bib) for bib in pubmed.entries)
        return bytes(text, 'utf-8')
        
    @staticmethod
    def from_bytes(b: bytes) -> PUBMED_BIBS:
        x = b.decode('utf-8').replace('\r', '')
        x = x.replace('\n\n', '__BREAK_HERE__').replace('\n      ', '').replace('__BREAK_HERE__', '\n\n')
        y = [[_.split('-') for _ in y.replace('\n ', ' ').split('\n') if '-' in _] for y in x.split('\n\n')]

        def process(entry):
            keys = list(set(_[0].strip() for _ in entry))
            return {k:['-'.join(_[1:]).strip() for _ in entry if _[0].strip() == k] for k in keys}
        lines = [process(_) for _ in y]
        def to_bib(entry):
            def get_date(line):
                if 'DP' in line:
                    ins = line['DP'][0]
                    try:
                        if ins.count(' ')==1:
                            date = datetime.strptime(ins, '%Y %b')
                        elif ins.count(" ") == 2:
                            date = datetime.strptime(ins, '%Y %b %d')
                        elif ins.count(" ") == 0:
                            date = datetime.strptime(ins, '%Y')
                    except:
                        date = datetime.now()
                elif 'PHST' in line:
                    ins = line['PHST'][0]
                    ins = ins[:ins.find('[')].strip()
                    date = datetime.strptime(ins, '%Y/%m/%d %H:%M')
                else:
                    date = datetime.now()
                return date.isoformat()
            return BIB(
                title = entry.get('TI', [''])[0],
                abstract = entry.get('AB', [''])[0],
                doi = ''.join([_.replace(' [doi]', '') for _ in entry.get('LID', []) if '[doi]' in _][:1]),
                date = get_date(entry),
                journal = entry.get('JT', [''])[0],
                authors = entry.get('AU', []),
                type = entry.get('PT', []),
                keywords = entry.get('MH', []) + entry.get('OT', []),
                affiliations = entry.get('AD', []),
                full_entry_type =  'PUBMED',
                full_entry = entry
            )
        entries = [to_bib(l) for l in lines]
        return PUBMED_BIBS(entries=entries)
        
    @staticmethod
    def str_preview(pubmed : PUBMED_BIBS) -> str:
        return '\n\n'.join(json.dumps(_.__dict__, indent = 1) for _ in pubmed.entries[:10])

    @staticmethod
    def len(pubmed : PUBMED_BIBS) -> int:
        return len(pubmed.entries)

from custom_types.wrapper import TYPE
from custom_types.JSONL.type import JSONL
wraped = TYPE(
    extension='pubmed',
    _class = PUBMED_BIBS,
    converter = Converter,
    inputable  = False,
    additional_converters={
        'jsonl':lambda x : JSONL([_.__dict__ for _ in x.entries])
        },
    icon='/icons/pubmed.svg'
)