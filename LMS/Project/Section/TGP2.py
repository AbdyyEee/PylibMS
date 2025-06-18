from LMS.Common.LMS_DataType import LMS_DataType
from LMS.FileIO.Stream import FileReader
from LMS.Project.Definitions.Tag import LMS_TagParamInfo


def read_tgp2(reader: FileReader) -> list[LMS_TagParamInfo]:
    parameter_info = []

    count = reader.read_uint32()
    for offset in reader.read_offset_array(count):
        reader.seek(offset)

        info_type = LMS_DataType(reader.read_uint8())

        if info_type is not LMS_DataType.LIST:
            name = reader.read_str_variable_encoding()
            parameter_info.append(LMS_TagParamInfo(name, datatype=info_type))
            continue

        reader.skip(1)
        list_count = reader.read_uint16()
        list_indexes = reader.read_uint16_array(list_count)
        name = reader.read_str_variable_encoding()
        parameter_info.append(LMS_TagParamInfo(name, list_indexes, LMS_DataType.LIST))

    return parameter_info
