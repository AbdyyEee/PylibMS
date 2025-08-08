from dataclasses import dataclass, field

from lms.common.lms_datatype import LMS_DataType


@dataclass(frozen=True)
class ValueDefinition:
    name: str
    description: str
    datatype: LMS_DataType
    list_items: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):
        name, description = data["name"], data["description"]
        datatype = LMS_DataType.from_string(data["datatype"])
        list_items = data.get("list_items", [])
        return cls(name, description, datatype, list_items)
