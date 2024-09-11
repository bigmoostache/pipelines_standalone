from typing import _GenericAlias, _LiteralGenericAlias
from custom_types.URL.type import wraped as URLWrapped
from custom_types.PDF.type import wraped as PDFWrapped
from custom_types.BIB.type import wraped as BIBWrapped
from custom_types.HTML.type import wraped as HTMLWrapped
from custom_types.PUBMED.type import wraped as PUBMEDWrapped
from custom_types.NBIB.type import wraped as NBIBWrapped
from custom_types.PROMPT.type import wraped as PROMPTWrapped
from custom_types.XLSX.type import wraped as XLSXWrapped
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
from custom_types.SELECT.type import wraped as SELECTWrapped

all_types = [NBIBWrapped, SELECTWrapped, EXTRACTIONWrapped, SOTAWrapped, TINY_BIBWrapped, GRIDWrapped, RAWrapped, PDICTWrapped, RAWrapped, URLWrapped,PDFWrapped,BIBWrapped,HTMLWrapped,PUBMEDWrapped,PROMPTWrapped, XLSXWrapped,JSONWrapped,JSONLWrapped, TXTWrapped, BYTESWrapped, FLOATWrapped, INTWrapped, BOOLWrapped, NEWSLETTERWrapped]
_allowed_inputs = {_.extension : list(set([_.extension] + [__.extension for __ in all_types if _.extension in __.additional_converters])) for _ in all_types}
_ext_to_class = {_.extension:_.customclass for _ in all_types}
_class_to_ext = {v:k for k,v in _ext_to_class.items()}
all_types = {_.extension : _ for _ in all_types}

def get_converter(extension):
    extension = extension.lower().strip()
    return all_types[extension].converter

def get_visualiser(extension):
    extension = extension.lower().strip()
    return all_types[extension].visualiser

def get_secondary_converter(source_ext, destination_ext):
    return all_types[source_ext].additional_converters[destination_ext]

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
