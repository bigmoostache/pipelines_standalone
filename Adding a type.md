## This is very important. To add a type:

### The python class

In itself, the actual python implementation is not very important. What is important, is that the bytes representation of a type should not change with time.

```python
@dataclass
class BIB:
    title: str
    abstract : str
    doi : str
    date : str
    journal : str
    authors : List[str]
    type : List[str]
    keywords : List[str]
    affiliations : List[str]
    full_entry_type : Literal['PUBMED', 'OTHER']
    full_entry : dict
```
Is an example of a defined class. It should not move too much. In can use subclasses, complex data structures, etc. We don't really care.

### What is a type?

A type is an interface which will make everything work correctly. Everything, in pipelines and articles, has to be correctly typed. If they aren't things will break down. 

A type has to come with two essential features:
1. A converter from `bytes` to a python in-memry class representation
2. The opposite

```python
class Converter:
    @staticmethod
    def to_bytes(url : BIB) -> bytes:
        return bytes(json.dumps(url.__dict__), 'utf-8')
        
    @staticmethod
    def from_bytes(b: bytes) -> BIB:
        loaded_str = b.decode('utf-8')
        return BIB(**json.loads(loaded_str))
```
The `string_preview` is deprecated. Please do not define it for new types.

Other additional features may be added:
3. A visualizer
4. Natural conversions (example: from `BIB` to `dict`, there is a natural conversion)


### Making things work

For the rest of the infrastructure to correctly interface with a type, you need to declare it. The declaration is standardized:

```python
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='bib',
    _class = BIB,
    converter = Converter,
    inputable  = False,
    additional_converters={
        'json':lambda x : x.__dict__
        }
)
```
Everything has to appear in there: the extension the python class, the converter, and the additional converters. The `imputable` field will be deprecated.

The last thing you'll need to do is to add a line in `converter.py`:

```python
# converter.py

# Import the new type
from custom_types.BIB.type import wraped as BIBWrapped
# Add it to the list of declarations
all_types = [..., BIBWrapped]
```


### Facilitating development

I would strongly suggest adding a few examples (`bytes` representation) in an attached `examples` folder. 