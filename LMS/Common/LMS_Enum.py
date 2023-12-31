from enum import Enum


class LMS_MessageEncoding(Enum):
    """An enum for representing message encoding. As in offical LMS files."""

    UTF8 = 0
    UTF16 = 1
    UTF32 = 2


class LMS_BinaryTypes(Enum):
    """A class that represents binary types utilized in attributes and tags."""

    UINT8_0 = 0
    UINT8_1 = 3
    FLOAT = 6
    UINT16_0 = 1
    UINT16_1 = 4
    UINT16_2 = 7
    UINT32_0 = 2
    UINT32_1 = 5
    STRING = 8
    LIST_INDEX = 9
