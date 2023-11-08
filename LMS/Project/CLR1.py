from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader


class CLR1:
    """A class that represents a CLR1 block in a MSBP file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format#clr1-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.colors: list[dict] = []

    def read(self, reader: Reader) -> None:
        """Reads the CLR1 block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)

        color_count = reader.read_uint32()
        # Read the RGBA colors
        for _ in range(color_count):
            color = {}
            color["r"] = reader.read_uint8()
            color["g"] = reader.read_uint8()
            color["b"] = reader.read_uint8()
            color["a"] = reader.read_uint8()
            self.colors.append(color)

        self.block.seek_to_end(reader)
