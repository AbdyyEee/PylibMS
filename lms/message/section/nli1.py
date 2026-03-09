from lms.fileio.io import FileReader, FileWriter


def read_nli1(reader: FileReader) -> dict[int, str]:
    entry_count = reader.read_uint32()

    labels = {}
    for _ in range(entry_count):
        label = str(reader.read_uint32())
        index = reader.read_uint32()
        labels[index] = label

    return labels


def write_nli1(writer: FileWriter, labels: list[str]) -> None:
    label_count = len(labels)
    writer.write_uint32(label_count)

    for i in range(label_count):
        writer.write_uint32(int(labels[i]))
        writer.write_uint32(i)
