from LMS.Common.LMS_DataType import LMS_DataType
from LMS.FileIO.Stream import FileReader
from LMS.Project.Definitions.Tag import LMS_TagInfo


def read_tag2(reader: FileReader) -> list[LMS_TagInfo]:
    info_list = []

    count = reader.read_uint32()
    for offset in reader.read_offset_array(count):
        reader.seek(offset)

        param_count = reader.read_uint16()
        param_indexes = reader.read_uint16_array(param_count)
        name = reader.read_str_variable_encoding()

        info_list.append(LMS_TagInfo(name, param_indexes))

    return info_list
