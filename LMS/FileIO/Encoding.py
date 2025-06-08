from enum import Enum
from typing import Literal


class FileEncoding(Enum):
    """An enum that represents a file encoding."""

    UTF8 = 0
    UTF16 = 1
    UTF32 = 2

    def to_string_format(
        self, big_endian: bool = False
    ) -> Literal["UTF-8", "UTF-16-LE", "UTF-16-BE", "UTF-32-LE", "UTF-32-BE"]:
        """Returns the encoding in the string format"""
        match self:
            case FileEncoding.UTF8:
                return "UTF-8"
            case FileEncoding.UTF16:
                if big_endian:
                    return "UTF-16-BE"
                return "UTF-16-LE"
            case FileEncoding.UTF32:
                if big_endian:
                    return "UTF-32-BE"
                return "UTF-32-LE"

    @property
    def width(self) -> Literal[1, 2, 4]:
        """The width of a character in a stream."""
        match self:
            case FileEncoding.UTF8:
                return 1
            case FileEncoding.UTF16:
                return 2
            case FileEncoding.UTF32:
                return 4

    @property
    def terminator(self) -> Literal[b"\x00", b"\x00\x00", b"\x00\x00\x00\x00"]:
        """The terminator of the string in a stream."""
        return b"\x00" * self.width
