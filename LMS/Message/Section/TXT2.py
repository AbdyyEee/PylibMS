from lms.fileio.stream import FileReader, FileWriter
from lms.message.definitions.lms_messagetext import LMS_MessageText
from lms.message.tag.io.tag_io import get_tag_indicator, read_tag, write_tag
from lms.message.tag.lms_tag import LMS_DecodedTag, LMS_EncodedTag
from lms.titleconfig.definitions.tags import TagConfig


def read_txt2(reader: FileReader, config: TagConfig | None) -> list[LMS_MessageText]:
    encoding = reader.encoding

    messages = []
    message_count = reader.read_uint32()

    encoding_format = encoding.to_string_format(reader.is_big_endian)
    tag_start, tag_close = get_tag_indicator(encoding, reader.is_big_endian)

    for offset in reader.read_offset_array(message_count):
        reader.seek(offset)

        text, parts = b"", []
        while (data := reader.read_bytes(encoding.width)) != encoding.terminator:
            is_opening_tag = data == tag_start
            is_closing_tag = data == tag_close

            if is_opening_tag or is_closing_tag:
                parts.append(text.decode(encoding_format))
                tag = read_tag(reader, config, is_closing_tag)
                parts.append(tag)
                text = b""
            else:
                text += data

        # Add the remaining text in case there were no control tags
        if text:
            parts.append(text.decode(encoding_format))

        message = LMS_MessageText(parts, config)
        messages.append(message)

    return messages


def write_txt2(writer: FileWriter, messages: list[LMS_MessageText]) -> None:
    start = writer.tell()
    offset = 4 + 4 * len(messages)
    writer.write_uint32(len(messages))

    for message in messages:
        writer.write_uint32(offset)
        next_offset = writer.tell()

        writer.seek(start + offset)
        text_start = writer.tell()

        for part in message:
            if isinstance(part, (LMS_EncodedTag, LMS_DecodedTag)):
                write_tag(writer, part)
            else:
                writer.write_variable_encoding_string(part, False)

        writer.write_bytes(writer.encoding.terminator)

        offset += writer.tell() - text_start
        writer.seek(next_offset)

    writer.seek(offset + start)
