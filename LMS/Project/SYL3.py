from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader


class SYL3:
    """A class that represents a SYL3 block in a MSBP file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format#syl3-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.styles: list[dict] = []

    def read(self, reader: Reader) -> None:
        """Reads the SYL3 block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)

        style_count = reader.read_uint32()
        # Read the styles
        for _ in range(style_count):
            style = {}
            style["region_width"] = reader.read_uint32()
            style["line_num"] = reader.read_uint32()
            style["font_index"] = reader.read_uint32()
            style["base_color_index"] = reader.read_uint32()

            self.styles.append(style)

        self.block.seek_to_end(reader)
