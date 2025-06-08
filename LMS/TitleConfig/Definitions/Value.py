from dataclasses import dataclass, field

from LMS.Field.LMS_DataType import LMS_DataType


@dataclass(frozen=True)
class ValueDefinition:
    name: str
    description: str
    datatype: LMS_DataType
    list_items: dict[int, str] = field(default=None)
