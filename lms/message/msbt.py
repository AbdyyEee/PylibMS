from typing import overload

from lms.common.lms_fileinfo import LMS_FileInfo
from lms.message.definitions.field.lms_field import LMS_FieldMap
from lms.message.definitions.lms_messagetext import LMS_MessageText
from lms.message.msbtentry import MSBTEntry
from lms.titleconfig.definitions.attribute import AttributeConfig
from lms.titleconfig.definitions.tags import TagConfig


class MSBT:
    """A Class that represents a MSBT file.

    https://nintendo-formats.com/libs/lms/msbt.html."""

    def __init__(
        self,
        info: LMS_FileInfo,
        attribute_config: AttributeConfig | None,
        tag_config: TagConfig | None,
    ):
        self._info = info

        self._entries: list[MSBTEntry] = []

        self.size_per_attribute = 0

        # 101 is default for almost all games. However the value can be overriden by some games (i.e Echos of Wisdom).
        # Due to this, the slot count is set dynamically when LBL1 is read.
        self.slot_count = 101

        self.attr_string_table: list[str] | bytes | None = None
        self.uses_encoded_attributes = True

        self.unsupported_sections: dict[str, bytes] = {}
        self.section_list: list[str] = []

        # List of unsupported sections mapped to their raw data
        self._attribute_config = attribute_config
        self._tag_config = tag_config

    def __iter__(self):
        return iter(self._entries)

    @property
    def entries(self) -> list[MSBTEntry]:
        """The list of entries for the MSBT instance."""
        return self._entries

    @property
    def info(self) -> LMS_FileInfo:
        """The file info for the MSBT instance."""
        return self._info

    @property
    def has_attributes(self) -> bool:
        """If the msbt contains attributs."""
        return self.section_exists("ATR1")

    @property
    def has_style_indexes(self) -> bool:
        """If the msbt contains style indexes."""
        return self.section_exists("TSY1")

    def section_exists(self, name: str) -> bool:
        """
        Determines if a section exists in the current MSBT.

        :param name: the name of the section.
        """
        return name in self.section_list

    def add_entry(
        self,
        name: str,
        text: str | None = None,
        attribute: dict | bytes | None = None,
        style_index: int | None = None,
    ) -> None:
        """
        Adds an entry to the MSBT instance.

        :param name: the name of the entry.
        :param text: the message text to add.
        :param attribute: the attribute data to add. can be a dictionary of data or raw bytes.
        :param style_index: the index of a style for the message.
        """
        if name in [entry.name for entry in self.entries]:
            raise KeyError(f"The label '{name}' already exists!")

        if isinstance(attribute, dict):
            if self._attribute_config is None:
                raise ValueError(
                    "The attribute config must have been provided when reading to add decoded attributes!"
                )
            converted_attribute = LMS_FieldMap.from_dict(
                attribute, self._attribute_config.definitions
            )
        else:
            converted_attribute = attribute

        if text is not None:
            message_text = LMS_MessageText(text, self._tag_config)
        else:
            message_text = ""

        self._entries.append(
            MSBTEntry(
                name,
                message=message_text,
                attribute=converted_attribute,
                style_index=style_index,
            )
        )

    def get_entry(self, name: str) -> MSBTEntry:
        """Retrieves an entry given it's name.

        :param name: the name of the entry."""
        for entry in self._entries:
            if name == entry.name:
                return entry

        raise KeyError(f"The label '{name}' does not exist!")
