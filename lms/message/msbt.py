from typing import overload

from lms.common.lms_fileinfo import LMS_FileInfo
from lms.message.definitions.field.lms_field import FieldValue, LMS_FieldMap
from lms.message.definitions.lms_messagetext import LMS_MessageText
from lms.message.msbtentry import MSBTEntry
from lms.titleconfig.definitions.attribute import AttributeConfig
from lms.titleconfig.definitions.tags import TagConfig


class MSBT:
    """A Class that represents a MSBT file.

    https://nintendo-formats.com/libs/lms/msbt.html."""

    def __init__(
        self,
        info: LMS_FileInfo | None = None,
        attribute_config: AttributeConfig | None = None,
        tag_config: TagConfig | None = None,
    ):
        self._info = info if info is not None else LMS_FileInfo()

        self._entries: list[MSBTEntry] = []

        self.size_per_attribute = 0

        # 101 is default for almost all games. However the value can be overriden by some games (i.e Echos of Wisdom).
        # Due to this, the slot count is set dynamically when LBL1 is read.
        self.slot_count = 101

        self.attr_string_table: list[str] | bytes | None = None
        self.uses_encoded_attributes = True

        self.unsupported_sections: dict[str, bytes] = {}

        # Default section list used for writing
        # The section order is usually fixed at LBL1 -> TXT2 -> ATR1 -> TSY1
        # However, ATR1 and TSY1 are not in the default list ince usually these are not required sections
        # The order of additional sections is preserved when reading
        self.section_list: list[str] = ["LBL1", "TXT2"]

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
        *,
        text: str | None = None,
        attribute: dict[str, FieldValue] | bytes | None = None,
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

        match attribute:
            case dict():
                if self._attribute_config is None:
                    raise ValueError(
                        "The attribute config must have been provided when reading to add decoded attributes!"
                    )
                converted_attr = LMS_FieldMap.from_dict(
                    attribute, self._attribute_config.definitions
                )
            case bytes():
                converted_attr = attribute
            case None:
                converted_attr = None
            case _:
                raise TypeError("The provided attributes are not type bytes or dict!")

        if text is not None:
            message_text = LMS_MessageText(text, self._tag_config)
        else:
            message_text = ""

        # Insert the section magics in the correct position that when writing the sections will be properly recognized
        if attribute is not None and "ATR1" not in self.section_list:
            self.section_list.insert(2, "ATR1")
            self._info.section_count += 1

        if style_index is not None and "TSY1" not in self.section_list:
            self.section_list.insert(3, "TSY1")
            self._info.section_count += 1

        self._entries.append(
            MSBTEntry(
                name,
                message=message_text,
                attribute=converted_attr,
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
