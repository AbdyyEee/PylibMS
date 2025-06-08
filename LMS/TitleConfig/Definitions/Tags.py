from __future__ import annotations

from dataclasses import dataclass, field

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
            f"Tag name '{tag}' not found in group '{group}'. Os the tag defined?"
        )

    def get_definition_by_indexes(self, group: int, tag: int) -> TagDefinition:
        for tag_def in self.definitions:
            if tag_def.group_index == group and tag_def.tag_index == tag:
                return tag_def

        raise KeyError(
            f"Tag index of {tag} was not found in group index {group}. Is the tag defined?"
        )
