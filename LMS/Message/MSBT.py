from LMS.Common.LMS_FileInfo import LMS_FileInfo
from LMS.Message.MSBTEntry import MSBTEntry


class MSBT:
    """A Class that represents a MSBT file.

    https://nintendo-formats.com/libs/lms/msbt.html."""

    def __init__(self, info: LMS_FileInfo):
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

    @property
    def info(self) -> LMS_FileInfo:
        """The file info for the MSBT instance."""
        return self._info

    @property
    def entries(self) -> list[MSBTEntry]:
        """The list of entries for the MSBT instance."""
        return self._entries

    def add_entry(
        self,
        name: str,
        text: str = None,
        attribute: dict[str, int | str | float | bool | bytes] = None,
        style_index: int = None,
    ) -> None:
        """Adds an entry to the MSBT instance.

        :param name: the name of the entry."""
        if name in [entry.name for entry in self.entries]:
            raise KeyError(f"The label '{name}' already exists!")

        self._entries.append(MSBTEntry(name, text, attribute, style_index))

    def get_entry(self, name: str) -> MSBTEntry:
        """Retrieves an entry given it's name.

        :param name: the name of the entry."""
        for entry in self._entries:
            if name == entry.name:
                return entry

        raise KeyError(f"The label '{name}' does not exist!")
