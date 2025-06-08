from LMS.FileIO.Stream import FileReader
from LMS.Project.Definitions.Color import LMS_Color


def read_clr1(reader: FileReader) -> list[LMS_Color]:
    count = reader.read_uint32()
    return [
        LMS_Color(
            reader.read_uint32(),
            reader.read_uint32(),
            reader.read_uint32(),
            reader.read_uint32(),
        )
        for _ in range(count)
    ]
