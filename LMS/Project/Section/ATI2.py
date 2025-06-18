from LMS.Common.LMS_DataType import LMS_DataType
from LMS.FileIO.Stream import FileReader
from LMS.Project.Definitions.Attribute import LMS_AttributeInfo


def read_ati2(reader: FileReader) -> list[LMS_AttributeInfo]:
    info_list = []
    count = reader.read_uint32()
    for _ in range(count):
        datatype = LMS_DataType(reader.read_uint8())
        reader.skip(1)
        list_index = reader.read_uint16()
        offset = reader.read_uint32()

        info_list.append(LMS_AttributeInfo(datatype, offset, list_index))

    return info_list
