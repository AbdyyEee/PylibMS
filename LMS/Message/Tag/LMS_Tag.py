import re
from abc import ABC, abstractmethod

from LMS.Message.Definitions.Field.LMS_Field import LMS_Field, cast_value
from LMS.Message.Definitions.Field.LMS_FieldMap import LMS_FieldMap
from LMS.Message.Tag.LMS_TagExceptions import LMS_InvalidTagFormatError
from LMS.Message.Tag.Tag_Formats import (DECODED_FORMAT, ENCODED_FORMAT,
                                         PARAMETER_FORMAT)
from LMS.TitleConfig.Definitions.Tags import TagConfig


class LMS_TagBase(ABC):
    def __init__(
        self,
        group_index: int,
        tag_index: int,
        parameters: LMS_FieldMap | list[str] | None = None,
        group_name: str = None,
        tag_name: str = None,
    ):
        self._group_index = group_index
        self._tag_index = tag_index
        self._parameters = parameters or {}
        self._group_name, self._tag_name = group_name, tag_name

    @property
    def group_index(self) -> int:
        """The index of the group."""
        return self._group_index

    @property
    def tag_index(self) -> int:
        """The index of the tag in it's group."""
        return self._tag_index

    @property
    def group_name(self) -> str:
        """The name of the tag group."""
        return self._group_name

    @property
    def tag_name(self) -> str:
        """The name of the tag in the tag group."""
        return self._tag_name

    @property
    def parameters(self) -> list[str] | LMS_FieldMap:
        """The parameters of the tag."""
        return self._parameters

    @abstractmethod
    def to_text(self) -> str:
        """Converts the tag to its string representation."""
        pass

    @classmethod
    @abstractmethod
    def from_string(self, string: str, config: TagConfig | None = None) -> str:
        pass


class LMS_EncodedTag(LMS_TagBase):
    """A class that represents an encoded tag.

    Example encoded tags:
        - `[0:3 00-00-00-FF]`
        - `[0:4]`
        - `[1:0 01-00-00-CD]`"""

    def __init__(
        self,
        group_index: int,
        tag_index: int,
        parameters: list[str] = None,
        group_name: str = None,
        tag_name: str = None,
    ):
        super().__init__(group_index, tag_index, parameters)
        self._group_name = group_name
        self._tag_name = tag_name

    def to_text(self) -> str:
        if self._group_name is not None and self._tag_name is not None:
            # Determine what to display based on if the names are provided
            group = self._group_name or self._group_index
            tag = self._tag_name or self._tag_index
        else:
            group, tag = self._group_index, self._tag_index

        if not self._parameters:
            return f"[{group}:{tag}]"

        parameters = "-".join(self.parameters)
        return f"[{group}:{tag} {parameters}]"

    @classmethod
    def from_string(cls, string: str, config: TagConfig | None = None):
        if match := re.match(ENCODED_FORMAT, string):
            group, tag = match.group(1), match.group(2)
            parameters = match.group(3).split("-")

            if group.isdigit() and tag.isdigit():
                return cls(int(group), int(tag), parameters)

            tag_definition = config.get_definition_by_names(group, tag)
            return cls(
                group,
                tag,
                parameters,
                tag_definition.group_name,
                tag_definition.tag_name,
            )
        else:
            raise LMS_InvalidTagFormatError(
                f"Invalid encoded tag format detected for tag'{string}'"
            )


class LMS_DecodedTag(LMS_TagBase):
    """A class that represents a decoded tag.

    Example encoded tags:
        - `[System:Color r="0" g="255" b="255" a="255"]`
        - `[System:Pagebreak]`
        - `[Mii:Nickname buffer="1" type="Text" conversion="None"]`"""

    def __init__(
        self,
        group_index: int,
        tag_index: int,
        group_name: str,
        tag_name: str,
        parameters: LMS_FieldMap = None,
    ):
        super().__init__(group_index, tag_index, parameters, group_name, tag_name)

    def to_text(self) -> str:
        if not self._parameters:
            return f"[{self.group_name}:{self.tag_name}]"

        parameters = " ".join(
            f'{key}="{param._value}"' for key, param in self._parameters.items()
        )
        return f"[{self.group_name}:{self.tag_name} {parameters}]"

    @classmethod
    def from_string(cls, tag: str, config: TagConfig):
        if match := re.match(DECODED_FORMAT, tag):
            group_name, tag_name = match.group(1), match.group(2)
            parameters = dict(re.findall(PARAMETER_FORMAT, tag))

            tag_definition = config.get_definition_by_names(group_name, tag_name)
            for definition in tag_definition.parameters:
                casted_value = cast_value(
                    parameters[definition.name], definition.datatype
                )
                parameters[definition.name] = LMS_Field(casted_value, definition)

            return cls(
                tag_definition.group_index,
                tag_definition.tag_index,
                group_name,
                tag_name,
                parameters,
            )
        else:
            raise LMS_InvalidTagFormatError(
                f"Invalid decoded tag format detectefd for tag '{tag}'"
            )
