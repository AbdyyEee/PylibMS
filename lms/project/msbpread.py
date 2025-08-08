import os
from typing import BinaryIO

from lms.common.lms_datatype import LMS_DataType
from lms.common.stream.FileInfo import read_file_info
from lms.common.stream.Hashtable import read_labels
from lms.common.stream.Section import read_section_data
from lms.fileio.io import FileReader
from lms.project.msbp import MSBP
from lms.project.section.ali2 import read_ali2
from lms.project.section.ati2 import read_ati2
from lms.project.section.clr1 import read_clr1
from lms.project.section.string import read_strings
from lms.project.section.syl3 import read_styles
from lms.project.section.tag2 import read_tag2
from lms.project.section.tgg2 import read_tgg2
from lms.project.section.tgp2 import read_tgp2


def read_msbp_path(file_path: str) -> MSBP:
    """Reads a MSBP file from a given path.

    :param file_path: the path to the MSBP file.

    ## Usage
    ```
    msbp = read_msbp_path("path/to/file.msbp")
    ...
    ```"""
    with open(file_path, "rb") as stream:
        return read_msbp(stream)


def read_msbp(stream: BinaryIO | None) -> MSBP:
    """Reads a MSBP file from a stream.

    :param stream: a stream object.

    ## Usage
    ```
    with open(file_path, "rb") as file:
        msbp = read_msbp(file)
        ...
    ```"""
    if stream is None:
        raise ValueError("Stream must be valid!")

    reader = FileReader(stream)
    file_info = read_file_info(reader, "MsgPrjBn")

    attribute_info_list = None
    attribute_lists = None
    tag_groups = None
    tag_info_list = None
    tag_param_list = None
    styles = None
    source_list = None

    for magic, _ in read_section_data(reader, file_info.section_count):
        match magic:
            case "CLB1" | "ALB1" | "SLB1":
                # Set the name attributes of last read item
                labels, _ = read_labels(reader)
                for i in labels:
                    items[i].name = labels[i]
            case "CLR1":
                colors = read_clr1(reader)
                items = colors
            case "ATI2":
                attribute_info_list = read_ati2(reader)
                items = attribute_info_list
            case "ALI2":
                attribute_lists = read_ali2(reader)
            case "TGG2":
                tag_groups = read_tgg2(reader, file_info.version)
            case "TAG2":
                tag_info_list = read_tag2(reader)
            case "TGP2":
                tag_param_list = read_tgp2(reader)
            case "TGL2":
                list_items = read_strings(reader, False)
            case "SYL3":
                styles = read_styles(reader)
                items = styles
            case "CTI1":
                source_list = read_strings(reader, True)
            case _:
                raise ValueError(f"Unknown section magic '{magic}' in MSBP file.")

    if attribute_info_list:
        for info in attribute_info_list:
            if info.datatype is LMS_DataType.LIST:
                info.list_items = attribute_lists[info.list_index]

    if tag_groups:
        for group in tag_groups:
            group.set_all_definitions(tag_info_list, tag_param_list, list_items)

    file = MSBP(file_info, colors, attribute_info_list, tag_groups, styles, source_list)
    file.name = os.path.basename(stream.name).removesuffix(".msbp")
    return file
