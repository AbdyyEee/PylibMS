from enum import Enum
from typing import Literal


class FileEncoding(Enum):
    """An enum that represents a file encoding."""

    UTF8 = 0
    UTF16 = 1
    UTF32 = 2

    def to_string_format(self, is_big_endian: bool = False):
        match self:
            case FileEncoding.UTF8:
                return "UTF-8"
            case FileEncoding.UTF16:
                if is_big_endian:
                    return "UTF-16-BE"
                return "UTF-16-LE"
            case FileEncoding.UTF32:
                if is_big_endian:
                    return "UTF-32-BE"
                return "UTF-32-LE"

    @property
    def width(self):
        match self:
            case FileEncoding.UTF8:
                return 1
            case FileEncoding.UTF16:
                return 2
            case FileEncoding.UTF32:
                return 4

    @property
    def terminator(self):
        return b"\x00" * self.width
