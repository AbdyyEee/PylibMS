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

    @classmethod
    def _8_bit_type(self, value: "LMS_BinaryTypes" or int):
        """Returns if a value or type is 8 bits.

        :param `value`: A int or LMS_Type enum value."""
        if isinstance(value, int):
            value = self(value)

        # Exlcude list type as it has special reading
        return value in [self.UINT8_0, self.UINT8_1, self.FLOAT]

    @classmethod
    def _16_bit_type(self, value: "LMS_BinaryTypes" or int):
        """Returns if a value or type is 16 bits.

        :param `value`: A int or LMS_Type enum value."""
        if isinstance(value, int):
            value = LMS_BinaryTypes(value)

        return value in [self.UINT16_0, self.UINT16_1, self.UINT16_2]

    @classmethod
    def _32_bit_type(self, value: "LMS_BinaryTypes" or int):
        """Returns if a value or type is 32 bits.

        :param `value`: A int or LMS_Type enum value."""
        if isinstance(value, int):
            value = self(value)

        # Exlcude String type as it has special reading
        return value in [self.UINT32_0, self.UINT32_1]
