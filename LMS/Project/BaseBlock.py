from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader
from LMS.Project.Structure import TagGroup

class ProjectBlock:
    """A class that represents all blocks in a MSBP file"""

    def __init__(self, item_type):
        self.block: LMS_Block = LMS_Block()
        self.item_type = item_type
        self.data: list[item_type] = []

    def read(self, reader: Reader, contains_offsets: bool = True, uint32_count: bool = True, version_4=False) -> None:
        """Reads the block from a stream.

        :param `reader`: a Reader object.
        :param `uint32_count`: determines weather the item count is a uint32. 
        :param `version_4`: determines if the block should be written for version 4 of a format. This is only used for `TagGroup`."""
        self.block.read_header(reader)

        if uint32_count:
            item_count = reader.read_uint32()
        else:
            item_count = reader.read_uint16()
            reader.skip(2)
        
        if contains_offsets:
            for offset in self.block.get_item_offsets(reader, item_count):
                reader.seek(offset)

                type = self.item_type()

                if isinstance(type, TagGroup):
                    type.read(reader, version_4)
                else:
                    type.read(reader)
                    
                self.data.append(type)
        else:
            for _ in range(item_count):
                type = self.item_type()
                type.read(reader)
                self.data.append(type)

        self.block.seek_to_end(reader)
