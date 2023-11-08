import struct
from io import BytesIO

types = {
    "little": {"uint8": "<B", "uint16": "<H", "uint32": "<I"},
    "big": {"uint8": ">B", "uint16": ">H", "uint32": ">I"},
}


class Reader:
    """A class utilized for reading binary files into a stream object."""

    def __init__(self, data: bytes, byte_order: str = "little"):
        self.data = BytesIO(data)
        self.byte_order = byte_order

    def change_byte_order(self, byte_order: str) -> None:
        """Changes the byte order of the Reader."""
        self.byte_order = byte_order

    def get_utf16_encoding(self) -> str:
        """Returns the UTF-16 encoding of the stream."""
        return "UTF-16-LE" if self.byte_order == "little" else "UTF-16-BE"

    def skip(self, length: int) -> None:
        """Skips `length` amount of bytes."""
        self.data.read(length)

    def read_bytes(self, length: int) -> bytes:
        """Reads `length` amount of bytes."""
        return self.data.read(length)

    def seek(self, offset: int, whence: int = 0) -> None:
        """Seeks to an offset with whence."""
        self.data.seek(offset, whence)

    def tell(self) -> int:
        """Returns the current position in the stream."""
        return self.data.tell()

    def read_uint8(self) -> int:
        """Reads a UInt8 from the stream."""
        return struct.unpack(types[self.byte_order]["uint8"], self.data.read(1))[0]

    def read_uint16(self) -> int:
        """Reads a UInt16 from the stream."""
        return struct.unpack(types[self.byte_order]["uint16"], self.data.read(2))[0]

    def read_uint32(self) -> int:
        """Reads a UInt32 from the stream."""
        return struct.unpack(types[self.byte_order]["uint32"], self.data.read(4))[0]

    def read_string_len(self, length: int) -> str:
        """Reads a string that is length bytes long from the stream."""
        return self.data.read(length).decode("UTF-8")

    def read_string_nt(self) -> str:
        """Reads a null terminated string from the stream."""
        result = b""
        char = self.data.read(1)
        while char != b"\x00":
            result += char
            char = self.data.read(1)
        return result.decode("UTF-8")

    def read_utf16_string(self):
        """Reads a UTF-16 string from the stream."""
        mode = "UTF-16-LE" if self.byte_order == "little" else "UTF-16-BE"

        message = b""
        byte = self.data.read(2)
        while True:
            if byte == b"\x00\x00":
                break
            message += byte
            byte = self.data.read(2)

        return message.decode(mode)

    def read_len_prefixed_utf16_string(self):
        """Reads a UTF-16 string from the stream."""
        length = self.read_uint16()
        string = self.read_bytes(length).decode("UTF-16-LE")
        return string
