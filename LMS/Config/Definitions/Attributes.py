from dataclasses import dataclass, field

from LMS.Config.Definitions.Value import ValueDefinition


@dataclass(frozen=True)
class AttributeConfig:
    """Class that represents an attribute structure definition.

    Configs may have multiple, linked to the if a game has multiple MSBP files."""

    name: str
    description: str = field(repr=False)
    definitions: list[ValueDefinition]
