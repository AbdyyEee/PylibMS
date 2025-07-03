from __future__ import annotations

from dataclasses import dataclass, field

from LMS.Common.LMS_DataType import LMS_DataType
from LMS.TitleConfig.Definitions.Value import ValueDefinition


@dataclass(frozen=True)
class TagDefinition:
    """Class that represents a signle tag definition in the structure."""

    group_name: str
    group_index: int
    tag_name: str
    tag_index: int
    description: str
    parameters: list[ValueDefinition] = field(default=None)

    @classmethod
    def from_dict(cls, data: dict, group_map: dict[int, str]):
        tag_name = data["name"]
        group_index, tag_index = data["group_index"], data["tag_index"]
        group_name = group_map[group_index]
        tag_description = data["description"]

        group_name = group_map[group_index]

        parameters = None
        if "parameters" in data:
            parameters = []
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


@dataclass(frozen=True)
class TagConfig:
    """Class that represents an tag structure definition."""

    group_map: dict[int, str]
    definitions: list[TagDefinition]

    def get_definition_by_names(self, group: str, tag: str) -> TagDefinition:
        group_index = None
        for i, name in self.group_map.items():
            if name == group:
                group_index = i
                break

        if group_index is None:
            raise KeyError(f"Group name '{group}' was not found! Is the group defined?")

        for tag_def in self.definitions:
            if tag_def.group_index == group_index and tag_def.tag_name == tag:
                return tag_def

        raise KeyError(
            f"Tag name '{tag}' not found in group '{group}'. Is the tag defined?"
        )

    def get_definition_by_indexes(self, group: int, tag: int) -> TagDefinition:
        for tag_def in self.definitions:
            if tag_def.group_index == group and tag_def.tag_index == tag:
                return tag_def

        raise KeyError(
            f"Tag index of {tag} was not found in group index {group}. Is the tag defined?"
        )
