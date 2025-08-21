import re

from lms.message.definitions.field.lms_field import LMS_FieldMap
from lms.message.tag.lms_tag import (LMS_ControlTag, LMS_DecodedTag,
                                     LMS_EncodedTag, is_tag)
from lms.titleconfig.config import TagConfig


class LMS_MessageText:
    """Class that represents a message text entry."""

    TAG_FORMAT = re.compile(r"(\[[^]]+])")

    def __init__(
        self,
        message: str | list[str | LMS_ControlTag],
        tag_config: TagConfig | None = None,
    ):
        self._tag_config = tag_config

        if isinstance(message, str):
            self._set_parts(message)
        else:
            self._parts = message

    def __iter__(self):
        return iter(self._parts)

    @property
    def text(self) -> str:
        """The raw text of the message."""
        result = []
        for part in self._parts:
            if is_tag(part):
                result.append(part.to_text())
            else:
                result.append(part)
        return "".join(result)

    @text.setter
    def text(self, string: str) -> None:
        self._set_parts(string)

    @property
    def tags(self) -> list[LMS_ControlTag]:
        """The list of control tags in the message."""
        return [part for part in self._parts if is_tag(part)]

    def append_encoded_tag(
        self, group_id: int, tag_index: int, *parameters: str, is_closing: bool = False
    ) -> LMS_EncodedTag:
        """
        Appends an encoded tag to the current message and returns that tag.

        :param group_id: the group index.
        :param tag_index: the index of the tag in the group.
        :param parameters: args of hex strings.
        :param is_closing: whether the tag is closing or not.

        Example
        ------
        >>> message = LMS_MessageText("Text")
        >>> message.append_encoded_tag(0, 3, "00", "23", "43", "32")
        """
        if is_closing:
            tag = LMS_EncodedTag(group_id, tag_index, is_closing=True)
        else:
            tag = LMS_EncodedTag(
                group_id, tag_index, None if not parameters else list(parameters)
            )

        self._parts.append(tag)
        return tag

    def append_decoded_tag(
        self,
        group_name: str,
        tag_name: str,
        is_closing: bool = False,
        **parameters: int | str | float | bool | bytes,
    ) -> LMS_DecodedTag:
        """
        Appends a decoded tag to the current message and returns that tag.

        :param group_name: the group name.
        :param tag_name: the tag name.:
        :param is_closing: whether the tag is closing or not.
        :param parameters: keyword arguments of parameters mapped to their value.

        Example
        -------
        >>> message = LMS_MessageText("Text")
        >>> message.append_decoded_tag("Mii", "Nickname", buffer=1, type="Voice", conversion="None")
        """
        if self._tag_config is None:
            raise ValueError("A TitleConfig is required to append decoded tags.")

        definition = self._tag_config.get_definition_by_names(group_name, tag_name)

        if not parameters:
            tag = LMS_DecodedTag(definition)
        else:
            param_map = LMS_FieldMap.from_dict(parameters, definition.parameters)

            if is_closing:
                tag = LMS_DecodedTag(definition, is_closing=True)
            else:
                tag = LMS_DecodedTag(definition, param_map)

        self._parts.append(tag)
        return tag

    def append_tag_string(self, tag: str) -> LMS_ControlTag:
        """
        Appends a tag to the current message given a string.

        :param tag: the tag string.
        """
        if re.fullmatch(LMS_DecodedTag.TAG_FORMAT, tag):
            if self._tag_config is None:
                raise ValueError("TagConfig is required to append decoded tags.")
            tag_obj = LMS_DecodedTag.from_string(tag, self._tag_config)
        elif re.fullmatch(LMS_EncodedTag.TAG_FORMAT, tag):
            tag_obj = LMS_EncodedTag.from_string(tag)
        else:
            raise ValueError(f"Invalid format for tag '{tag}'.")

        self._parts.append(tag_obj)
        return tag_obj

    def _set_parts(self, text: str) -> None:
        self._parts = []
        for part in self.TAG_FORMAT.split(text):
            if bool(re.match(self.TAG_FORMAT, part)):
                self.append_tag_string(part)
            else:
                self._parts.append(part)
