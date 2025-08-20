from dataclasses import dataclass

from lms.fileio.encoding import FileEncoding


@dataclass
class LMS_FileInfo:
    is_big_endian: bool = False
    encoding: FileEncoding = FileEncoding.UTF16
    version: int = 3
    section_count: int = 2
