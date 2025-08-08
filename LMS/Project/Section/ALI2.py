from lms.fileio.stream import FileReader


def read_ali2(reader: FileReader) -> list[list[str]]:
    attr_lists = []

    count = reader.read_uint32()
    for offset in reader.read_offset_array(count):
        reader.seek(offset)

        items = []
        item_count = reader.read_uint32()
        for offset in reader.read_offset_array(item_count):
            reader.seek(offset)
            items.append(reader.read_str_variable_encoding())

        attr_lists.append(items)

    return attr_lists
