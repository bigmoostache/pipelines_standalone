from typing import _GenericAlias, _LiteralGenericAlias
from custom_types.URL.type import wraped as URLWrapped
from custom_types.URL2.type import wraped as URL2Wrapped
from custom_types.PDF.type import wraped as PDFWrapped
from custom_types.BIB.type import wraped as BIBWrapped
from custom_types.HTML.type import wraped as HTMLWrapped
from custom_types.PUBMED.type import wraped as PUBMEDWrapped
from custom_types.NBIB.type import wraped as NBIBWrapped
from custom_types.PROMPT.type import wraped as PROMPTWrapped
from custom_types.XLSX.type import wraped as XLSXWrapped
from custom_types.CSV.type import wraped as CSVWrapped
from custom_types.JSON.type import wraped as JSONWrapped
from custom_types.JSONL.type import wraped as JSONLWrapped
from custom_types.TXT.type import wraped as TXTWrapped
from custom_types.BYTES.type import wraped as BYTESWrapped
from custom_types.INT.type import wraped as INTWrapped
from custom_types.FLOAT.type import wraped as FLOATWrapped
from custom_types.BOOL.type import wraped as BOOLWrapped
from custom_types.NEWSLETTER.type import wraped as NEWSLETTERWrapped
from custom_types.RA.type import wraped as RAWrapped
from custom_types.PDICT.type import wraped as PDICTWrapped
from custom_types.GRID.type import wraped as GRIDWrapped
from custom_types.TINY_BIB.type import wraped as TINY_BIBWrapped
from custom_types.SOTA.type import wraped as SOTAWrapped
from custom_types.EXTRACTION.type import wraped as EXTRACTIONWrapped
from custom_types.XTRK.type import wraped as XTRKWrapped
from custom_types.SELECT.type import wraped as SELECTWrapped
from custom_types.LUCARIO.type import wraped as LUCARIOWrapped
from custom_types.RIS.type import wraped as RISWrapped
from custom_types.ZIP.type import wraped as ZIPWrapped
from custom_types.PLAN.type import wraped as PLANWrapped
from custom_types.LLM.type import wraped as LLMWrapped
from custom_types.DOCX.type import wraped as DOCXWrapped
from custom_types.NP_ARRAY.type import wraped as NDARRAYWrapped

from custom_types.KONEKT.type import wraped_result as KONEKTWrapped, wraped_generic as KONEKTWrappedGeneric
from custom_types.framework_formats.REPORT.type import wraped as REPORTWrapped

# text formats
from custom_types.text_formats.MD.type import wraped as MDWrapped
from custom_types.text_formats.MDX.type import wraped as MDXWrapped

# framework formats
from custom_types.framework_formats.FACTORY.type import wraped as FACTORYWrapped
from custom_types.framework_formats.TUTORIAL_DEMO.type import wraped as TUTORIAL_DEMOWrapped

all_types = [CSVWrapped, REPORTWrapped, TUTORIAL_DEMOWrapped, FACTORYWrapped, MDWrapped, MDXWrapped, NDARRAYWrapped, DOCXWrapped, LLMWrapped, LUCARIOWrapped, PLANWrapped, ZIPWrapped, RISWrapped, XTRKWrapped, URL2Wrapped, KONEKTWrapped, KONEKTWrappedGeneric, NBIBWrapped, SELECTWrapped, EXTRACTIONWrapped, SOTAWrapped, TINY_BIBWrapped, GRIDWrapped, RAWrapped, PDICTWrapped, RAWrapped, URLWrapped,PDFWrapped,BIBWrapped,HTMLWrapped,PUBMEDWrapped,PROMPTWrapped, XLSXWrapped,JSONWrapped,JSONLWrapped, TXTWrapped, BYTESWrapped, FLOATWrapped, INTWrapped, BOOLWrapped, NEWSLETTERWrapped]
_allowed_inputs = {_.extension : list(set([_.extension] + [__.extension for __ in all_types if _.extension in __.additional_converters])) for _ in all_types}
_ext_to_class = {_.extension:_.customclass for _ in all_types}
_class_to_ext = {v:k for k,v in _ext_to_class.items()}
all_types = {_.extension : _ for _ in all_types}
def build_accepts():
    accepts = {
        type_name: {
            type_name: lambda x: x
        } for type_name in all_types.keys()
    }

    for type_name ,_type in all_types.items():
        for destination_type, _func in _type.additional_converters.items():
            accepts[type_name][destination_type] = _func
            
    def complete_tree():
        found = False
        to_add = []
        for source, destination in accepts.items():
            for destination_type, _func in destination.items():
                for rec_destination, rec_func in accepts[destination_type].items():
                    if rec_destination not in accepts[source]:
                        conversion_func = lambda x: rec_func(_func(x))
                        to_add.append((source, rec_destination, conversion_func))
                        found = True
        for source, destination, _func in to_add:
            accepts[source][destination] = _func
        return found
    found = True
    while found:
        found = complete_tree()
    to_from = {}
    for k,v in accepts.items():
        for kk in v.keys():
            if kk not in to_from:
                to_from[kk] = set([kk])
            to_from[kk].add(k)
    return accepts, to_from

from_to, _allowed_inputs = build_accepts() # build the conversion tree
_allowed_inputs = {k: list(v) for k,v in _allowed_inputs.items()}

def get_converter(extension):
    extension = extension.lower().strip()
    return all_types[extension].converter

def get_visualiser(extension):
    extension = extension.lower().strip()
    return all_types[extension].visualiser

def get_secondary_converter(source_ext, destination_ext):
    return from_to[source_ext][destination_ext]

def CLASS_TO_EXT(X):
    multi = False
    if isinstance(X, _LiteralGenericAlias):
        return ', '.join(X.__args__), "SINGLE"
    elif isinstance(X, _GenericAlias):
        multi = True
        X = X.__args__[0]
    return _class_to_ext[X], "MULTI" if multi else "SINGLE"

def get_feeder(extension):
    return f"_SFP_{extension}"

def auto_convert(source_ext: str, destination_ext: str, data: bytes):
    """
    Automatically convert data from source_ext to destination_ext.
    """
    loader = get_converter(source_ext)
    converter = get_secondary_converter(source_ext, destination_ext)
    return converter(loader.from_bytes(data))