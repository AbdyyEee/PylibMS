from lms.common.lms_datatype import LMS_DataType
from lms.fileio.stream import FileReader
from lms.project.definitions.attribute import LMS_AttributeDefinition


def read_ati2(reader: FileReader) -> list[LMS_AttributeDefinition]:
    info_list = []
    count = reader.read_uint32()
    for _ in range(count):
        datatype = LMS_DataType(reader.read_uint8())
        reader.skip(1)

        list_index = reader.read_uint16()
        offset = reader.read_uint32()

        info_list.append(LMS_AttributeDefinition(datatype, offset, list_index))

    return info_list
