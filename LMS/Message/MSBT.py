from LMS.Common.LMS_FileInfo import LMS_FileInfo
from LMS.Message.Definitions.Field.LMS_Field import LMS_Field
from LMS.Message.Definitions.LMS_MessageText import LMS_MessageText
from LMS.Message.MSBTEntry import MSBTEntry
from LMS.TitleConfig.Definitions.Attributes import AttributeConfig
from LMS.TitleConfig.Definitions.Tags import TagConfig


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
        self.slot_count = None

        self.attr_string_table: bytes = None
        self.encoded_attributes = True

        # List of section names to preserve order
        self.section_list: list[str] = []

        # List of unsupported sections mapped to their raw data
        self.unsupported_sections: dict[str, bytes] = {}

        # Store configs so if new labels are added LMS_MessageText objects and Attributes can be made properly
        self._attribute_config = attribute_config
        self._tag_config = tag_config

    @property
    def info(self) -> LMS_FileInfo:
        """The file info for the MSBT instance."""
        return self._info

    @property
    def entries(self) -> list[MSBTEntry]:
        """The list of entries for the MSBT instance."""
        return self._entries

    def section_exists(self, name: str) -> bool:
        """Determines if a section exists in the MSBT.

        :param name: the name of the section."""
        return name in self.section_list

    def add_entry(
        self,
        name: str,
        text: str = None,
        attribute: dict[str, int | str | float | bool | bytes] | bytes = None,
        style_index: int = None,
    ) -> None:
        """Adds an entry to the MSBT instance.

        :param name: the name of the entry."""
        if name in [entry.name for entry in self.entries]:
            raise KeyError(f"The label '{name}' already exists!")

        if isinstance(attribute, dict):
            if self._attribute_config is None:
                raise ValueError(
                    "The attribute config must have been provided when reading to add decoded attributes!"
                )

            converted_attribute = {}
            for definition in self._attribute_config.definitions:
                converted_attribute[definition.name] = LMS_Field(
                    attribute[definition.name], definition
                )
        else:
            converted_attribute = attribute

        if text is not None:
            if self._tag_config is not None:
                message_text = LMS_MessageText(text, self._tag_config)
            else:
                message_text = text
        else:
            message_text = ""

        self._entries.append(
            MSBTEntry(name, message_text, converted_attribute, style_index)
        )

    def get_entry(self, name: str) -> MSBTEntry:
        """Retrieves an entry given it's name.

        :param name: the name of the entry."""
        for entry in self._entries:
            if name == entry.name:
                return entry

        raise KeyError(f"The label '{name}' does not exist!")
