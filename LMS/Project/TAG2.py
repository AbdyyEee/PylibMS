from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer


class TAG2:
    """A class that represents a TAG2 block in a MSBT file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format#tag2-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.tags: list[dict] = []

    def read(self, reader: Reader) -> None:
        """Reads the TAG2 block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)

        tag_count = reader.read_uint16()
        reader.skip(2)
        # Read the tags
        for offset in self.block.get_item_offsets(reader, tag_count):
            tag = {}
            reader.seek(offset)
            tag["parameter_count"] = reader.read_uint16()
            tag["parameter_indexes"] = [
                reader.read_uint16() for _ in range(tag["parameter_count"])
            ]
            tag["name"] = reader.read_string_nt()
            self.tags.append(tag)

        self.block.seek_to_end(reader)
