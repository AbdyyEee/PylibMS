from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer
from LMS.Common.LMS_Enum import LMS_BinaryTypes

class AttributeStructure:
    """A class that represents the structure of a specifc attribute."""
    def __init__(self):
        self.type: LMS_BinaryTypes = None
        self.offset = 0 
        self.list_index = 0

        self.list_items: list[str] = []

    def read(self, reader: Reader) -> None:
        self.type = LMS_BinaryTypes(reader.read_uint8())
        reader.skip(1)
        self.list_index = reader.read_uint16()
        self.offset = reader.read_uint32()

class TagGroup:
    """A class that represents a tag group."""
    def __init__(self):
        self.name: str = ""
        self.group_index: int | None = None 
        self.tag_count: int = 0 
        self.tag_indexes: list[int] = [] 

        self.tags: list[Tag] = []
    
    def __repr__(self):
        return self.name
    
    def read(self, reader: Reader, version_4=False) -> None:
        # Version 4 MSBTS have a short before the tag count that is the 
        # index of the tag group.
        if version_4:
            self.group_index = reader.read_uint16()

        self.tag_count = reader.read_uint16()
        self.tag_indexes = [reader.read_uint16() for _ in range(self.tag_count)]
        self.name = reader.read_string_nt()

    def write(self, writer: Writer) -> None:
        pass 
    
class Tag:
    """A class that represents a tag."""
    def __init__(self):
        self.name: str = ""
        self.parameter_count = 0 
        self.parameter_indexes: list[int] = []

        self.parameters: list[TagParameter] = []

    def __repr__(self):
        return self.name
    
    def read(self, reader: Reader) -> None:
        self.parameter_count = reader.read_uint16()
        self.parameter_indexes = [reader.read_uint16() for _ in range(self.parameter_count)]
        self.name = reader.read_string_nt()

    def write(self, writer: Writer) -> None:
        pass 

class TagParameter:
    """A class that represents a tag parameter."""
    def __init__(self):
        self.name: str = ""

        self.type: int = 0
        self.list_indexes: list[int] = []
        self.list_items: list[str] = []

    def __repr__(self):
        return self.name
    
    def read(self, reader: Reader) -> None:
        self.type = LMS_BinaryTypes(reader.read_uint8())

        if self.type is not LMS_BinaryTypes.LIST_INDEX:
            self.name = reader.read_string_nt() 
            return 
        
        reader.skip(1)
        list_count = reader.read_uint16()
        self.list_indexes = [reader.read_uint16() for _ in range(list_count)]
        self.name = reader.read_string_nt()

    def write(self, writer: Writer) -> None:
        pass 



    