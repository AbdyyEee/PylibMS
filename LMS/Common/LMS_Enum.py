from enum import Enum


class LMS_MessageEncoding(Enum):
    """An enum for representing message encoding. As in offical LMS files."""
    UTF8 = 0
    UTF16 = 1
    UTF32 = 2

class LMS_Types(Enum):
    """A class that represents binary types utilized in attributes and tags."""
    uint8_0 = 0
    uint8_1 = 3
    float = 6 # According to Trippixyz on discord, float will be parsed like a regular UInt8 though.
    uint16_0 = 1
    uint16_1 = 4
    uint16_2 = 7
    uint32_0 = 2
    uint32_1 = 5
    string = 8
    list_index = 9
