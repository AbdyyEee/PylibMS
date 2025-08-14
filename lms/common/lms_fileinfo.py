from dataclasses import dataclass, field

from lms.fileio.encoding import FileEncoding


@dataclass(frozen=True)
class LMS_FileInfo:
    is_big_endian: bool = False
    encoding: FileEncoding = FileEncoding.UTF16
    version: int = 3
    section_count: int = 2
