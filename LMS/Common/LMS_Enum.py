from enum import Enum
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer

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
    def action_based_value(self, stream: Reader | Writer, value: "LMS_BinaryTypes", parameter = None, action: str = "read" or "write") -> None:
        bit_type = LMS_BinaryTypes._get_bits(value)
        if action == "read":
            if bit_type == "8":
                return stream.read_uint8()
            elif bit_type == "16":
                return stream.read_uint16()
            elif bit_type == "32":
                return stream.read_uint32()

        elif action == "write":
            if bit_type == "8":
                stream.write_uint8(parameter)
            elif bit_type == "16":
                stream.write_uint16(parameter)
            elif bit_type == "32":
                stream.write_uint32(parameter)

    @classmethod
    def _int_type(self, value: "LMS_BinaryTypes") -> bool:
        return value in [
            self.UINT8_0,
            self.UINT8_1,
            self.FLOAT,
            self.UINT16_0,
            self.UINT16_1,
            self.UINT16_2,
            self.UINT32_0,
            self.UINT32_1
        ]

    @classmethod
    def _int_type(self, value: "LMS_BinaryTypes") -> bool:
        return LMS_BinaryTypes._get_bits(value) is not None
    
    @classmethod
    def _get_bits(self, value: "LMS_BinaryTypes") -> str:
        if self._8_bit_type(value):
            return "8"
        
        if self._16_bit_type(value):
            return "16"
        
        if self._32_bit_type(value):
            return "32"
        
        return None

    @classmethod
    def _8_bit_type(self, value: "LMS_BinaryTypes" or int):
        """Returns if a value or type is 8 bits.

        :param `value`: A int or LMS_Type enum value."""
        if isinstance(value, int):
            value = self(value)

        # Exlcude list type as it has special reading
        return value in (self.UINT8_0, self.UINT8_1, self.FLOAT)

    @classmethod
    def _16_bit_type(self, value: "LMS_BinaryTypes" or int):
        """Returns if a value or type is 16 bits.

        :param `value`: A int or LMS_Type enum value."""
        if isinstance(value, int):
            value = LMS_BinaryTypes(value)

        return value in (self.UINT16_0, self.UINT16_1, self.UINT16_2)

    @classmethod
    def _32_bit_type(self, value: "LMS_BinaryTypes" or int):
        """Returns if a value or type is 32 bits.

        :param `value`: A int or LMS_Type enum value."""
        if isinstance(value, int):
            value = self(value)

        # Exlcude String type as it has special reading
        return value in (self.UINT32_0, self.UINT32_1)
