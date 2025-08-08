from dataclasses import dataclass

from lms.fileio.encoding import FileEncoding


@dataclass(frozen=True)
class LMS_FileInfo:
    is_big_endian: bool
    encoding: FileEncoding
    version: int
    section_count: int
