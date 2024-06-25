from LMS.Common.LMS_Binary import LMS_Binary
from LMS.Common.LMS_HashTable import LMS_HashTable
from LMS.Common.LMS_Enum import LMS_BinaryTypes
from LMS.Stream.Reader import Reader

from LMS.Project.BaseBlock import ProjectBlock
from LMS.Project.Structure import TagGroup, Tag, TagParameter, AttributeStructure

from LMS.Project.CLR1 import CLR1
from LMS.Project.CTI1 import CTI1

from LMS.Project.ALI2 import ALI2

from LMS.Project.TGL2 import TGL2

from LMS.Project.SYL3 import SYL3


class MSBP:
    """A class that represents a Message Studio Binary Project file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format"""

    def __init__(self):
        self.binary: LMS_Binary = LMS_Binary()
        self.CLR1: CLR1 = CLR1()
        self.CLB1: LMS_HashTable = LMS_HashTable()
        self.ATI2 = ProjectBlock(AttributeStructure)
        self.ALB1: LMS_HashTable = LMS_HashTable()
        self.ALI2 = ALI2()
        self.TGG2 = ProjectBlock(TagGroup)
        self.TAG2 = ProjectBlock(Tag)
        self.TGP2 = ProjectBlock(TagParameter)
        self.TGL2 = TGL2()
        self.SYL3 = SYL3()
        self.SLB1: LMS_HashTable = LMS_HashTable()
        self.CTI1 = CTI1()

    def get_attribute_structure(self) -> dict[str,AttributeStructure]:
        """Returns a formatted dictionary of all the data in the ATI2, ALB1, ALI2 blocks."""
        if self.ALB1 is None:
            return {}
        
        structure = {self.ALB1.labels[i]: self.ATI2.data[i] for i in self.ALB1.labels}

        for label in structure:
            attribute: AttributeStructure = structure[label]
            if attribute.type is LMS_BinaryTypes.LIST_INDEX:
                attribute.list_items = self.ALI2.attribute_lists[attribute.list_index]

        return structure

    def get_tag_structure(self) -> list[TagGroup]:
        """Returns a formatted dictionary of all the data in the TGG2, TAG2, TGP2, AND TGL2 blocks."""
        structure: list[TagGroup] = [group for group in self.TGG2.data]
        
        for group in structure:
            for i in group.tag_indexes:
                tag: Tag = self.TAG2.data[i]
                group.tags.append(tag)

                tag.parameters = [self.TGP2.data[i] for i in tag.parameter_indexes]

        list_parameters: list[TagParameter] = [parameter for parameter in self.TGP2.data if parameter.type is LMS_BinaryTypes.LIST_INDEX]

        for parameter in list_parameters:
            parameter.list_items = [self.TGL2.items[i] for i in parameter.list_indexes]

        return structure

    def read(self, reader: Reader) -> None:
        """Reads a MSBP file from a stream.

        :param `reader`: A Reader object."""
        self.binary.read_header(reader)

        clr1_valid, clr1_offset = self.binary.search_block_by_name(
            reader, "CLR1")
        clb1_valid, clb1_offset = self.binary.search_block_by_name(
            reader, "CLB1")
        ati2_valid, ati2_offset = self.binary.search_block_by_name(
            reader, "ATI2")
        alb1_valid, alb1_offset = self.binary.search_block_by_name(
            reader, "ALB1")
        ali2_valid, ali2_offset = self.binary.search_block_by_name(
            reader, "ALI2")
        tgg2_valid, tgg2_offset = self.binary.search_block_by_name(
            reader, "TGG2")
        tag2_valid, tag2_offset = self.binary.search_block_by_name(
            reader, "TAG2")
        tgp2_valid, tgp2_offset = self.binary.search_block_by_name(
            reader, "TGP2")
        tgl2_valid, tgl2_offset = self.binary.search_block_by_name(
            reader, "TGL2")
        syl3_valid, syl3_offset = self.binary.search_block_by_name(
            reader, "SYL3")
        slb1_valid, slb1_offset = self.binary.search_block_by_name(
            reader, "SLB1")
        cti1_valid, cti1_offset = self.binary.search_block_by_name(
            reader, "CTI1")

        # Read CLR1
        if clr1_valid:
            reader.seek(clr1_offset)
            self.CLR1.read(reader)

        # Read CLB1
        if clb1_valid:
            reader.seek(clb1_offset)
            self.CLB1.read(reader)

        # Read ATI2
        if ati2_valid:
            reader.seek(ati2_offset)
            self.ATI2.read(reader, contains_offsets=False)

        # Read ALB1
        if alb1_valid:
            reader.seek(alb1_offset)
            self.ALB1.read(reader)

        # Read ALI2
        if ali2_valid:
            reader.seek(ali2_offset)
            self.ALI2.read(reader)

        # Read TGG2
        if tgg2_valid:
            reader.seek(tgg2_offset)
            self.TGG2.read(reader)

        # Read TAG2
        if tag2_valid:
            reader.seek(tag2_offset)
            self.TAG2.read(reader)

        # Read TGP2
        if tgp2_valid:
            reader.seek(tgp2_offset)
            self.TGP2.read(reader)

        # Read TGL2
        if tgl2_valid:
            reader.seek(tgl2_offset)
            self.TGL2.read(reader)

        # Read SYL3
        if syl3_valid:
            reader.seek(syl3_offset)
            self.SYL3.read(reader)

        # Read SLB1
        if slb1_valid:
            reader.seek(slb1_offset)
            self.SLB1.read(reader)

        # Read CTI1
        if cti1_valid:
            reader.seek(cti1_offset)
            self.CTI1.read(reader)
