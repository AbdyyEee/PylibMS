from typing import cast

from lms.common.lms_datatype import LMS_DataType
from lms.fileio.io import FileReader, FileWriter
from lms.message.definitions.field.lms_field import LMS_Field
from lms.titleconfig.definitions.value import ValueDefinition


def read_field(reader: FileReader, definition: ValueDefinition) -> LMS_Field:
    # String is excluded as their reading varies between tags and attributes
    match definition.datatype:
        case LMS_DataType.UINT8:
            value = reader.read_uint8()
        case LMS_DataType.UINT16:
            value = reader.read_uint16()
        case LMS_DataType.UINT32:
            value = reader.read_uint32()
        case LMS_DataType.INT8:
            value = reader.read_int8()
        case LMS_DataType.INT16:
            value = reader.read_int16()
        case LMS_DataType.INT32:
            value = reader.read_int32()
        case LMS_DataType.FLOAT32:
            value = reader.read_float32()
        case LMS_DataType.LIST:
            index = reader.read_uint8()
            value = definition.list_items[index]
        case LMS_DataType.BOOL:
            value = bool(reader.read_uint8())
        case LMS_DataType.BYTES:
            value = reader.read_bytes(1)

    return LMS_Field(value, definition)


def write_field(writer: FileWriter, field: LMS_Field) -> None:
    if isinstance(field.value, int):
        value = cast(int, field.value)

    match field.datatype:
        case LMS_DataType.UINT8:
            writer.write_uint8(value)
        case LMS_DataType.INT8:
            writer.write_int8(value)
        case LMS_DataType.UINT16:
            writer.write_uint16(value)
        case LMS_DataType.INT16:
            writer.write_int16(value)
        case LMS_DataType.UINT32:
            writer.write_uint32(value)
        case LMS_DataType.INT32:
            writer.write_int32(value)
        case LMS_DataType.LIST:
            writer.write_uint8(field.list_items.index(cast(str, field.value)))
        case LMS_DataType.BOOL:
            writer.write_uint8(bool(field.value))
        case LMS_DataType.BYTES:
            writer.write_bytes(cast(bytes, field.value))
