from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader


class CTI1:
    """A class that represents a CTI1 block in a MSBT file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format#cti1-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.source_files: list[str] = []

    def read(self, reader: Reader) -> None:
        """Reads the CTI1 block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)
        source_count = reader.read_uint32()

        # Read the sources
        for offset in self.block.get_item_offsets(reader, source_count):
            reader.seek(offset)
            source = reader.read_string_nt()
            self.source_files.append(source)
