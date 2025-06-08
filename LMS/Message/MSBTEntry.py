from LMS.Message.Definitions.LMS_FieldMap import LMS_FieldMap
from LMS.Message.Definitions.LMS_MessageText import LMS_MessageText


class MSBTEntry:
    """A class that represents an entry in a MSBT file."""

    def __init__(
        self,
        name: str,
        message: str | LMS_MessageText,
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
