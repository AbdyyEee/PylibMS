from LMS.Field.LMS_DataType import LMS_DataType
from LMS.Field.LMS_Field import LMS_DataType, LMS_Field
from LMS.Field.Stream import read_field, write_field
from LMS.FileIO.Stream import FileReader, FileWriter
from LMS.Message.Definitions.LMS_FieldMap import LMS_FieldMap
from LMS.TitleConfig.Definitions.Attributes import AttributeConfig


def read_encoded_atr1(
    reader: FileReader, section_size: int
) -> tuple[list[bytes], int, list[str]]:
    absolute_size = section_size + reader.tell()

    attribute_count = reader.read_uint32()
    size_per_attribute = reader.read_uint32()

    attributes = [reader.read_bytes(size_per_attribute) for _ in range(attribute_count)]
    string_table = None

    if section_size > 8 + size_per_attribute * attribute_count:
        string_table = reader.read_bytes(absolute_size - reader.tell())

    return (attributes, size_per_attribute, string_table)


def write_encoded_atr1(
    writer: FileWriter,
    attributes: list[bytes],
    size_per_attribute: int,
    string_table: bytes | None,
):
    writer.write_uint32(len(attributes))

    if attributes:
        writer.write_uint32(size_per_attribute)
    else:
        writer.write_uint32(0)

    for attr in attributes:
        writer.write_bytes(attr)

    if string_table is not None:
        writer.write_bytes(string_table)


def read_decoded_atr1(
    reader: FileReader, structure: AttributeConfig
) -> tuple[list[LMS_FieldMap], int, None]:
    section_start = reader.tell()

    attr_count = reader.read_uint32()
    size_per_attr = reader.read_uint32()

    attributes = []
    attr_start = reader.tell()

    for _ in range(attr_count):
        reader.seek(attr_start)

        attribute = {}
        for definition in structure.definitions:
            if definition.datatype is LMS_DataType.STRING:
                last = reader.tell() + 4
                reader.seek(section_start + reader.read_uint32())
                value = LMS_Field(reader.read_str_variable_encoding(), definition)

                reader.seek(last)
            else:
                value = read_field(reader, definition)

            attribute[definition.name] = value

        attributes.append(attribute)

        # Move to the start of the next attribute
        attr_start += size_per_attr

    return attributes, size_per_attr, None


def write_decoded_atr1(
    writer: FileWriter, attributes: list[LMS_FieldMap], size_per_attribute: int
) -> None:
    writer.write_uint32(len(attributes))
    writer.write_uint32(size_per_attribute)

    string_table = []
    string_offset = 8 + size_per_attribute * len(attributes)
    for attr in attributes:
        for field in attr.values():
            if field.datatype is not LMS_DataType.STRING:
                write_field(writer, field)
            else:
                writer.write_uint32(string_offset)
                string_offset += (
                    len(field.value) * writer.encoding.width
                ) + writer.encoding.width
                string_table.append(field.value)

    for string in string_table:
        writer.write_variable_encoding_string(string)
