import re
from typing import overload

from LMS.Message.Definitions.Field.LMS_Field import LMS_Field
from LMS.Message.Definitions.Field.LMS_FieldMap import LMS_FieldMap
from LMS.Message.Tag.LMS_Tag import LMS_DecodedTag, LMS_EncodedTag, LMS_TagBase
from LMS.Message.Tag.System_Definitions import get_system_tag
from LMS.Message.Tag.Tag_Formats import (DECODED_FORMAT, ENCODED_FORMAT,
                                         TAG_FORMAT)
from LMS.TitleConfig.Config import TagConfig


class LMS_MessageText:
    """Class that represents a text entry."""

    def __init__(
        self, message: str | list[str | LMS_TagBase], config: TagConfig | None = None
    ):
        # Inject a reference to the tag definitions to allow for decoding of names and parameter types
        self._config = config

        if isinstance(message, str):
            self._set_parts(message)
        else:
            self._parts = message

    def __iter__(self):
        return iter(self._parts)

    @property
    def text(self) -> str:
        """The raw text of the message."""
        return "".join(
            part.to_text() if isinstance(part, LMS_TagBase) else part
            for part in self._parts
        )

    @text.setter
    def text(self, string: str) -> str:
        self._set_parts(string)

    @property
    def tags(self) -> list[LMS_EncodedTag | LMS_DecodedTag]:
        """The list of control tags in the message."""
        return [part for part in self._parts if isinstance(part, LMS_TagBase)]

    @overload
    def append_encoded_tag(
        self, group: int, tag: int, *parameters: tuple[str] 
    ) -> None: ...

    @overload
    def append_encoded_tag(
        self, group: str, tag: str, *parameters: tuple[str]
    ) -> None: ...

    def append_encoded_tag(
        self, group: int | str, tag: int | str, *parameters: tuple[str]
    ):
        """Appends an encoded tag to the current message.

        :param group: the group name or index.
        :param tag: the group tag or index:
        :param parameters: a list of hex strings.

        message.append_encoded_tag(1, 2, "01", "00", "00", "CD")
        """
        if isinstance(group, int) and isinstance(tag, int):
            self._parts.append(LMS_EncodedTag(group, tag, parameters))
            return
        
        definition = self._config.get_definition_by_names(group, tag)
        self._parts.append(
            LMS_EncodedTag(
                definition.group_index, definition.tag_index, parameters, group, tag
            )
        )

    def append_decoded_tag(self, group_name: str, tag_name: str, **parameters: LMS_FieldMap) -> None:
        """Appends an decoded tag to the current message.

        :param group_name: the group name.
        :param tag_name: the tag name.:
        :param parameters: keyword arguments of parameters mapped to their value.

        ## Usage
        ```
        message.append_decoded_tag("Mii", "Nickname", buffer=1, type="Voice", conversion="None")
        ```
        """

        if group_name == "System":
            definition = get_system_tag(tag_name)
        else:
            definition = self._config.get_definition_by_names(group_name, tag_name)

        # The provided kwargs must match the structure defined in the config in order for value conversion to work
        converted_params = {
            param_def.name: LMS_Field(parameters[param_def.name], param_def)
            for param_def in definition.parameters
        }

        tag = LMS_DecodedTag(
            definition.group_index,
            definition.tag_index,
            group_name,
            tag_name,
            converted_params,
        )
        self._parts.append(tag)

    def append_tag_string(self, string: str) -> None:
        """Appends a tag to the current message given a string.

        :param string: the tag string."""
        if re.match(DECODED_FORMAT, string):
            tag = LMS_DecodedTag
        elif re.match(ENCODED_FORMAT, string):
            tag = LMS_EncodedTag
        else:
            raise ValueError(f"Invalid format for tag '{string}'.")

        self._parts.append(tag.from_string(string, self._config))

    def _set_parts(self, text: str) -> None:
        self._parts = []
        for part in re.split(TAG_FORMAT, text):
            if bool(re.match(TAG_FORMAT, part)):
                self.append_tag_string(part)
            else:
                self._parts.append(part)
