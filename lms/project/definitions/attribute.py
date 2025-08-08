from lms.common.lms_datatype import LMS_DataType


class LMS_AttributeDefinition:
    def __init__(self, datatype: LMS_DataType, offset: int, list_index: int):
        self.name: str | None = None

        self.list_items: list[str] = []

        self._datatype = datatype
        self._offset = offset
        self._list_index = list_index

    @property
    def datatype(self) -> LMS_DataType:
        return self._datatype

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def list_index(self) -> int:
        return self._list_index
