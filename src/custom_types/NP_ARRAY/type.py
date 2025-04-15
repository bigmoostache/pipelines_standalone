import json, typing, base64
import numpy as np
   
class Converter:
    @staticmethod
    def to_bytes(array: np.ndarray) -> bytes:
        # Create metadata dict with shape and dtype info
        metadata = {
            'shape': array.shape,
            'dtype': str(array.dtype)
        }
        
        # Convert metadata to JSON string and then to bytes
        metadata_bytes = json.dumps(metadata).encode('utf-8')
        
        # Get the length of metadata bytes and convert to 4 bytes
        metadata_length = len(metadata_bytes).to_bytes(4, byteorder='little')
        
        # Convert array to bytes
        array_bytes = array.tobytes()
        
        # Combine metadata length + metadata + array bytes
        return metadata_length + metadata_bytes + array_bytes
    
    @staticmethod
    def from_bytes(b: bytes) -> np.ndarray:
        # Get metadata length from first 4 bytes
        metadata_length = int.from_bytes(b[:4], byteorder='little')
        
        # Extract metadata bytes and convert to dict
        metadata_bytes = b[4:4+metadata_length]
        metadata = json.loads(metadata_bytes.decode('utf-8'))
        
        # Extract array bytes
        array_bytes = b[4+metadata_length:]
        
        # Reconstruct array using metadata
        array = np.frombuffer(array_bytes, dtype=np.dtype(metadata['dtype']))
        return array.reshape(metadata['shape'])
    
    @staticmethod
    def len(array : np.ndarray) -> int:
        return len(array)
   
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='ndarray',
    _class = np.ndarray,
    converter = Converter,
    icon="/icons/js.svg"
)