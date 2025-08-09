from typing import Self, overload

from lms.message.definitions.field.lms_field import (LMS_Field, LMS_FieldMap,
                                                     dict_to_field_map)
from lms.message.definitions.lms_messagetext import LMS_MessageText
from lms.titleconfig.definitions.attribute import AttributeConfig
from lms.titleconfig.definitions.tags import TagConfig


class MSBTEntry:
    """A class that represents an entry in a MSBT file."""

    def __init__(
        self,
        name: str,
        message: LMS_MessageText | str | None = None,
        attribute: LMS_FieldMap | bytes | None = None,
        style_index: int | None = None,
    ):
        self.name = name

        if not isinstance(message, (LMS_MessageText, str)):
            raise TypeError(
                f"An invalid type was provided for text in entry '{name}'! Expected LMS_MessageText object or str got {type(message)}"
            )

        if message is not None:
            self._message = (
                message
                if isinstance(message, LMS_MessageText)
                else LMS_MessageText(message)
            )
        else:
            self._message = None

        if not isinstance(attribute, (dict, bytes)):
            raise TypeError(
                f"An invalid type was provided for attribute in entry '{name}'. Expected dict or bytes got {type(attribute)},"
            )

        self._attribute = attribute
        self.style_index = style_index

    @property
    def message(self) -> LMS_MessageText | None:
        """The message object for the instance."""
        return self._message

    @property
    def attribute(self) -> LMS_FieldMap | bytes | None:
        """The attribute for the instance."""
        return self._attribute

    def to_dict(self) -> dict:
        """Converts the MSBTEntry instance into a dictionary object."""
        result = {}
        result["name"] = self.name
        result["message"] = "" if self.message is None else self.message.text

        if self._attribute is not None:
            if isinstance(self._attribute, bytes):
                result["attribute"] = self._attribute.hex().upper()
            else:

                result["attribute"] = {
                    name: attr.value for name, attr in self._attribute.items()
                }

        result["style_index"] = self.style_index
        return result

    @classmethod
    def from_dict(
        cls,
        data: dict,
        attribute_conifg: AttributeConfig | None = None,
        tag_config: TagConfig | None = None,
    ) -> Self:
        """Creates a MSBTEntry from a dictionary object.

        :param data: the dictionary data.
        :param attribute_config: the config to use to import decoded attributes.
        :param tag_config: the config to use if decoded tags are included in the message.
        """
        if "message" in data:
            message = LMS_MessageText(data["message"], tag_config)

        attribute = None
        if "attribute" in data:
            attr = data["attribute"]
            if isinstance(attr, dict):
                if attribute_conifg is None:
                    raise TypeError(
                        "A valid attribute config must be provided for decoded attributes!"
                    )
                attribute = dict_to_field_map(attr, attribute_conifg.definitions)
            elif isinstance(attr, str):
                attribute = bytes.fromhex(attr)
            else:
                raise TypeError("Invalid attribute type!")

        style_index = data.get("style_index")
        return cls(data["name"], message, attribute, style_index)
