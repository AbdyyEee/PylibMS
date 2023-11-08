from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader


class ALI2:
    """A class that represents a ALI2 block in a MSBP file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format#ali2-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.attribute_lists: list[list] = []

    def read(self, reader: Reader) -> None:
        """Reads the ALI2 block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)

        list_count = reader.read_uint32()

        # Read the lists
        for list_offset in self.block.get_item_offsets(reader, list_count):
            list_items = []
            reader.seek(list_offset)
            item_count = reader.read_uint32()

            item_offsets = [
                list_offset + reader.read_uint32() for _ in range(item_count)
            ]

            for item_offset in item_offsets:
                reader.seek(item_offset)
                list_items.append(reader.read_string_nt())

            self.attribute_lists.append(list_items)

        self.block.seek_to_end(reader)
