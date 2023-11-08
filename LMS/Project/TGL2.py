from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader


class TGL2:
    """A class that represents a TGL2 block in a MSBT file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format#tgl2-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.items: list[str] = []

    def read(self, reader: Reader) -> None:
        """Reads the TGL2 block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)

        item_count = reader.read_uint32()
        # Read the list items
        for offset in self.block.get_item_offsets(reader, item_count):
            reader.seek(offset)
            self.items.append(reader.read_string_nt())

        self.block.seek_to_end(reader)
