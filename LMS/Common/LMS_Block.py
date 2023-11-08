from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer

class LMS_Block:
    """A class that represents a block in a LMS file."""
    def __init__(self):
        self.magic: str = None 
        self.size: int = None 
        self.data_start: int = None 
 
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

    def write_header(self, writer: Writer) -> None:
        """Writes the block to a stream.
        
        `writer`: A Writer object."""
        writer.write_string(self.magic)
        writer.write_uint32(0)
        writer.write_bytes(b"\x00" * 8)
        self.data_start = writer.tell()

    def write_ab_padding(self, writer: Writer) -> None:
        """Writes the ab padding after a block.
        
        `writer`: A Writer object."""
        
        remainder = 16 - self.size % 16
        if remainder == 16:
            return 0
        
        writer.write_bytes(b"\xAB" * remainder)
        return remainder

    def write_size(self, writer: Writer):
        """Writes the size of the block.
        
        `writer`: A Writer object."""
        writer.seek(self.data_start - 12)
        writer.write_uint32(self.size)

    def write_end_data(self, writer: Writer):
        """Writes the ab padding, size, and seeks to the end of a block.
        
        `writer`: A Writer object."""
        offset = writer.tell()
        remainder = self.write_ab_padding(writer)
    
        self.write_size(writer)
        writer.seek(offset)
        
        if remainder == 0:
            return
        
        writer.write_bytes(b"\xAB" * remainder)
        self.seek_to_end(writer)
   