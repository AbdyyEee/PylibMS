from dataclasses import dataclass, field

from LMS.Common.LMS_DataType import LMS_DataType


@dataclass(frozen=True)
class ValueDefinition:
    name: str
    description: str
    datatype: LMS_DataType
    list_items: dict[int, str] = field(default=None)

    @classmethod
    def from_dict(cls, data: dict):
        name, description = data["name"], data["description"]
        datatype = LMS_DataType.from_string(data["datatype"])
        list_items = data.get("list_items")
        return cls(name, description, datatype, list_items)
