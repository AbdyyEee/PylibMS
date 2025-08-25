from lms.fileio.io import FileReader


def read_strings(reader: FileReader, four_byte_count: bool) -> list[str]:
    string_list = []

    if four_byte_count:
        count = reader.read_uint32()
    else:
        count = reader.read_uint16()
        reader.skip(2)

    for offset in reader.read_offset_array(count):
        reader.seek(offset)
        string_list.append(reader.read_encoded_string())

    return string_list
