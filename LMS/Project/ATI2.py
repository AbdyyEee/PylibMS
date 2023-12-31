from LMS.Common.LMS_Block import LMS_Block
from LMS.Common.LMS_Enum import LMS_BinaryTypes
from LMS.Stream.Reader import Reader


class ATI2:
    """A class that represents a ATI2 block in a MSBP file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format#ati2-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.attributes: list[dict] = []

    def read(self, reader: Reader) -> None:
        """Reads the ATI2 block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)

        attribute_count = reader.read_uint32()
        # Read the attribute information
        for _ in range(attribute_count):
            attribute = {}
            attribute["type"] = LMS_BinaryTypes(reader.read_uint8())
            reader.skip(1)
            attribute["list_index"] = reader.read_uint16()
            attribute["offset"] = reader.read_uint32()
            self.attributes.append(attribute)

        self.block.seek_to_end(reader)
