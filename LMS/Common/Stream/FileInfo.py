from lms.common import lms_exceptions
from lms.common.lms_fileinfo import LMS_FileInfo
from lms.fileio.encoding import FileEncoding
from lms.fileio.stream import FileReader, FileWriter


def read_file_info(reader: FileReader, expected_magic: str) -> LMS_FileInfo:
    magic = reader.read_string_len(8)

    if magic != expected_magic:
        raise lms_exceptions.LMS_UnexpectedMagicError(
            f"Invalid magic!' Expected {expected_magic}', got '{magic}'."
        )

    big_endian = reader.read_bytes(2) == b"\xfe\xff"
    reader.is_big_endian = big_endian

    reader.skip(2)

    encoding = FileEncoding(reader.read_uint8())
    reader.encoding = encoding

    version = reader.read_uint8()
    section_count = reader.read_uint16()

    reader.skip(2)
    file_size = reader.read_uint32()

    reader.seek(0, 2)
    if file_size != reader.tell():
        raise lms_exceptions.LMS_MisalignedSizeError(f"Filesize is misaligned!")

    # Seek to the start of data
    reader.seek(0x20)

    return LMS_FileInfo(
        big_endian,
        encoding,
        version,
        section_count,
    )


def write_file_info(writer: FileWriter, magic: str, file_info: LMS_FileInfo) -> None:
    """Writes the file info to a stream.

    :param writer: a Writer object.
    :param file_info: the file_info object."""
    writer.is_big_endian = file_info.big_endian
    writer.encoding = file_info.encoding

    writer.write_string(magic)
    writer.write_bytes(b"\xff\xfe" if not file_info.big_endian else b"\xfe\xff")
    writer.write_bytes(b"\x00\x00")

    writer.write_uint8(file_info.encoding.value)
    writer.write_uint8(file_info.version)
    writer.write_uint16(file_info.section_count)

    writer.write_bytes(b"\x00\x00")
    writer.write_bytes(b"\x00" * 4)
    writer.write_bytes(b"\x00" * 10)
    writer.seek(0x20)
