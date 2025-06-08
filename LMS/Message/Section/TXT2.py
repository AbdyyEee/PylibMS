from LMS.Config.Definitions.Tags import TagConfig
from LMS.FileIO.Encoding import FileEncoding
from LMS.FileIO.Stream import FileReader, FileWriter
from LMS.Message.Definitions.LMS_MessageText import LMS_MessageText
from LMS.Message.Tag.LMS_Tag import LMS_TagBase
from LMS.Message.Tag.Stream import read_tag, write_tag


def read_txt2(
    reader: FileReader, encoding: FileEncoding, config: TagConfig
) -> list[LMS_MessageText]:
    text_list = []
    count = reader.read_uint32()

    encoding_format = encoding.to_string_format(reader.big_endian)
    tag_indicator = b"\x0e" + (b"\x00" * (reader.encoding.width - 1))

    if reader.big_endian:
        tag_indicator = tag_indicator[::-1]

    for offset in reader.read_offset_array(count):
        reader.seek(offset)

        text, parts = b"", []
        while (data := reader.read_bytes(encoding.width)) != encoding.terminator:
            if data == tag_indicator:
                # Add all the text before the control tag
                parts.append(text.decode(encoding_format))

                # Read the tag data
                group_index = reader.read_uint16()
                tag_index = reader.read_uint16()
                param_size = reader.read_uint16()

                tag = read_tag(reader, param_size, group_index, tag_index, config)

                parts.append(tag)
                text = b""
            # TODO: Add support for closing tags
            elif data == b"\x0f":
                raise NotImplementedError(
                    "MSBT files with closing tags are unsupported at this time!"
                )
            else:
                text += data

        # Add the remaining text in case there were no control tags
        if text:
            parts.append(text.decode(encoding_format))

        message = LMS_MessageText(parts, config)
        text_list.append(message)

    return text_list


def write_txt2(writer: FileWriter, messages: list[LMS_MessageText]) -> None:
    start = writer.tell()
    writer.write_uint32(len(messages))

    offset = 4 + 4 * len(messages)
    for message in messages:
        writer.write_uint32(offset)
        next = writer.tell()

        writer.seek(start + offset)
        text_start = writer.tell()
        for part in message:
            if isinstance(part, LMS_TagBase):
                write_tag(writer, part)
            else:
                writer.write_variable_encoding_string(part, False)

        writer.write_bytes(writer.encoding.terminator)
        offset += writer.tell() - text_start
        writer.seek(next)

    # Seek to the end of the text to ensure end data can be written properly
    writer.seek(offset + start)
