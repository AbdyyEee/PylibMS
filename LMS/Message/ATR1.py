from LMS.Common.LMS_Block import LMS_Block
from LMS.Common.LMS_Enum import LMS_Types
from LMS.Project.MSBP import MSBP
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer


class ATR1:
    """A class that represents a ATR1 block in a MSBT file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBT-File-Format#atr1-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.attributes: list[dict | bytes] = []
        self.structure: dict = {}

    def create_decoded_attribute(self) -> dict:
        """Adds an attribute, setting each value to the default for each type."""
        attribute = {}
        for label in self.structure:
            type = self.structure[label]["type"]
            match type:
                case LMS_Types.uint8_0:
                    attribute[label] = 0
                case LMS_Types.uint8_1:
                    attribute[label] = 0
                case LMS_Types.float:
                    attribute[label] = 0
                case LMS_Types.uint16_0:
                    attribute[label] = 0
                case LMS_Types.uint16_1:
                    attribute[label] = 0
                case LMS_Types.uint16_2:
                    attribute[label] = 0
                case LMS_Types.uint32_0:
                    attribute[label] = 0
                case LMS_Types.uint32_1:
                    attribute[label] = 0
                case LMS_Types.string:
                    attribute[label] = ""
                case LMS_Types.list_index:
                    attribute[label] = self.structure[label]["list_items"][0]
        return attribute

    def read(self, reader: Reader, project: MSBP = None) -> None:
        """Reads the ATR1 block from a stream.

        :param `reader`: A Reader object.
        :param `project`: A MSBP object used for decoding attributes."""

        self.block.read_header(reader)
        attribute_count = reader.read_uint32()
        bytes_per_attribute = reader.read_uint32()

        # Read the attributes
        if not isinstance(project, MSBP) or len(project.ALB1.labels) == 0:
            self.attributes = [reader.read_bytes(bytes_per_attribute) for _ in range(attribute_count)]
            return
        
        # Create the structure
        for index in project.ALB1.labels:
            label = project.ALB1.labels[index]
            type = project.ATI2.attributes[index]["type"]
            offset = project.ATI2.attributes[index]["offset"]
            list_index = project.ATI2.attributes[index]["list_index"]

            self.structure[label] = {
                "type": type,
                "offset": offset,
                "list_index": list_index,
            }

            if type == LMS_Types.list_index:
                self.structure[label]["list_items"] = project.ALI2.attribute_lists[
                    list_index
                ]

        # Write the attributes
        for _ in range(attribute_count):
            attribute = {}
            for label in self.structure:
                type = self.structure[label]["type"]
                match type:
                    case LMS_Types.uint8_0:
                        attribute[label] = reader.read_uint8()
                    case LMS_Types.uint8_1:
                        attribute[label] = reader.read_uint8()
                    case LMS_Types.float:
                        attribute[label] = reader.read_uint8()
                    case LMS_Types.uint16_0:
                        attribute[label] = reader.read_uint16()
                    case LMS_Types.uint16_1:
                        attribute[label] = reader.read_uint16()
                    case LMS_Types.uint16_2:
                        attribute[label] = reader.read_uint16()
                    case LMS_Types.uint32_0:
                        attribute[label] = reader.read_uint32()
                    case LMS_Types.uint32_1:
                        attribute[label] = reader.read_uint32()
                    case LMS_Types.string:
                        offset = self.block.data_start + reader.read_uint32()
                        last = reader.tell()
                        reader.seek(offset)
                        string = reader.read_utf16_string()
                        attribute[label] = string
                        reader.seek(last)
                    case LMS_Types.list_index:
                        index = reader.read_uint8()
                        attribute[label] = self.structure[label]["list_items"][index]

            self.attributes.append(attribute)

        self.block.seek_to_end(reader)

    def write(self, writer: Writer):
        """Writes the ATR1 block to a stream.

        :param `reader`: A Reader object.
        """
        self.block.magic = "ATR1"
        self.block.write_header(writer)
        self.block.data_start = writer.tell()

        bytes_per_attribute = 0
        attribute_count = len(self.attributes)
        writer.write_uint32(attribute_count)

        # If an error occurs trying to get length, there are no attributes
        try:
            attribute = self.attributes[0]
        except IndexError:
            attribute = None 
            bytes_per_attribute = 0
     
        if isinstance(attribute, bytes):
            bytes_per_attribute = len(attribute)
        else:
            for label in self.structure:
                type = self.structure[label]["type"]
                match type:
                    case LMS_Types.uint8_0:
                        bytes_per_attribute += 1
                    case LMS_Types.uint8_1:
                        bytes_per_attribute += 1
                    case LMS_Types.float:
                        bytes_per_attribute += 1
                    case LMS_Types.uint16_0:
                        bytes_per_attribute += 2
                    case LMS_Types.uint16_1:
                        bytes_per_attribute += 2
                    case LMS_Types.uint16_2:
                        bytes_per_attribute += 2
                    case LMS_Types.uint32_0:
                        bytes_per_attribute += 4
                    case LMS_Types.uint32_1:
                        bytes_per_attribute += 4
                    case LMS_Types.string:
                        bytes_per_attribute += 4
                    case LMS_Types.list_index:
                        bytes_per_attribute += 1

        writer.write_uint32(bytes_per_attribute)

        # Verify each attribute is type bytes meaning to write the raw parameters
        if all(isinstance(attribute, bytes) for attribute in self.attributes):
            for attribute in self.attributes:
                writer.write_bytes(attribute)

            self.block.size = 8 + attribute_count * bytes_per_attribute
            self.block.write_end_data(writer)
            return

        # Get the bytes_per_attribute
        strings = []
        string_offset = 8 + attribute_count * bytes_per_attribute
        for attribute in self.attributes:
            for label in self.structure:
                type = self.structure[label]["type"]
                match type:
                    case LMS_Types.uint8_0:
                        writer.write_uint8(attribute[label])
                    case LMS_Types.uint8_1:
                        writer.write_uint8(attribute[label])
                    case LMS_Types.float:
                        writer.write_uint8(attribute[label])
                    case LMS_Types.uint16_0:
                        writer.write_uint16(attribute[label])
                    case LMS_Types.uint16_1:
                        writer.write_uint16(attribute[label])
                    case LMS_Types.uint16_2:
                        writer.write_uint16(attribute[label])
                    case LMS_Types.uint32_0:
                        writer.write_uint32(attribute[label])
                    case LMS_Types.uint32_1:
                        writer.write_uint32(attribute[label])
                    case LMS_Types.string:
                        string = attribute[label]
                        strings.append(string)
                        writer.write_uint32(string_offset)
                        string_offset += (
                            len(string.encode(writer.get_utf16_encoding())) + 2
                        )
                    case LMS_Types.list_index:
                        writer.write_uint8(
                            self.structure[label]["list_items"].index(attribute[label])
                        )

        string_size = 8
        for string in strings:
            writer.write_utf16_string(string, use_double=True)
            string_size += len(string.encode(writer.get_utf16_encoding())) + 2

        self.block.size = attribute_count * bytes_per_attribute + string_size
        self.block.write_end_data(writer)
