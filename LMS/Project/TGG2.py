from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader


class TGG2:
    """A class that represents a TGG2 block in a MSBT file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format#tgg2-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.groups: list[str] = []

    def read(self, reader: Reader) -> None:
        """Reads the TGG2 block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)

        group_count = reader.read_uint16()
        reader.skip(2)
        # Read the tag groups
        for offset in self.block.get_item_offsets(reader, group_count):
            group = {}
            reader.seek(offset)

            group["tag_count"] = reader.read_uint16()
            group["tag_indexes"] = [
                reader.read_uint16() for _ in range(group["tag_count"])
            ]
            group["name"] = reader.read_string_nt()
            self.groups.append(group)

        self.block.seek_to_end(reader)
