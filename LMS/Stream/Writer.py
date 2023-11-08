import struct
from io import BytesIO


types = {
    "little": {"uint8": "<B", "uint16": "<H", "uint32": "<I"},
    "big": {"uint8": ">B", "uint16": ">H", "uint32": ">I"},
}


class Writer:
    """A class utilized for writing to a stream."""

    def __init__(self, data: BytesIO, byte_order: str = "little"):
        self.data = BytesIO(data)
        self.byte_order = byte_order

    def get_utf16_encoding(self) -> str:
        """Returns the UTF-16 encoding of the stream."""
        return "UTF-16-LE" if self.byte_order == "little" else "UTF-16-BE"

    def skip(self, length: int) -> None:
        """Skips `length` amount of bytes."""
        self.data.read(length)

    def write_bytes(self, data: bytes) -> None:
        """Writes specifc bytes to the stream."""
        self.data.write(data)

    def seek(self, offset: int, whence: int = 0) -> None:
        """Seeks to an offset with whence."""
        self.data.seek(offset, whence)

    def tell(self) -> int:
        """Returns the current position in the stream."""
        return self.data.tell()

    def write_string_nt(self, string: str) -> None:
        """Writes a null terminated string to the stream."""
        self.data.write(string.encode("UTF-8") + b"\x00")

    def write_string(self, string: str) -> None:
        """Writes a  string to the stream."""
        self.data.write(string.encode("UTF-8"))

    def write_uint8(self, num: int):
        """Writes a UInt8 to the stream."""
        self.data.write(struct.pack(types[self.byte_order]["uint8"], num))

    def write_uint16(self, num: int):
        """Writes a UInt16 to the stream."""
        self.data.write(struct.pack(types[self.byte_order]["uint16"], num))

    def write_uint32(self, num: int):
        """Writes a UInt32 to the stream."""
        self.data.write(struct.pack(types[self.byte_order]["uint32"], num))

    def write_utf16_string(self, string: str, use_double: bool = False):
        """Writes a  UTF-16 string to a stream."""
        encoding = "UTF-16-LE" if self.byte_order == "little" else "UTF-16-BE"
        self.write_bytes(string.encode(encoding))
        if use_double:
            self.write_bytes(b"\x00\x00")

    def write_len_prefixed_utf16_string(self, string: str):
        """Writes a length prefixed UTF-16 string to a stream."""
        encoding = "UTF-16-LE" if self.byte_order == "little" else "UTF-16-BE"
        string = string.encode(encoding)
        self.write_uint16(len(string))
        self.write_bytes(string)

    def get_data(self) -> bytes:
        return self.data.getvalue()
