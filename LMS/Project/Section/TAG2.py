from lms.fileio.stream import FileReader
from lms.project.definitions.tag import LMS_TagDefinition


def read_tag2(reader: FileReader) -> list[LMS_TagDefinition]:
    info_list = []

    count = reader.read_uint32()
    for offset in reader.read_offset_array(count):
        reader.seek(offset)

        param_count = reader.read_uint16()
        parameter_indexes = reader.read_uint16_array(param_count)
        name = reader.read_str_variable_encoding()

        info_list.append(LMS_TagDefinition(name, parameter_indexes))

    return info_list
