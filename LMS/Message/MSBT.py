from LMS.Common.LMS_Binary import LMS_Binary
from LMS.Common.LMS_Enum import LMS_MessageEncoding
from LMS.Project.MSBP import MSBP

from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer

from LMS.Common.LMS_HashTable import LMS_HashTable
from LMS.Message.TXT2 import TXT2
from LMS.Message.ATR1 import ATR1



class MSBT:
    """A class that represents a Message Studio Binary Text file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBT-File-Format"""

    def __init__(self):
        self.binary: LMS_Binary = LMS_Binary()
        self.LBL1: LMS_HashTable = LMS_HashTable()
        self.ATR1: ATR1 = ATR1()
        self.TXT2: TXT2 = TXT2()

    def read(
        self, reader: Reader, msbp: MSBP = None, tag_decoding_mode: str = "default"
    ) -> None:
        """Reads a MSBT file from a stream.

        :param `reader`: A Reader object.
        :param `msbp`: A MSBP object. Used for decoding of attributes.
        :param `tag_decoding_mode`: The mode at which to decode tags.
            * `default` uses near Kuriimu syntax `<n0.4:>`, `<n0.3:00-00-00-FF>`,
            * `preset` completely decodes it `<System:PageBreak:>`, `<System:Color r="0" g="0" b="0" a="255">`.
                * A preset must be set using `TXT2.generate_preset_msbp` or a manual one that has been created.
        """
        self.binary.read_header(reader)

        lbl1_valid, lbl1_offset = self.binary.search_block_by_name(reader, "LBL1")
        atr1_valid, atr1_offset = self.binary.search_block_by_name(reader, "ATR1")
        txt2_valid, txt2_offset = self.binary.search_block_by_name(reader, "TXT2")
       
        # Read LBL1
        if lbl1_valid:
            reader.seek(lbl1_offset)
            self.LBL1.read(reader)
        else:
            self.LBL1 = None

        # Read ATR1
        if atr1_valid:
            reader.seek(atr1_offset)
            self.ATR1.read(reader, msbp)
        else:
            self.ATR1 = None

        # Read TXT2
        if txt2_valid:
            reader.seek(txt2_offset)
            self.TXT2.read(reader, tag_decoding_mode)
        else:
            self.TXT2 = None

    def write(self, writer: Writer) -> None:
        """Writes a MSBT file to a stream.

        :param `reader`: A Reader object."""
        block_count = 0

        if self.LBL1 is not None:
            block_count += 1

        if self.ATR1 is not None:
            block_count += 1
        
        if self.TXT2 is not None:
            block_count += 1

        self.binary.magic = "MsgStdBn"
        self.binary.encoding = LMS_MessageEncoding(2)
        self.binary.revision = 3
        self.binary.block_count = block_count

        self.binary.write_header(writer)
        self.LBL1.block.magic = "LBL1"
        self.ATR1.block.magic = "LBL1"
        self.TXT2.block.magic = "TXT2"

        if self.LBL1 is not None:
            self.LBL1.write(writer, 101)

        if self.ATR1 is not None:
            self.ATR1.write(writer)

        if self.TXT2 is not None:
            self.TXT2.write(writer)

        writer.seek(0, 2)
        size = writer.tell()
        writer.seek(18)
        writer.write_uint32(size)
