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
    A wrapper for a dictionary of LMS_Field objects for controlled access, validation and abstraction from the dictionary object.
    """

    fields: dict[str, LMS_Field]

    def __iter__(self) -> Iterator[LMS_Field]:
        return iter(self.fields.values())

    def __getitem__(self, name: str) -> LMS_Field:
        if name not in self.fields:
            raise KeyError(f"Field '{name}' does not exist")

        return self.fields[name]

    def __setitem__(self, name: str, value: FieldValue) -> None:
        if name not in self.fields:
            raise KeyError(f"Field '{name}' does not exist")

        self.fields[name].value = value

    def to_dict(self) -> dict[str, FieldValue]:
        """Converts the field map to a regular dictionary."""
        return {field.name: field.value for field in self.fields.values()}

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
            if definition.datatype in (LMS_DataType.STRING, LMS_DataType.LIST):
                fields[definition.name] = LMS_Field(data[definition.name], definition)
                continue

            value = data[definition.name]
            match definition.datatype:
                case LMS_DataType.BYTES:
                    casted_value = bytes.fromhex(value)
                case LMS_DataType.BOOL:
                    if value not in ("false", "true"):
                        raise ValueError("Value must be true or false for bool type.")
                    casted_value = value.strip().lower() == "true"
                case LMS_DataType.FLOAT32:
                    casted_value = float(value)
                case _:
                    casted_value = int(value)

            fields[definition.name] = LMS_Field(casted_value, definition)

        return cls(fields)


class LMS_Field:
    """
    A class that represents a mapped value linked to a config definition.
    """

    def __init__(
        self, value: int | str | float | bytes | bool, definition: ValueDefinition
    ):
        _verify_value(value, definition)
        self._definition = definition
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
        _verify_value(new_value, self._definition)
        self._value = new_value


def _verify_value(
    value: int | str | float | bytes | bool, definition: ValueDefinition
) -> None:
    datatype = definition.datatype

    if datatype in (LMS_DataType.BOOL, LMS_DataType.STRING):
        return

    match datatype:
        case LMS_DataType.BYTES if isinstance(value, bytes):
            if len(value) != 1:
                raise ValueError("Byte types only work for values of length 1!")
            else:
                return
        case LMS_DataType.LIST if isinstance(value, str):
            if value not in definition.list_items:
                raise ValueError(
                    f"The value of '{value}' provided for field '{definition.name}' is not in the list {definition.list_items}."
                )
            else:
                return
        case LMS_DataType.FLOAT32 if isinstance(value, float):
            _verify_range(value, FLOAT_MIN, FLOAT_MAX, definition)
            return
        case _ if isinstance(value, int):
            bits = datatype.stream_size * 8
            if datatype.signed:
                max_value = 2 ** (bits - 1)
                min_value = -max_value
            else:
                min_value, max_value = 0, (2**bits) - 1

            _verify_range(value, min_value, max_value, definition)
            return

    raise TypeError(
        f"The value provided for '{definition.name}' type '{type(value)}' should be '{datatype.builtin_type}'."
    )


def _verify_range(
    value: int | float, min: int | float, max: int | float, definition: ValueDefinition
):
    if not min <= value <= max:
        raise ValueError(
            f"The value '{value}' of type '{definition.datatype}' provided for field '{definition.name}' is out of range of ({min}, {max})"
        )
