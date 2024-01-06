from LMS.Common.LMS_Block import LMS_Block
from LMS.Common.LMS_Enum import LMS_BinaryTypes
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

        # Define a string table attribute for when attributes arent decoded
        self.strings: list[str] = []

    def attributes_decoded(self) -> bool:
        """Checks if the attributes are decoded and valid, as in they are not type bytes or are empty."""
        if len(self.attributes) > 0:
            return not isinstance(self.attributes[0], bytes)
        return False

    def read_encoded_attributes(self, reader: Reader) -> None:
        """Reads encoded attributes and the string table.

        :param `reader`: A Reader object."""
        self.attributes = [
            reader.read_bytes(self.bytes_per_attribute)
            for _ in range(self.attribute_count)
        ]

        if self.block.size > self.attribute_count * self.bytes_per_attribute:
            while reader.tell() != self.block.data_start + self.block.size:
                self.strings.append(reader.read_utf16_string())

    def create_decoded_attribute(self) -> dict:
        """Adds an attribute, setting each value to the default for each type."""
        attribute = {}
        for label in self.structure:
            type = self.structure[label]["type"]
            if (
                LMS_BinaryTypes._8_bit_type(type)
                or LMS_BinaryTypes._16_bit_type()
                or LMS_BinaryTypes._32_bit_type
            ):
                attribute[label] = 0
            elif type is LMS_BinaryTypes.STRING:
                attribute[label] = ""
            else:
                attribute[label] = self.structure[label]["list_items"][0]

    def read(self, reader: Reader, msbp: MSBP = None) -> None:
        """Reads the ATR1 block from a stream.

        :param `reader`: A Reader object.
        :param `project`: A MSBP object used for decoding attributes."""

        self.block.read_header(reader)
        self.attribute_count = reader.read_uint32()
        self.bytes_per_attribute = reader.read_uint32()

        # Read the attributes
        if msbp is None or len(msbp.ALB1.labels) == 0:
            self.read_encoded_attributes(reader)
            self.block.seek_to_end(reader)
            return

        self.structure = msbp.get_attribute_structure()

        # Verify the bytes per attribute is the same as defined in the MSBP
        # This is to prevent unintended behaviour where the MSBP defines attributes
        # But a file is not accurate with those attributes
        byte_count = 0
        for label in self.structure:
            type = self.structure[label]["type"]
            if LMS_BinaryTypes._8_bit_type(type):
                byte_count += 1
            elif LMS_BinaryTypes._16_bit_type(type):
                byte_count += 2
            elif LMS_BinaryTypes._32_bit_type(type) or type is LMS_BinaryTypes.STRING:
                byte_count += 4
            else:
                byte_count += 1

        if byte_count != self.bytes_per_attribute:
            self.read_encoded_attributes(reader)
            self.block.seek_to_end(reader)
            return

        # Write the attributes
        for _ in range(self.attribute_count):
            attribute = {}
            for label in self.structure:
                type = self.structure[label]["type"]
                if LMS_BinaryTypes._8_bit_type(type):
                    attribute[label] = reader.read_uint8()
                elif LMS_BinaryTypes._16_bit_type(type):
                    attribute[label] = reader.read_uint16()
                elif LMS_BinaryTypes._32_bit_type(type):
                    attribute[label] = reader.read_uint32()
                elif type is LMS_BinaryTypes.STRING:
                    offset = self.block.data_start + reader.read_uint32()
                    last = reader.tell()
                    reader.seek(offset)
                    string = reader.read_utf16_string()
                    attribute[label] = string
                    reader.seek(last)
                else:
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

        self.bytes_per_attribute = 0
        self.attribute_count = len(self.attributes)
        writer.write_uint32(self.attribute_count)

        if not self.attributes_decoded():
            self.bytes_per_attribute = len(self.attributes[0])
            writer.write_uint32(self.bytes_per_attribute)

            for attribute in self.attributes:
                writer.write_bytes(attribute)

            string_size = 8
            for string in self.strings:
                writer.write_utf16_string(string, use_double=True)
                string_size += len(string.encode(writer.get_utf16_encoding())) + 2\

            self.block.size = self.attribute_count * self.bytes_per_attribute + string_size
            self.block.write_end_data(writer)
            return
        else:
            for label in self.structure:
                type = self.structure[label]["type"]
                if LMS_BinaryTypes._8_bit_type(type):
                    self.bytes_per_attribute += 1
                elif LMS_BinaryTypes._16_bit_type(type):
                    self.bytes_per_attribute += 2
                elif (
                    LMS_BinaryTypes._32_bit_type(type)
                    or type is LMS_BinaryTypes.STRING
                ):
                    self.bytes_per_attribute += 4
                else:
                    self.bytes_per_attribute += 1

        writer.write_uint32(self.bytes_per_attribute)
        strings = []
        string_offset = 8 + self.attribute_count * self.bytes_per_attribute
        for attribute in self.attributes:
            for label in self.structure:
                type = self.structure[label]["type"]
                if LMS_BinaryTypes._8_bit_type(type):
                    writer.write_uint8(attribute[label])
                elif LMS_BinaryTypes._16_bit_type(type):
                    writer.write_uint16(attribute[label])
                elif LMS_BinaryTypes._32_bit_type(type):
                    writer.write_uint32(attribute[label])
                elif type is LMS_BinaryTypes.STRING:
                    string = attribute[label]
                    strings.append(string)
                    writer.write_uint32(string_offset)
                    string_offset += len(string.encode(writer.get_utf16_encoding())) + 2
                else:
                    writer.write_uint8(
                        self.structure[label]["list_items"].index(
                            attribute[label])
                    )

        string_size = 8
        for string in strings:
            writer.write_utf16_string(string, use_double=True)
            string_size += len(string.encode(writer.get_utf16_encoding())) + 2

        self.block.size = self.attribute_count * self.bytes_per_attribute + string_size
        self.block.write_end_data(writer)
