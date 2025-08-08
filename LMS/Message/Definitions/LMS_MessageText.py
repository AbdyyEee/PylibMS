import re

from lms.message.definitions.field.lms_field import LMS_Field
from lms.message.tag.lms_tag import (LMS_ControlTag, LMS_DecodedTag,
                                     LMS_EncodedTag)
from lms.titleconfig.config import TagConfig


class LMS_MessageText:
    """Class that represents a message text entry."""

    TAG_FORMAT = re.compile(r"(\[[^\]]+\])")

    def __init__(
        self, message: str | list[str | LMS_ControlTag], config: TagConfig | None = None
    ):
        if isinstance(message, str):
            self._set_parts(message)
        else:
            self._parts = message

        self._config = config

    def __iter__(self):
        return iter(self._parts)

    @property
    def text(self) -> str:
        """The raw text of the message."""
        text_list = []
        for part in self._parts:
            text_list.append(
                part.to_text()
                if isinstance(part, (LMS_EncodedTag, LMS_DecodedTag))
                else part
            )
        return "".join(text_list)

    @text.setter
    def text(self, string: str):
        self._set_parts(string)

    @property
    def tags(self) -> list[LMS_ControlTag]:
        """The list of control tags in the message."""
        return [
            part
            for part in self._parts
            if isinstance(part, (LMS_EncodedTag, LMS_DecodedTag))
        ]

    def append_encoded_tag(self, group_id: int, tag_index: int, *parameters: str):
        """Appends an encoded tag to the current message.

        :param group: the group name or index.
        :param tag: the group tag or index:
        :param parameters: a list of hex strings.

        ## Usage
        ```
        message.append_encoded_tag(1, 2, "01", "00", "00", "CD")
        ```
        """
        self._parts.append(LMS_EncodedTag(group_id, tag_index, list(parameters)))

    def append_decoded_tag(
        self,
        group_name: str,
        tag_name: str,
        **parameters: int | str | float | bool | bytes,
    ) -> None:
        """Appends an decoded tag to the current message.

        :param group_name: the group name.
        :param tag_name: the tag name.:
        :param parameters: keyword arguments of parameters mapped to their value.

        ## Usage
        ```
        message.append_decoded_tag("Mii", "Nickname", buffer=1, type="Voice", conversion="None")
        ```
        """
        if self._config is None:
            raise ValueError("A TitleConfig is required to append decoded tags.")

        definition = self._config.get_definition_by_names(group_name, tag_name)

        converted_params = {}
        for param_def in definition.parameters:
            converted_params[param_def.name] = LMS_Field(
                parameters[param_def.name], param_def
            )

        self._parts.append(LMS_DecodedTag(definition, converted_params))

    def append_tag_string(self, tag: str) -> None:
        """Appends a tag to the current message given a string.

        :param tag: the tag string."""
        if re.match(LMS_DecodedTag.TAG_FORMAT, tag):
            if self._config is None:
                raise ValueError("TagConfig is required to append decoded tags.")
            self._parts.append(LMS_DecodedTag.from_string(tag, self._config))
        elif re.match(LMS_EncodedTag.TAG_FORMAT, tag):
            self._parts.append(LMS_EncodedTag.from_string(tag))
        else:
            raise ValueError(f"Invalid format for tag '{tag}'.")

    def _set_parts(self, text: str) -> None:
        self._parts = []
        for part in self.TAG_FORMAT.split(text):
            if bool(re.match(self.TAG_FORMAT, part)):
                self.append_tag_string(part)
            else:
                self._parts.append(part)
