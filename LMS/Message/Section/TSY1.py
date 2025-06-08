from LMS.FileIO.Stream import FileReader, FileWriter


def read_tsy1(reader: FileReader, message_count: int) -> list[int]:
    style_indexes = []
    for _ in range(message_count):
        style_indexes.append(reader.read_uint32())
    return style_indexes


def write_tsy1(writer: FileWriter, style_indexes: list[int]) -> None:
    for i in style_indexes:
        writer.write_uint32(i)
