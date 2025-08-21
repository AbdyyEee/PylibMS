import re
from typing import TypeGuard

from lms.message.definitions.field.lms_field import LMS_FieldMap
from lms.message.tag.lms_tagexceptions import LMS_InvalidTagFormatError
from lms.titleconfig.definitions.tags import TagConfig, TagDefinition

TAG_PADDING_CHAR = "CD"

type LMS_ControlTag = LMS_EncodedTag | LMS_DecodedTag


def is_tag(obj: object) -> TypeGuard[LMS_ControlTag]:
    """Typeguard to narrow tag objects."""
    return isinstance(obj, (LMS_EncodedTag, LMS_DecodedTag))


class LMS_EncodedTag:
    """
    A class that represents an encoded tag.

    Example encoded tags:
        - `[0:3 00-00-00-FF]`
        - `[0:4]`
        - `[1:0 01-00-00-CD]`
    """

    TAG_FORMAT = re.compile(r"\[\s*(/)?\s*(\d+)\s*:\s*(\d+)[^]]*]")
    PARAMETER_FORMAT = re.compile(r"^\s*([0-9A-Fa-f]{2})(\s*-\s*[0-9A-Fa-f]{2})*\s*$")

    def __init__(
        self,
        group_id: int,
        tag_index: int,
        parameters: list[str] | None = None,
        is_fallback: bool = False,
        is_closing: bool = False,
    ):
        self._group_id = group_id
        self._tag_index = tag_index
        self._parameters = parameters

        self._is_fallback = is_fallback
        self._is_closing = is_closing

    @property
    def group_id(self) -> int:
        """The group id for the tag."""
        return self._group_id

    @property
    def tag_index(self) -> int:
        """The tag index in the tags group."""
        return self._tag_index

    @property
    def parameters(self) -> list[str] | None:
        """The list of hex string parameters."""
        return self._parameters

    @property
    def is_fallback(self) -> bool:
        """Determines if the tag is a fallback tag."""
        return self._is_fallback

    @property
    def is_closing(self) -> bool:
        """Determines if the tag is a closing tag."""
        return self._is_closing

    def to_text(self) -> str:
        if self._is_closing:
            return f"[/{self._group_id}:{self._tag_index}]"

        fallback_prefix = "!" if self._is_fallback else ""

        if self._parameters is None:
            return f"[{self.group_id}:{self.tag_index}]"

        parameters = "-".join(self._parameters)
        return f"[{fallback_prefix}{self.group_id}:{self.tag_index} {parameters}]"

    @classmethod
    def from_string(cls, tag: str):
        if not (match := cls.TAG_FORMAT.match(tag)):
            raise LMS_InvalidTagFormatError(
                f"Invalid encoded tag format detected for tag: '{tag}'"
            )

        is_closing = match.group(1) is not None
        group_id, tag_index = match.group(2), match.group(3)

        if not group_id.isdigit() or not tag_index.isdigit():
            raise LMS_InvalidTagFormatError(
                f"The group id and or tag index must be digits in tag: '{tag}'"
            )

        group_id, tag_index = int(group_id), int(tag_index)

        if is_closing:
            return cls(group_id, tag_index, is_closing=True)

        param_str = tag[match.end(3) :].strip().removesuffix("]").strip()

        if not param_str:
            return cls(group_id, tag_index)

        if not cls.PARAMETER_FORMAT.match(param_str):
            raise LMS_InvalidTagFormatError(
                f"Malformed parameters located in tag: '{tag}'"
            )

        parameters = [param.strip().upper() for param in param_str.split("-")]

        # Ensure 0xCD padding is added
        if len(parameters) % 2 == 1:
            parameters.append(TAG_PADDING_CHAR)

        return cls(group_id, tag_index, parameters)


class LMS_DecodedTag:
    """
    A class that represents a decoded tag.

    Example decoded tags:
        - `[System:Color r="0" g="255" b="255" a="255"]`
        - `[System:PageBreak]`
        - `[Mii:Nickname buffer="1" type="Text" conversion="None"]`
    """

    TAG_FORMAT = re.compile(
        r"\[\s*(/)?\s*([A-Za-z]\w*)\s*:\s*([A-Za-z]+)(?:\s+[^]]*)?\s*]"
    )
    PARAMETER_FORMAT = re.compile(r'(\w+)="([^"]*)"')

    def __init__(
        self,
        definition: TagDefinition,
        parameters: LMS_FieldMap | None = None,
        is_closing: bool = False,
    ):
        self._definition = definition
        self._parameters = parameters

        self._is_closing = is_closing

    @property
    def group_id(self) -> int:
        """The group id for the tag."""
        return self._definition.group_id

    @property
    def tag_index(self) -> int:
        """The tag index in the tags group."""
        return self._definition.tag_index

    @property
    def group_name(self) -> str:
        """The name of the tag group."""
        return self._definition.group_name

    @property
    def tag_name(self) -> str:
        """The name of the tag in the tag group."""
        return self._definition.tag_name

    @property
    def description(self) -> str:
        """The description of the tag."""
        return self._definition.description

    @property
    def is_closing(self) -> bool:
        """Determines if the tag is a closing tag."""
        return self._is_closing

    @property
    def parameters(self) -> LMS_FieldMap | None:
        """The map of parameters for the tag."""
        return self._parameters

    def to_text(self) -> str:
        if self._is_closing:
            return f"[/{self._definition.group_name}:{self._definition.tag_name}]"

        if not self._parameters:
            return f"[{self._definition.group_name}:{self._definition.tag_name}]"

        parameters = []
        for param in self._parameters:
            if isinstance(param.value, bytes):
                parameters.append(f'{param.name}="{param.value.hex()}"')
            else:
                parameters.append(f'{param.name}="{param.value}"')

        parameters = " ".join(parameters)
        return (
            f"[{self._definition.group_name}:{self._definition.tag_name} {parameters}]"
        )

    @classmethod
    def from_string(cls, tag: str, config: TagConfig):
        if not (match := cls.TAG_FORMAT.match(tag)):
            raise LMS_InvalidTagFormatError(
                f"Invalid decoded tag format detected for tag '{tag}'"
            )

        is_closing = match.group(1) is not None
        group_name, tag_name = match.group(2), match.group(3)
        tag_definition = config.get_definition_by_names(group_name, tag_name)

        if is_closing:
            return cls(tag_definition, is_closing=True)

        parameters = dict(cls.PARAMETER_FORMAT.findall(tag))
        parameter_map = LMS_FieldMap.from_string_dict(
            parameters, tag_definition.parameters
        )
        return cls(tag_definition, parameter_map)
