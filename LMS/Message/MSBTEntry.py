from typing import Self

from LMS.Message.Definitions.Field.LMS_Field import LMS_Field
from LMS.Message.Definitions.Field.LMS_FieldMap import LMS_FieldMap
from LMS.Message.Definitions.LMS_MessageText import LMS_MessageText
from LMS.TitleConfig.Definitions.Attributes import AttributeConfig
from LMS.TitleConfig.Definitions.Tags import TagConfig


class MSBTEntry:
    """A class that represents an entry in a MSBT file."""

    def __init__(
        self,
        name: str,
        message: str | LMS_MessageText | None,
        attribute: LMS_FieldMap | bytes = None,
        style_index: int = None,
    ):
        self.name = name

        if isinstance(message, str):
            self._message = LMS_MessageText(message)
        else:
            self._message = message

        self._attribute = attribute
        self.style_index = style_index

    @property
    def message(self) -> LMS_MessageText:
        """The message object for the instance."""
        return self._message

    @property
    def attribute(self) -> LMS_FieldMap | bytes:
        """The attribute for the instance."""
        return self._attribute

    def to_dict(self) -> dict:
        """Converts the MSBTEntry instance into a dictionary object."""
        result = {"name": self.name}

        if self.message is not None:
            result["message"] = self.message.text

        if self.attribute is not None:
            if isinstance(self.attribute, bytes):
                result["attribute"] = self.attribute.hex().upper()
            else:
                result["attribute"] = {
                    name: attr.value for name, attr in self.attribute.items()
                }

        if self.style_index is not None:
            result["style_index"] = self.style_index

        return result

    @classmethod
    def from_dict(
        cls,
        data: dict,
        attribute_conifg: AttributeConfig = None,
        tag_config: TagConfig = None,
    ) -> Self:
        """Creates a MSBTEntry from a dictionary object.

        :param data: the dictionary data.
        :param attribute_config: the config to use to import decoded attributes.
        :param tag_config: the config to use if decoded tags are included in the message.
        """

        if "message" in data:
            message = LMS_MessageText(data["message"], tag_config)
        else:
            message = None

        if "attribute" in data:
            if isinstance(data["attribute"], dict):
                attribute = {
                    definition.name: LMS_Field(
                        data["attribute"][definition.name], definition
                    )
                    for definition in attribute_conifg.definitions
                }
            else:
                attribute = data["attribute"]
        else:
            attribute = None

        if "style_index" in data:
            style_index = data["style_index"]
        else:
            style_index = None

        return cls(data["name"], message, attribute, style_index)
