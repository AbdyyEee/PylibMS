from dataclasses import dataclass

from LMS.FileIO.Encoding import FileEncoding


@dataclass(frozen=True)
class LMS_FileInfo:
    big_endian: bool
    encoding: FileEncoding
    version: int
    section_count: int
