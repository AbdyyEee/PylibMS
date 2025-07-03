import os
from typing import BinaryIO

from LMS.Common.LMS_DataType import LMS_DataType
from LMS.Common.Stream.FileInfo import read_file_info
from LMS.Common.Stream.Hashtable import read_labels
from LMS.Common.Stream.Section import read_section_data
from LMS.FileIO.Stream import FileReader
from LMS.Project.MSBP import MSBP
from LMS.Project.Section.ALI2 import read_ali2
from LMS.Project.Section.ATI2 import read_ati2
from LMS.Project.Section.CLR1 import read_clr1
from LMS.Project.Section.String import read_strings
from LMS.Project.Section.SYL3 import read_styles
from LMS.Project.Section.TAG2 import read_tag2
from LMS.Project.Section.TGG2 import read_tgg2
from LMS.Project.Section.TGP2 import read_tgp2


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

    exist_map = {"CLB1": False, "ALB1": False, "SLB1": False}

    attribute_info_list = attribute_lists = tag_groups = tag_info_list = styles = (
        source_list
    ) = tag_param_list = None
    for magic, _ in read_section_data(reader, file_info.section_count):
        match magic:
            case "CLB1" | "ALB1" | "SLB1":
                labels, _ = read_labels(reader)
                # Set the name attributes of last read item
                for i in labels:
                    items[i].name = labels[i]
                # Set the section exists
                exist_map[magic] = True
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
                list_items = read_strings(reader, 16)
            case "SYL3":
                styles = read_styles(reader)
                items = styles
            case "CTI1":
                source_list = read_strings(reader, 32)
            case _:
                pass

    # Set all list items for attributes
    if attribute_info_list:
        for info in attribute_info_list:
            if info.datatype is LMS_DataType.LIST:
                info.list_items = attribute_lists[info.list_index]

    # Combining tag data
    if tag_groups:
        for group in tag_groups:
            group.tag_definitions = [tag_info_list[i] for i in group.tag_indexes]

            for tag in group.tag_definitions:
                tag.param_info = [tag_param_list[i] for i in tag.parameter_indexes]

                for parameter in tag.param_info:
                    parameter.list_items = [
                        list_items[i] for i in parameter.list_indexes
                    ]

    file = MSBP(file_info, colors, attribute_info_list, tag_groups, styles, source_list)
    file.name = os.path.basename(stream.name).removesuffix(".msbp")

    file.clb1_exists = exist_map["CLB1"]
    file.alb1_exists = exist_map["ALB1"]
    file.slb1_exists = exist_map["SLB1"]

    return file
