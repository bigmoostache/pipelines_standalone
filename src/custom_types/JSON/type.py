import json, typing, base64

JSON = dict

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return '___ASCII___' + base64.b64encode(obj).decode('ascii')  # convert bytes to base64 string
        return json.JSONEncoder.default(self, obj)

def bytes_decoder(dct):
    for key, value in dct.items():
        if isinstance(value, str) and value.startswith('___ASCII___'):
            try:
                # Attempt to decode the string as base64; revert if it fails
                value= value[11:]
                possible_bytes = base64.b64decode(value, validate=True)
                dct[key] = possible_bytes
            except (ValueError, base64.binascii.Error):
                continue
    return dct    
    
class Converter:
    @staticmethod
    def to_bytes(dic) -> bytes:
        _json = json.dumps(dic, cls=BytesEncoder)
        return bytes(_json, 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> str:
        loaded_str = b.decode('utf-8')
        return json.loads(loaded_str, object_hook=bytes_decoder)
    @staticmethod
    def str_preview(dic: dict) -> str:
        return json.dumps(dic, cls=BytesEncoder, indent = 1)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='json',
    _class = JSON,
    converter = Converter,
    icon="icons/js.svg"
)