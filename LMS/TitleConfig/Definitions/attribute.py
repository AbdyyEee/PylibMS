from dataclasses import dataclass, field

from lms.titleconfig.definitions.value import ValueDefinition


@dataclass(frozen=True)
class AttributeConfig:
    """Class that represents an attribute config definition"""

    name: str
    description: str
    definitions: list[ValueDefinition]
