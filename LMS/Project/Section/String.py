from LMS.FileIO.Stream import FileReader


def read_strings(reader: FileReader, count_bits: int) -> list[str]:
    string_list = []

    match count_bits:
        case 16:
            count = reader.read_uint16()
            reader.skip(2)
        case 32:
            count = reader.read_uint32()

    for offset in reader.read_offset_array(count):
        reader.seek(offset)
        string_list.append(reader.read_str_variable_encoding())

    return string_list
