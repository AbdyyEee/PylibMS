from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer

from LMS.Common.LMS_Enum import LMS_MessageEncoding

class LMS_Binary:
    """A class that represents common data and functions shared betweeen all LMS files."""

    def __init__(self):
        self.magic: str  = None 
        self.bom: str = None 
        self.encoding: LMS_MessageEncoding = None 
        self.revision: int = None 
        self.block_count: int = None 
        self.file_size: int = None

    def read_header(self, reader: Reader) -> None:
        """Reads the header from the stream.
        
        :param `reader`: A Reader object."""
        self.magic = reader.read_string_len(8)
        self.bom = "little" if reader.read_bytes(2) == b"\xFF\xFE" else "big"
       
        reader.change_byte_order(self.bom)

        # Unk 1
        reader.skip(2)
        self.encoding = LMS_MessageEncoding(reader.read_uint8())
        self.revision = reader.read_uint8()
        self.block_count = reader.read_uint16()
        # Unk 2
        reader.skip(2)
        self.file_size = reader.read_uint32()
        # Skip to end 
        reader.skip(10)
        end = reader.tell()

        # Verify file size alignment 
        reader.seek(0, 2)
        size = reader.tell() 
        if size != self.file_size: 
            raise Exception("The file size is misaligned!")
        reader.seek(end)

    def write_header(self, writer: Writer) -> None:
        """Writes the header from the stream.
        
        :param `writer`: A Writer object."""
        self.bom = writer.byte_order
        writer.write_string(self.magic)
        writer.write_bytes(b"\xFF\xFE" if self.bom ==
                           "little" else b"\xFE\xFF")
        # Unk 1
        writer.write_bytes(b"\x00\x00")
        writer.write_uint8(self.encoding.value)
        writer.write_uint8(self.revision)
        writer.write_uint16(self.block_count)
        # Unk 2
        writer.write_bytes(b"\x00\x00")
        writer.write_uint32(0)
        # Padding
        writer.write_bytes(b"\x00" * 10)

    def write_size(self, writer: Writer):
        """Writes the size of the file to the stream.
        
        :param `writer`: A Writer object."""
        writer.seek(0, 2)
        size = writer.tell()
        writer.seek(18)
        writer.write_uint32(size)

    def search_block_by_name(self, reader: Reader, name: str) -> tuple[bool, int]:
        """Returns the absolute offset of a specific block from a stream and if the offset is valid.
        
        :param `reader`: A Reader object.
        :param `name`: The name of the block."""
        name = name.upper()
        blocks = self.search_all_blocks(reader)
        return (True, blocks[name]) if name in blocks else (False, None)

    def search_all_blocks(self, reader: Reader) -> dict[str:int]:
        """Returns the absolute offset of every block in a stream.
        
        :param `reader`: A Reader object."""
        result = {}
        # First block is always located absolute 32
        reader.seek(32)
        block_count = self.block_count

        for _ in range(block_count):
            offset = reader.tell()
            magic = reader.read_string_len(4)
            size = reader.read_uint32()
            # Skip Padding to seek past block using size
            reader.skip(8)
            reader.seek(size, 1)
            remainder = 16 - size % 16

            if remainder != 16:
                reader.skip(remainder)

            result[magic] = offset

        return result


            
