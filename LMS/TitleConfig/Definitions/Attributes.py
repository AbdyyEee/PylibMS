from dataclasses import dataclass, field

from LMS.TitleConfig.Definitions.Value import ValueDefinition


@dataclass(frozen=True)
class AttributeConfig:
    """Class that represents an attribute config definition"""
    name: str
    description: str = field(repr=False)
    definitions: list[ValueDefinition]
