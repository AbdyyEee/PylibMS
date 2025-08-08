from __future__ import annotations

from dataclasses import dataclass, field

from lms.common.lms_datatype import LMS_DataType


class LMS_TagGroup:
    def __init__(
        self,
        name: str,
        id: int,
        tag_indexes: list[int],
    ):
        self._name = name
        self._id = id
        self._tag_indexes = tag_indexes

        self.tag_definitions = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    def set_all_definitions(
        self,
        tag_definitions: list["LMS_TagDefinition"],
        parameter_definitions: list["LMS_TagParamDefinition"],
        list_items: list[list[str]],
    ) -> None:

        self.tag_definitions.extend(tag_definitions[i] for i in self._tag_indexes)
        for tag in self.tag_definitions:
            tag.param_info.extend(
                parameter_definitions[i] for i in tag.parameter_indexes
            )
            for parameter in tag.param_info:
                if parameter.datatype is LMS_DataType.LIST:
                    parameter.list_items = [
                        item for i in parameter.list_indexes for item in list_items[i]
                    ]


class LMS_TagDefinition:
    def __init__(
        self,
        name: str,
        parameter_indexes: list[int],
        parameter_definitions: list[LMS_TagParamDefinition] | None = None,
    ):
        self._name = name
        self._parameter_indexes = (
            parameter_indexes if parameter_indexes is not None else []
        )
        self.param_info = (
            parameter_definitions if parameter_definitions is not None else []
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def parameter_indexes(self) -> list[int]:
        return self._parameter_indexes


class LMS_TagParamDefinition:
    def __init__(
        self,
        name: str,
        datatype: LMS_DataType,
        list_indexes: list[int] | None = None,
    ):
        self._name = name
        self.list_items = []

        self._datatype = datatype
        self._list_indexes = list_indexes if list_indexes is not None else []

    @property
    def name(self) -> str:
        return self._name

    @property
    def datatype(self) -> LMS_DataType:
        return self._datatype

    @property
    def list_indexes(self) -> list[int]:
        return self._list_indexes
