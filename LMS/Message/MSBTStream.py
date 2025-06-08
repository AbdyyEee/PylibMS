from typing import BinaryIO

from LMS.Common import LMS_Exceptions
from LMS.Common.Stream.FileInfo import read_file_info, write_file_info
from LMS.Common.Stream.Hashtable import read_labels, write_labels
from LMS.Common.Stream.Section import (read_section_data, write_section,
                                       write_unsupported_section)
from LMS.TitleConfig.Config import AttributeConfig, TagConfig
from LMS.FileIO.Stream import FileReader, FileWriter
from LMS.Message.MSBT import MSBT
from LMS.Message.MSBTEntry import MSBTEntry
from LMS.Message.Section.ATR1 import (read_decoded_atr1, read_encoded_atr1,
                                      write_decoded_atr1, write_encoded_atr1)
from LMS.Message.Section.TSY1 import read_tsy1, write_tsy1
from LMS.Message.Section.TXT2 import read_txt2, write_txt2


def read_msbt(
    stream: BinaryIO,
    attribute_config: AttributeConfig = None,
    tag_config: TagConfig = None,
) -> MSBT:
    """Reads a MSBT file from a stream.

    :param stream: a stream object.

    ## Usage
    ```
    with open(file_path, "rb") as file:
        msbt = read_msbt(file, "Game.yaml")
        ...
    ```"""
    if stream is None:
        raise ValueError("Stream must be valid!")

    reader = FileReader(stream)
    file_info = read_file_info(reader, "MsgStdBn")

    file = MSBT(file_info)

    if attribute_config is not None:
        file.encoded_attributes = False

    messages = attributes = style_indexes = None
    for magic, size in read_section_data(reader, file_info.section_count):
        match magic:
            case "LBL1":
                labels, slot_count = read_labels(reader)
                file.slot_count = slot_count
            case "ATR1":
                # Map to shared variable to make assignment cleaner
                if attribute_config is None:
                    data = read_encoded_atr1(reader, size)
                else:
                    file.encoded_attributes = False
                    data = read_decoded_atr1(reader, attribute_config)

                attributes, size_per_attribute, string_table = data
                file.size_per_attribute = size_per_attribute
                file.attr_string_table = string_table
            case "TXT2":
                messages = read_txt2(reader, file_info.encoding, tag_config)
            case "TSY1":
                style_indexes = read_tsy1(reader, len(labels))
            case _:
                file.unsupported_sections[magic] = reader.read_bytes(size)

        file.section_list.append(magic)

    for i, label in labels.items():
        text = None if messages is None else messages[i]
        attribute = None if attributes is None else attributes[i]
        style_index = None if style_indexes is None else style_indexes[i]
        file.entries.append(MSBTEntry(label, text, attribute, style_index))

    return file


def write_msbt(stream: BinaryIO, file: MSBT) -> None:
    """Writes a MSBT file to a stream.

    :param stream: the filestream.
    :param file: the MSBT file object.

    ## Usage
    ```
        with open(file_path, "wb") as file:
            write_msbt(file, msbt)
            ...
    ```
    """
    if stream is None:
        raise LMS_Exceptions.LMS_Error("Stream is not valid!")

    if not isinstance(file, MSBT):
        raise LMS_Exceptions.LMS_Error("File provided is not a MSBT.")

    writer = FileWriter(file.info.encoding)
    write_file_info(writer, "MsgStdBn", file.info)

    for section in file.section_list:
        match section:
            case "LBL1":
                labels = [entry.name for entry in file.entries]
                write_section(writer, "LBL1", write_labels, labels, file.slot_count)
            case "ATR1":
                attributes = [entry.attribute for entry in file.entries]
                if file.encoded_attributes:
                    write_section(
                        writer,
                        "ATR1",
                        write_encoded_atr1,
                        attributes,
                        file.size_per_attribute,
                        file.attr_string_table,
                    )
                else:
                    write_section(
                        writer,
                        "ATR1",
                        write_decoded_atr1,
                        attributes,
                        file.size_per_attribute,
                    )
            case "TXT2":
                messages = [entry.message for entry in file.entries]
                write_section(writer, "TXT2", write_txt2, messages)
            case "TSY1":
                style_indexes = [entry.style_index for entry in file.entries]
                write_section(writer, "TSY1", write_tsy1, style_indexes)
            case _:
                write_unsupported_section(
                    writer, section, file.unsupported_sections[section]
                )

    writer.seek(0x12)
    writer.write_uint32(writer.get_stream_size())
    stream.write(writer.get_data())
