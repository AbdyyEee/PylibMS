from __future__ import annotations

from LMS.Field.LMS_DataType import LMS_DataType


class LMS_TagGroup:
    def __init__(
        self, name: str = None, index: int = None, tag_indexes: list[int] = None
    ):
        self.name = name

        self.tag_definitions: list[LMS_TagInfo] = []

        # The index may be literally set or from the given from the stream
        # The index from the stream does not always align with the total amount of groups
        # Reason why is unknown (acts as an ID of some sort?)
        self.index = index

        self._tag_indexes = tag_indexes

    @property
    def tag_indexes(self) -> list[int]:
        return self._tag_indexes


class LMS_TagInfo:
    def __init__(self, name: str = None, param_indexes: list[int] = None):
        self.name = name
        self.param_info: list[LMS_TagParamInfo] = []
        self._parameter_indexes = param_indexes

    @property
    def parameter_indexes(self) -> list[int]:
        return self._parameter_indexes


class LMS_TagParamInfo:

    def __init__(
        self,
        name: str = None,
        list_indexes: list[int] = None,
        datatype: LMS_DataType = None,
        list_items: list[str] = None,
    ):
        self.name = name
        self.list_items = list_items or []

        self._list_indexes = [] if list_indexes is None else list_indexes
        self._type = datatype

    @property
    def datatype(self) -> LMS_DataType:
        return self._type

    @property
    def list_indexes(self) -> list[int]:
        return self._list_indexes
