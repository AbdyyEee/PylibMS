from LMS.Field.LMS_DataType import LMS_DataType
from LMS.Field.LMS_Field import LMS_Field
from LMS.FileIO.Stream import FileReader, FileWriter
from LMS.TitleConfig.Definitions.Value import ValueDefinition


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
        case LMS_DataType.STRING:
            value = reader.read_uint32()
        case LMS_DataType.LIST:
            index = reader.read_uint8()
            value = definition.list_items[index]
        case LMS_DataType.BOOL:
            value = bool(reader.read_uint8())
        case LMS_DataType.BYTE:
            value = reader.read_bytes(1)

    return LMS_Field(value, definition)


def write_field(writer: FileWriter, field: LMS_Field) -> None:
    match field.datatype:
        case LMS_DataType.UINT8:
            writer.write_uint8(field.value)
        case LMS_DataType.INT8:
            writer.write_int8(field.value)
        case LMS_DataType.UINT16:
            writer.write_uint16(field.value)
        case LMS_DataType.INT16:
            writer.write_int16(field.value)
        case LMS_DataType.UINT32:
            writer.write_uint32(field.value)
        case LMS_DataType.INT32:
            writer.write_int32(field.value)
        case LMS_DataType.LIST:
            writer.write_uint8(field.list_items.index(field.value))
        case LMS_DataType.BOOL:
            writer.write_uint8(bool(field.value))
        case LMS_DataType.BYTE:
            writer.write_bytes(field.value)
