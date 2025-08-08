from enum import Enum
from typing import Literal, Type


class LMS_DataType(Enum):
    """Enum that represents a datatype for a value entry in a MSBT/MSBP file."""

    UINT8 = 0
    UINT16 = 1
    UINT32 = 2

    INT8 = 3
    INT16 = 4
    INT32 = 5

    FLOAT32 = 6

    # Unknown 16 bit type (value of 6) has yet to be documented
    # Might be some sort of 2 byte integer, float, or may be an array.
    # We wont ever know cause no game (yet that has been found) has utilized this type
    # Thanks Nintendo.
    ...

    STRING = 8
    LIST = 9

    # These types are not offical, but allow for abstraction from the value of the actual type
    # As an example, BOOL can be utilized for UInt8 values that act like a bool
    # Byte types can also be used for when the type/value is unknown or if there is extra data in the tag.
    BOOL = "bool"
    BYTES = "byte"

    def to_string(self) -> str:
        return self._name_.lower()

    @property
    def signed(self) -> bool:
        """Property for if the type is signed or not."""
        if self not in [
            LMS_DataType.STRING,
            LMS_DataType.LIST,
            LMS_DataType.BOOL,
            LMS_DataType.BYTES,
        ]:
            return self in [LMS_DataType.INT8, LMS_DataType.INT16, LMS_DataType.INT32]

        raise TypeError(f"Signed is not a valid property for '{self.to_string()}'!")

    @property
    def builtin_type(self) -> Type[int | str | float | bool | bytes]:
        """The enum as the builtin python type."""
        return {
            LMS_DataType.UINT8: int,
            LMS_DataType.UINT16: int,
            LMS_DataType.UINT32: int,
            LMS_DataType.INT8: int,
            LMS_DataType.INT16: int,
            LMS_DataType.INT32: int,
            LMS_DataType.FLOAT32: float,
            LMS_DataType.STRING: str,
            LMS_DataType.LIST: str,
            LMS_DataType.BOOL: bool,
            LMS_DataType.BYTES: bytes,
        }[self]

    @property
    def stream_size(self):
        """The size the datatype takes up in a stream."""
        return {
            LMS_DataType.UINT8: 1,
            LMS_DataType.UINT16: 2,
            LMS_DataType.UINT32: 4,
            LMS_DataType.INT8: 1,
            LMS_DataType.INT16: 2,
            LMS_DataType.INT32: 4,
            LMS_DataType.FLOAT32: 4,
            LMS_DataType.LIST: 1,
            LMS_DataType.BOOL: 1,
            LMS_DataType.BYTES: 1,
        }[self]

    @classmethod
    def from_string(cls, string: str):
        """Creates a LMS_Datatype enum value from it's string representation"""
        string = string.upper()
        if string in cls.__members__:
            return cls[string]
        else:
            raise ValueError(f"Unknown value of '{string}' was provided!")
