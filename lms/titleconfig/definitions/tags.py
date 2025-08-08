from __future__ import annotations

from dataclasses import dataclass, field

from lms.common.lms_datatype import LMS_DataType
from lms.titleconfig.definitions.value import ValueDefinition

class TagConfig:
    """Class that represents an tag structure definition."""

    def __init__(self, group_map: dict[int, str], definitions: list[TagDefinition]):
        self._group_map = group_map
        self._definitions = definitions
        self.silence_reading_exceptions = False

    @property
    def group_map(self) -> dict[int, str]:
        return self._group_map

    @property
    def definitions(self) -> list[TagDefinition]:
        return self._definitions

    def get_definition_by_names(self, group: str, tag: str) -> TagDefinition:
        group_index = None
        for i, name in self.group_map.items():
            if name == group:
                group_index = i
                break

        if group_index is None:
            raise KeyError(f"Group name '{group}' was not found! Is the group defined?")

        for tag_def in self.definitions:
            if tag_def.group_id == group_index and tag_def.tag_name == tag:
                return tag_def

        raise KeyError(
            f"Tag name '{tag}' not found in group '{group}'. Is the tag defined?"
        )

    def get_definition_by_indexes(
        self, group_id: int, tag_index: int
    ) -> TagDefinition | None:
        if group_id not in self._group_map:
            return None

        for tag_def in self.definitions:
            if tag_def.group_id == group_id and tag_def.tag_index == tag_index:
                return tag_def

        return None


@dataclass(frozen=True)
class TagDefinition:
    """Class that represents a signle tag definition in the structure."""

    group_name: str
    group_id: int
    tag_name: str
    tag_index: int
    description: str
    parameters: list[ValueDefinition] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict, group_map: dict[int, str]):
        tag_name = data["name"]
        group_index, tag_index = data["group_id"], data["tag_index"]
        group_name = group_map[group_index]
        tag_description = data["description"]

        group_name = group_map[group_index]

        parameters = []
        if "parameters" in data:
            for param_def in data["parameters"]:
                param_name = param_def["name"]
                param_description = param_def["description"]
                datatype = LMS_DataType.from_string(param_def["datatype"])
                list_items = param_def.get("list_items")
                parameters.append(
                    ValueDefinition(param_name, param_description, datatype, list_items)
                )

        return cls(
            group_name,
            group_index,
            tag_name,
            tag_index,
            tag_description,
            parameters,
        )
