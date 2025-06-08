from LMS.FileIO.Stream import FileReader
from LMS.Project.Definitions.Tag import LMS_TagGroup


def read_tgg2(reader: FileReader, version: int) -> list[LMS_TagGroup]:
    group_list = []

    count = reader.read_uint32()
    for i, offset in enumerate(reader.read_offset_array(count)):
        reader.seek(offset)

        index = reader.read_uint16() if version == 4 else i

        tag_count = reader.read_uint16()
        tag_indexes = reader.read_uint16_array(tag_count)

        name = reader.read_str_variable_encoding()
        group_list.append(LMS_TagGroup(name, index, tag_indexes))

    return group_list
