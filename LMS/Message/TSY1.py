from LMS.Common.LMS_Block import LMS_Block
from LMS.Common.LMS_Enum import LMS_BinaryTypes
from LMS.Project.MSBP import MSBP
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer


class TSY1:
    """A class that represents a TSY1 block in a MSBT file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBT-File-Format#tsy1-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.style_indexes: list[int] = []

    def add_style_msbp(self, name: str, msbp: MSBP) -> None:
        """Adds the style index of a style from the msbp given a name.

        :param `name`: The name of the style.
        :param `msbp`: A MSBP object."""
        self.style_indexes.append(msbp.SLB1.get_index_by_label(name))

    def read(self, reader: Reader) -> None:
        """Reads the TSY1 block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)

        # There is no short for the amount of style indexes as its for every message
        # just read until the end is reached so the amount of messages doesnt need to be passed
        while reader.tell() != self.block.data_start + self.block.size:
            self.style_indexes.append(reader.read_uint32())

        self.block.seek_to_end(reader)

    def write(self, writer: Writer) -> None:
        """Writes the TSY1 block to a stream.

        :param `writer`: A Writer object."""
        self.block.magic = "TSY1"
        self.block.size = 0
        self.block.write_header(writer)

        for index in self.style_indexes:
            writer.write_uint32(index)

        self.block.size = 4 * len(self.style_indexes)
        self.block.write_end_data(writer)
