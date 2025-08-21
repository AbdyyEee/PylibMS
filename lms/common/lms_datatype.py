from __future__ import annotations

from enum import Enum
from typing import Type, TypeGuard


def is_number_datatype(value: object, datatype: LMS_DataType) -> TypeGuard[int | float]:
    return datatype in (
        LMS_DataType.UINT8,
        LMS_DataType.UINT16,
        LMS_DataType.UINT32,
        LMS_DataType.INT8,
        LMS_DataType.INT16,
        LMS_DataType.INT32,
        LMS_DataType.FLOAT32,
    ) and isinstance(value, (int, float))


def is_list_datatype(value: object, datatype: LMS_DataType) -> TypeGuard[str]:
    return datatype is LMS_DataType.LIST and isinstance(value, str)


def is_bool_datatype(value: object, datatype: LMS_DataType) -> TypeGuard[bool]:
    return datatype is LMS_DataType.BOOL and isinstance(value, bool)


def is_bytes_datatype(value: object, datatype: LMS_DataType) -> TypeGuard[bytes]:
    return datatype is LMS_DataType.BYTES and isinstance(value, bytes)


def is_string_datatype(value: object, datatype: LMS_DataType) -> TypeGuard[str]:
    return datatype is LMS_DataType.STRING and isinstance(value, str)


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
    # We won't ever know cause no game (yet that has been found) has utilized this type
    # Thanks Nintendo.
    ...

    STRING = 8
    LIST = 9

    # Interface types
    # These types act as an abstraction for a real LMS_Datatype
    # The actual value isn't important since they are not real types, but are instantiated from a config
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
    def stream_size(self) -> int:
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
        """Creates an enum value from its string representation"""
        member = string.upper()
        if member in cls.__members__:
            return cls[member]

        alias_map = {
            "u8": "UINT8",
            "u16": "UINT16",
            "u32": "UINT32",
            "i8": "INT8",
            "i16": "INT16",
            "i32": "INT32",
            "f32": "FLOAT32",
            "str": "STRING",
            "bool": "BOOL",
            "byte": "BYTES",
        }

        alias_member = alias_map.get(string.lower())
        if alias_member is not None:
            return cls[alias_member]
        else:
            raise ValueError(f"Unknown value of '{string}' was provided!")
