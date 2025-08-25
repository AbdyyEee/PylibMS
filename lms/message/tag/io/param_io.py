from typing import cast

from lms.common.lms_datatype import is_string_datatype
from lms.common.lms_datatype import LMS_DataType
from lms.fileio.io import FileReader, FileWriter
from lms.message.definitions.field.io import read_field, write_field
from lms.message.definitions.field.lms_field import LMS_Field, LMS_FieldMap
from lms.message.tag.lms_tagexceptions import (
    LMS_TagReadingError,
    LMS_TagWritingException,
)
from lms.titleconfig.definitions.tags import TagDefinition

TAG_PADDING_BYTE = b"\xcd"


def read_encoded_parameters(
    reader: FileReader, parameter_size: int
) -> list[str] | None:
    hex_parameters = reader.read_bytes(parameter_size).hex().upper()
    encoded_parameters = [
        f"{hex_parameters[i : i + 2]}" for i in range(0, len(hex_parameters), 2)
    ]
    return encoded_parameters


def read_decoded_parameters(
    reader: FileReader, definition: TagDefinition
) -> LMS_FieldMap | None:
    parameters = {}
    for param in definition.parameters:
        param_offset = reader.tell()
        try:
            if param.datatype is LMS_DataType.STRING:
                value = LMS_Field(reader.read_len_string_encoded(), param)
            else:
                value = read_field(reader, param)
        except Exception as e:
            raise LMS_TagReadingError(
                f"An error occurred reading tag '[{definition.group_name}:{definition.tag_name}]', parameter '{param.name}' at offset {param_offset}"
            ) from e

        parameters[param.name] = value

    return LMS_FieldMap(parameters)


def write_encoded_parameters(writer: FileWriter, parameters: list[str]) -> None:
    writer.write_uint16(len(parameters))
    for param in parameters:
        writer.write_bytes(bytes.fromhex(param))


def write_decoded_parameters(
    writer: FileWriter, parameters: LMS_FieldMap, group_name: str, tag_name: str
) -> None:
    param_size = 0

    for field in parameters:
        if is_string_datatype(field.value, field.datatype):
            param_size += 2 + len(field.value) * writer.encoding.width
        else:
            param_size += field.datatype.stream_size

    if needs_padding := (param_size % writer.encoding.width != 0):
        param_size += 1

    writer.write_uint16(param_size)

    for field in parameters:
        try:
            if is_string_datatype(field.value, field.datatype):
                # Tags are padded by a 0xCD byte if the size is not aligned to the encoding
                # This can occur before a string parameter, or at the end of the tag.
                # If a string parameter exists, then the padding will always be at the first string instance
                if needs_padding:
                    writer.write_bytes(TAG_PADDING_BYTE)
                    needs_padding = False

                writer.write_len_encoded_string(field.value)
            else:
                write_field(writer, field)
        except Exception as e:
            raise LMS_TagWritingException(
                f"An error occurred in tag [{group_name}:{tag_name} writing parameter '{field.name}' at offset {writer.tell()}!"
            ) from e

    if needs_padding:
        writer.write_bytes(TAG_PADDING_BYTE)
