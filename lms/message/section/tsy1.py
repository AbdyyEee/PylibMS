from lms.fileio.io import FileReader, FileWriter


def read_tsy1(reader: FileReader, message_count: int) -> list[int]:
    style_indices = []
    for _ in range(message_count):
        style_indices.append(reader.read_uint32())
    return style_indices


def write_tsy1(writer: FileWriter, style_indices: list[int]) -> None:
    for i in style_indices:
        writer.write_uint32(i)
