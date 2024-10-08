from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer


class LMS_Block:
    """A class that represents a block in a LMS file."""

    def __init__(self):
        self.magic: str = None
        self.size: int = 0
        self.data_start: int = 0

    def read_header(self, reader: Reader) -> None:
        """Reads the block header from a stream

        `reader`: A Reader object."""
        self.magic = reader.read_string_len(4)
        self.size = reader.read_uint32()
        reader.skip(8)
        self.data_start = reader.tell()

    def get_item_offsets(self, reader: Reader, item_count: int) -> list[int]:
        """Returns the absolute offsets to items in a block.

        :param `reader`: A Reader object.
        :param `item_count`: Amount of items."""
        return [reader.read_uint32() + self.data_start for _ in range(item_count)]

    def seek_to_end(self, stream: Reader | Writer) -> None:
        """Seeks to the end of a block passed the AB padding

        `stream`: A Writer or Reader object."""
        stream.seek(self.data_start)
        end = self.size + 16 - self.size % 16
        stream.seek(end, 1)

    def write_initial_data(self, writer: Writer, item_count: int | None = None) -> None:
        """Sets and writes the initial data for a block.
        
        :param `writer`: a Writer object.
        :param `magic`: the magic name of the block."""
        writer.write_string(self.magic)
        writer.write_uint32(0)
        writer.write_bytes(b"\x00" * 8)
        self.data_start = writer.tell()

        if item_count:
            writer.write_uint32(item_count)

    def write_end_data(self, writer: Writer):
        """Writes the ab padding, size, and seeks to the end of a block.

        `writer`: A Writer object."""
        offset = writer.tell()

        # 0xAB padding
        remainder = 16 - self.size % 16
        if remainder == 16:
            return 0

        writer.write_bytes(b"\xAB" * remainder)

        # Size
        writer.seek(self.data_start - 12)
        writer.write_uint32(self.size)
        writer.seek(offset)

        if remainder == 0:
            return

        writer.write_bytes(b"\xAB" * remainder)
        self.seek_to_end(writer)#
