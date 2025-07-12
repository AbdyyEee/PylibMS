from LMS.Common.LMS_DataType import LMS_DataType
from LMS.TitleConfig.Definitions.Value import ValueDefinition


class LMS_Field:
    """A class that represents a mapped field linked to a config definition.

    Acts as values for Attributes and Tag Parameters."""

    def __init__(
        self, value: int | str | float | bytes | bool, definition: ValueDefinition
    ):
        self._definition = definition
        self._verify_value(value)
        self._value = value

    def __repr__(self):
        typename = self._definition.datatype.name
        if typename == "LIST":
            if len(self.list_items) > 6:
                preview = self.list_items[:3] + ["..."]
            else:
                preview = self.list_items
            return f"LMS_Field(value={self._value}, options={preview})"
        return f"LMS_Field(value={self._value!r}, type={typename})"

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
        """The list items bound to the field instance. Only is valid for LMS_Datatype.LIST values."""
        return self._definition.list_items

    @value.setter
    def value(self, new_value: int | str | float | bytes | bool):
        self._verify_value(new_value)
        self._value = new_value

    def _verify_value(self, value: int | str | float | bytes | bool) -> None:
        datatype = self._definition.datatype

        # Check if the value is not the correct instance of the datatype
        if type(value) is not (builtin_type := datatype.builtin_type):
            raise TypeError(
                f"The value provided for '{self.name}' type '{type(value)}' should be '{builtin_type.__name__}'."
            )

        # These values require no extra verification
        if datatype in (LMS_DataType.BOOL, LMS_DataType.STRING):
            return

        match datatype:
            case LMS_DataType.BYTE:
                if len(value) != 1:
                    raise ValueError("Byte types only work for values of length 1!")
                else:
                    return
            case LMS_DataType.LIST:
                if value not in self._definition.list_items:
                    raise ValueError(
                        f"The value of '{value}' provided for field '{self.name}' is not in the list {self._definition.list_items}."
                    )
                else:
                    return
            case LMS_DataType.FLOAT32:
                min_value, max_value = -3.4028235e38, 3.4028235e38
            # Other number types fall here
            case _:
                bits = datatype.stream_size * 8
                if datatype.signed:
                    max_value = 2 ** (bits - 1)
                    min_value = -max_value
                else:
                    min_value, max_value = 0, (2**bits) - 1

        if not min_value <= value <= max_value:
            raise ValueError(
                f"The value '{value}' of type '{datatype}' provided for field '{self.name}' is out of range of ({min_value}, {max_value})"
            )


def cast_value(value: int | str | float | bytes | bool, datatype: LMS_DataType) -> str:
    if datatype in (LMS_DataType.STRING, LMS_DataType.LIST):
        return value

    match datatype:
        case LMS_DataType.BYTE:
            return hex(int(value))
        case LMS_DataType.BOOL:
            if value not in ("false", "true"):
                raise ValueError("Value must be true or false for bool type.")
            return value.strip().lower() == "true"
        case LMS_DataType.FLOAT32:
            return float(value)
        case _:
            return int(value)
