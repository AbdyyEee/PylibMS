from typing import Callable

from lms.common.lms_datatype import (LMS_DataType, is_bool_datatype,
                                     is_bytes_datatype, is_list_datatype,
                                     is_number_datatype)
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

    return LMS_Field(value, definition)  # type: ignore


def write_field(writer: FileWriter, field: LMS_Field) -> None:
    if is_number_datatype(field.value, field.datatype):
        write_functions: dict[LMS_DataType, Callable] = {
            LMS_DataType.UINT8: writer.write_uint8,
            LMS_DataType.INT8: writer.write_int8,
            LMS_DataType.UINT16: writer.write_uint16,
            LMS_DataType.INT16: writer.write_int16,
            LMS_DataType.UINT32: writer.write_uint32,
            LMS_DataType.INT32: writer.write_int32,
            LMS_DataType.FLOAT32: writer.write_float32,
        }
        write_functions[field.datatype](field.value)
        return

    if is_list_datatype(field.value, field.datatype):
        writer.write_uint8(field.list_items.index(field.value))
    elif is_bytes_datatype(field.value, field.datatype):
        writer.write_bytes(field.value)
    elif is_bool_datatype(field.value, field.datatype):
        writer.write_uint8(bool(field.value))
    else:
        raise ValueError(f"Unsupported datatype: {field.datatype}")
