from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import cast

from lms.common.lms_datatype import LMS_DataType
from lms.titleconfig.definitions.value import ValueDefinition

FLOAT_MIN = 1.17549435e-38
FLOAT_MAX = 3.4028235e38


type FieldValue = int | str | float | bool | bytes


@dataclass(frozen=True)
class LMS_FieldMap:
    """
    A wrapper for a dictionary of LMS_Field objects for easier access and abstraction from the dictionary object.
    """

    _fields: dict[str, LMS_Field]

    def __iter__(self) -> Iterator[LMS_Field]:
        return iter(self._fields.values())

    def __getitem__(self, name: str) -> LMS_Field:
        if name not in self._fields:
            raise KeyError(f"Field '{name}' does not exist")
        return self._fields[name]

    def __setitem__(self, name: str, value: FieldValue) -> None:
        if name not in self._fields:
            raise KeyError(f"Field '{name}' does not exist")
        self._fields[name].value = value

    def to_dict(self) -> dict[str, FieldValue]:
        """Converts the field map to a regular dictionary."""
        return {field.name: field.value for field in self._fields.values()}

    @classmethod
    def from_dict(cls, data: dict[str, FieldValue], definitions: list[ValueDefinition]):
        return cls(
            {
                definition.name: LMS_Field(data[definition.name], definition)
                for definition in definitions
            }
        )

    @classmethod
    def from_string_dict(cls, data: dict[str, str], definitions: list[ValueDefinition]):
        fields = {}

        for definition in definitions:
            value = convert_string_to_type(data[definition.name], definition.datatype)
            fields[definition.name] = LMS_Field(value, definition)

        return cls(fields)


class LMS_Field:
    """
    A class that represents a mapped field linked to a config definition.

    Acts as values for Attributes and Tag Parameters.
    """

    def __init__(
        self, value: int | str | float | bytes | bool, definition: ValueDefinition
    ):
        self._definition = definition
        self._verify_value(value)
        self._value = value

    def __repr__(self):
        if self.datatype is LMS_DataType.LIST:
            return f"LMS_Field(value={self._value}, list_items={self.list_items})"
        return f"LMS_Field(value={self._value}, type={self.datatype.name})"

    @property
    def name(self) -> str:
        """The name of the field."""
        return self._definition.name

    @property
    def description(self) -> str:
        """The description of the field."""
        return self._definition.description

    @property
    def value(self) -> int | str | float | bytes | bool:
        """The value of the field instance."""
        return self._value

    @property
    def datatype(self) -> LMS_DataType:
        """The datatype of the field instance."""
        return self._definition.datatype

    @property
    def list_items(self) -> list[str]:
        """The list items bound to the field instance. Only is valid for `LMS_Datatype.LIST` values."""
        return self._definition.list_items

    @value.setter
    def value(self, new_value: int | str | float | bytes | bool):
        self._verify_value(new_value)
        self._value = new_value

    def _verify_value(self, value: int | str | float | bytes | bool) -> None:
        datatype = self._definition.datatype

        if datatype in (LMS_DataType.BOOL, LMS_DataType.STRING):
            return

        match datatype:
            case LMS_DataType.BYTES if isinstance(value, bytes):
                if len(value) != 1:
                    raise ValueError("Byte types only work for values of length 1!")
                else:
                    return
            case LMS_DataType.LIST if isinstance(value, str):
                if value not in self._definition.list_items:
                    raise ValueError(
                        f"The value of '{value}' provided for field '{self.name}' is not in the list {self._definition.list_items}."
                    )
                else:
                    return
            case LMS_DataType.FLOAT32 if isinstance(value, float):
                _verify_range(value, FLOAT_MIN, FLOAT_MAX, self._definition)
                return
            case _ if isinstance(value, int):
                bits = datatype.stream_size * 8
                if datatype.signed:
                    max_value = 2 ** (bits - 1)
                    min_value = -max_value
                else:
                    min_value, max_value = 0, (2**bits) - 1

                _verify_range(value, min_value, max_value, self._definition)
                return

        raise TypeError(
            f"The value provided for '{self.name}' type '{type(value)}' should be '{datatype.builtin_type}'."
        )


def convert_string_to_type(
    value: str, datatype: LMS_DataType
) -> int | str | bool | float | bytes:
    if datatype in (LMS_DataType.STRING, LMS_DataType.LIST):
        return cast(str, value)

    match datatype:
        case LMS_DataType.BYTES:
            return bytes.fromhex(value)
        case LMS_DataType.BOOL:
            if value not in ("false", "true"):
                raise ValueError("Value must be true or false for bool type.")
            return value.strip().lower() == "true"
        case LMS_DataType.FLOAT32:
            return float(value)
        case _:
            return int(value)


def _verify_range(
    value: int | float, min: int | float, max: int | float, definition: ValueDefinition
):
    if not min <= value <= max:
        raise ValueError(
            f"The value '{value}' of type '{definition.datatype}' provided for field '{definition.name}' is out of range of ({min}, {max})"
        )
