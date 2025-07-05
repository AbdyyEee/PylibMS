from LMS.Common.LMS_DataType import LMS_DataType
from LMS.FileIO.Stream import FileReader, FileWriter
from LMS.Message.Definitions.Field.LMS_Field import LMS_Field
from LMS.Message.Definitions.Field.LMS_FieldMap import LMS_FieldMap
from LMS.Message.Definitions.Field.Stream import read_field, write_field
from LMS.Message.Tag.LMS_Tag import LMS_DecodedTag, LMS_EncodedTag, LMS_TagBase
from LMS.Message.Tag.LMS_TagExceptions import (LMS_TagReadingError,
                                               LMS_TagWritingException)
from LMS.Message.Tag.System_Definitions import SYSTEM_GROUP
from LMS.TitleConfig.Definitions.Tags import TagConfig, TagDefinition


def read_tag(
    reader: FileReader,
    param_size: int,
    group_index: int,
    tag_index: int,
    config: TagConfig | None,
) -> LMS_EncodedTag | LMS_DecodedTag:
    end = reader.tell() + param_size

    # System tags of group 0 are always defined, ensure they are read like any other decoded tag by default
    if config is None and group_index > 0:
        parameters = _read_encoded_parameters(reader, param_size)

        if parameters is None:
            return LMS_EncodedTag(group_index, tag_index)

        return LMS_EncodedTag(group_index, tag_index, parameters)

    if group_index == 0:
        definition = SYSTEM_GROUP[tag_index]
    else:
        definition = config.get_definition_by_indexes(group_index, tag_index)

    # If the parameters were omitted from the definition but the tag still has defined parameters, add the decoded
    # names but read the tag as encoded. This is to account for encoded tags that group have tag names attatched.
    # i.e [Group:Tag 00-00-00-FF]
    if definition.parameters is None and param_size > 0:
        parameters = _read_encoded_parameters(reader, param_size)
        return LMS_EncodedTag(
            group_index,
            tag_index,
            parameters,
            definition.group_name,
            definition.tag_name,
        )
    else:
        parameters = _read_decoded_parameters(reader, definition)

    reader.seek(end)
    return LMS_DecodedTag(
        group_index, tag_index, definition.group_name, definition.tag_name, parameters
    )


def write_tag(writer: FileWriter, tag: LMS_TagBase) -> None:
    tag_indicator = b"\x0e" + (b"\x00" * (writer.encoding.width - 1))

    if writer.big_endian:
        tag_indicator = tag_indicator[::-1]

    writer.write_bytes(tag_indicator)
    writer.write_uint16(tag.group_index)
    writer.write_uint16(tag.tag_index)

    if tag.parameters is None:
        writer.write_uint16(0)
        return

    if isinstance(tag, LMS_EncodedTag):
        _write_encoded_parameters(writer, tag.parameters)
    else:
        _write_decoded_parameters(writer, tag)

    return


# --
def _read_encoded_parameters(reader: FileReader, param_size: int) -> list[str] | None:
    if param_size == 0:
        return

    hex_parameters = reader.read_bytes(param_size).hex().upper()
    encoded_parameters = [
        hex_parameters[i : i + 2] for i in range(0, len(hex_parameters), 2)
    ]
    return encoded_parameters


def _write_encoded_parameters(writer: FileWriter, parameters: list[str] | None) -> None:
    writer.write_uint16(len(parameters))
    for param in parameters:
        writer.write_bytes(bytes.fromhex(param))


def _read_decoded_parameters(
    reader: FileReader, definition: TagDefinition | None
) -> LMS_FieldMap | None:
    if definition.parameters is None:
        return

    parameters = {}
    for param in definition.parameters:
        param_offset = reader.tell()
        try:
            if param.datatype is LMS_DataType.STRING:
                value = LMS_Field(reader.read_len_string_variable_encoding(), param)
            else:
                value = read_field(reader, param)
        # There could be multiple errors related to reading, share the extra info but display the original exception
        except Exception as e:
            raise LMS_TagReadingError(
                f"An error occured reading tag '[{definition.group_name}:{definition.tag_name}]', parameter '{param.name}' at offset {param_offset}"
            ) from e

        parameters[param.name] = value
    return parameters


def _write_decoded_parameters(writer: FileWriter, tag: LMS_DecodedTag) -> None:
    param_size = 0

    # Tags are padded by a 0xCD byte if the size is not aligned to the encoding
    # This can occur before a string parameter, or at the end of the tag.
    # If a string parameter exists, then the padding will always be at the first string instance
    # first_string is a flag so that the first string can be padded correctly.
    first_string = True

    for field in tag.parameters.values():
        if field.datatype is LMS_DataType.STRING:
            param_size += 2 + len(field.value) * writer.encoding.width
        else:
            param_size += field.datatype.stream_size

    if needs_padding := param_size % 2 == 1:
        param_size += 1

    writer.write_uint16(param_size)
    for field in tag.parameters.values():
        try:
            if field.datatype is LMS_DataType.STRING:

                if first_string and needs_padding:
                    writer.write_bytes(b"\xcd")
                    first_string, needs_padding = False, False

                writer.write_len_variable_encoding_string(field.value)
            else:
                write_field(writer, field)
        except Exception as e:
            raise LMS_TagWritingException(
                f"An error occured writing tag '{tag}', parameter '{field.name}' at offset {writer.tell()}!"
            ) from e

    if needs_padding:
        writer.write_bytes(b"\xcd")
