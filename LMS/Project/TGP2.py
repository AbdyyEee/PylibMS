from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader
from LMS.Common.LMS_Enum import LMS_Types


class TGP2:
    """A class that represents a TGP2 block in a MSBT file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBP-File-Format#tgp2-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.parameters: list[dict] = []

    def read(self, reader: Reader) -> None:
        """Reads the TGP2 block from a stream.

        :param `reader`: A Reader object."""
        self.block.read_header(reader)

        parameter_count = reader.read_uint16()
        reader.skip(2)
        # Read the parameters
        for offset in self.block.get_item_offsets(reader, parameter_count):
            parameter = {}
            reader.seek(offset)
            type = LMS_Types(reader.read_uint8())
            parameter["type"] = type

            if type != LMS_Types.list_index:
                parameter["name"] = reader.read_string_nt()
                self.parameters.append(parameter)
                continue

            reader.skip(1)
            list_count = reader.read_uint16()
            parameter["item_indexes"] = [
                reader.read_uint16() for _ in range(list_count)
            ]
            parameter["name"] = reader.read_string_nt()

            self.parameters.append(parameter)

        self.block.seek_to_end(reader)
