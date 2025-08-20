from typing import Any

from lms.common.lms_fileinfo import LMS_FileInfo
from lms.message.definitions.field.lms_field import FieldValue, LMS_FieldMap
from lms.message.definitions.lms_messagetext import LMS_MessageText
from lms.message.msbtentry import MSBTEntry
from lms.titleconfig.definitions.attribute import AttributeConfig
from lms.titleconfig.definitions.tags import TagConfig


class MSBT:
    """A class that represents a MSBT file.

    https://nintendo-formats.com/libs/lms/msbt.html."""

    def __init__(
        self,
        info: LMS_FileInfo | None = None,
        attribute_config: AttributeConfig | None = None,
        tag_config: TagConfig | None = None,
    ):
        self._info = info if info is not None else LMS_FileInfo()

        self._entries: list[MSBTEntry] = []
        self._label_map: dict[str, MSBTEntry] = {}

        self.size_per_attribute = 0

        # 101 is default for almost all games. However the value can be overriden by some games (i.e Echos of Wisdom).
        # Due to this, the slot count is set dynamically when LBL1 is read.
        self.slot_count = 101

        self.attr_string_table: bytes | None = None
        self.uses_encoded_attributes = True

        self.unsupported_sections: dict[str, bytes] = {}

        # Store the section list so that the order of any and all sections is preserved when writing
        self._section_list: list[str] = ["LBL1"]

        self._attribute_config = attribute_config
        self._tag_config = tag_config

    def __iter__(self):
        return iter(self._entries)

    @property
    def info(self) -> LMS_FileInfo:
        """The file info for the MSBT instance."""
        return self._info

    @property
    def section_list(self) -> tuple[str, ...]:
        """The list of sections with order preserved."""
        return tuple(self._section_list)

    @property
    def has_attributes(self) -> bool:
        """If the msbt contains attributs."""
        return self.section_exists("ATR1")

    @property
    def has_style_indexes(self) -> bool:
        """If the msbt contains style indexes."""
        return self.section_exists("TSY1")

    def get_entry_by_index(self, index: int) -> MSBTEntry:
        """
        Retrieves an entry given its index. Supports negative indexing.

        :param index: the index of the entry.
        """
        if not (-len(self._entries) <= index < len(self._entries)):
            raise IndexError(f"The index {index} is not a valid MSBT entry!")

        return self._entries[index]

    def get_entry_by_name(self, label: str) -> MSBTEntry:
        """
        Retrieves an entry given its name.

        :param name: the label name for the entry.
        """
        if label not in self._label_map:
            raise KeyError(f"The label '{label}' does not exist!")

        return self._label_map[label]

    def add_entry(self, entry: MSBTEntry) -> None:
        """
        Adds an entry to the MSBT instance.

        :param entry: the MSBTEntry object to add.
        """
        if entry.name in self._label_map:
            raise KeyError(f"The label '{entry.name}' already exists!")

        if self.section_exists("ATR1"):
            if entry.attribute is None:
                raise ValueError(
                    f"Entry '{entry.name}' can't be added with no attributes when attributes already exist!"
                )
        elif entry.attribute is not None:
            self._section_list.insert(1, "ATR1")
            self._info.section_count += 1

        # TXT2 will always exist so insert it at all times
        if not self.section_exists("TXT2"):
            self._section_list.insert(2, "TXT2")

        if self.section_exists("TSY1"):
            if entry.style_index is None:
                raise ValueError(
                    f"Entry '{entry.name}' can't be added with no style index when styles already exist!"
                )
        elif entry.style_index is not None:
            self._section_list.insert(3, "TSY1")
            self._info.section_count += 1

        self._entries.append(entry)
        self._label_map[entry.name] = entry

    def delete_entry(self, entry: MSBTEntry) -> None:
        """
        Removes an entry from the MSBT instance.

        :param entry: the MSBTEntry object to remove.
        """
        if entry.name not in self._label_map:
            raise KeyError(f"The entry '{entry.name}' does not exist!")

        self._entries.remove(entry)
        del self._label_map[entry.name]

    def section_exists(self, name: str) -> bool:
        """
        Determines if a section exists in the current MSBT.

        :param name: the name of the section.
        """
        return name in self._section_list
