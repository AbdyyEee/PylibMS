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
        if len(self.attributes):
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

    def read_decoded_attributes(self, reader: Reader) -> None:
        """Reads decoded attributes and the string table.

        :param `reader`: A Reader object."""
        for _ in range(self.attribute_count):
            attribute = {}
            for label in self.structure:
                attribute_type = self.structure[label].type

                if LMS_BinaryTypes._int_type(attribute_type):
                    attribute[label] = LMS_BinaryTypes.action_based_value(
                        reader, attribute_type, action="read"
                    )
                else:
                    if attribute_type is LMS_BinaryTypes.STRING:
                        offset = self.block.data_start + reader.read_uint32()
                        last_position = reader.tell()
                        reader.seek(offset)
                        utf16_string = reader.read_utf16_string()
                        attribute[label] = utf16_string
                        reader.seek(last_position)
                    else:

                        index = reader.read_uint8()
                        attribute[label] = self.structure[label].list_items[index]

            self.attributes.append(attribute)

    def get_bytes_per_attribute(self):
        """Gets the bytes_per_attribute of the ATR1 block."""
        if not self.attributes_decoded():
            return len(self.attributes[0])
        else:
            bytes_per_attribute = 0
            for label in self.structure:
                type = self.structure[label].type
                if LMS_BinaryTypes._8_bit_type(type):
                    bytes_per_attribute += 1
                elif LMS_BinaryTypes._16_bit_type(type):
                    bytes_per_attribute += 2
                elif (
                    LMS_BinaryTypes._32_bit_type(type) or type is LMS_BinaryTypes.STRING
                ):
                    bytes_per_attribute += 4
                else:
                    bytes_per_attribute += 1
            return bytes_per_attribute

    def write_encoded_attributes(self, writer: Writer) -> None:
        """Writes the encoded attributes to a stream.

        :param `writer`: a Writer object."""
        for attribute in self.attributes:
            writer.write_bytes(attribute)

        string_size = 8
        for string in self.strings:
            writer.write_utf16_string(string, use_double=True)
            string_size += len(string.encode(writer.get_utf16_encoding())) + 2
        self.block.size = self.attribute_count * self.bytes_per_attribute + string_size
        self.block.write_end_data(writer)

    def write_decoded_attributes(self, writer: Writer) -> None:
        """Writes the decoded attributes to a stream.

        :param `writer`: a Writer object."""
        self.strings = []

        string_offset = 8 + self.attribute_count * self.bytes_per_attribute

        for attribute in self.attributes:
            for label in self.structure:

                value = attribute[label]
                type = self.structure[label].type

                if LMS_BinaryTypes._int_type(type):
                    LMS_BinaryTypes.action_based_value(writer, type, value, "write")
                else:
                    if type is LMS_BinaryTypes.STRING:
                        self.strings.append(value)
                        writer.write_uint32(string_offset)
                        string_offset += (
                            len(value.encode(writer.get_utf16_encoding())) + 2
                        )
                    else:
                        writer.write_uint8(
                            self.structure[label].list_items.index(value)
                        )

    def create_decoded_attribute(self) -> dict:
        """Adds an attribute, setting each value to the default for each type."""
        attribute = {}
        for label in self.structure:
            type = self.structure[label].type
            if LMS_BinaryTypes._get_bits(type) is not None:
                attribute[label] = 0
            elif type is LMS_BinaryTypes.STRING:
                attribute[label] = ""
            else:
                attribute[label] = self.structure[label].list_items[0]

    def read(self, reader: Reader, msbp: MSBP = None) -> None:
        """Reads the ATR1 block from a stream.

        :param `reader`: a Reader object.
        :param `project`: a MSBP object used for decoding attributes."""

        self.block.read_header(reader)
        self.attribute_count = reader.read_uint32()
        self.bytes_per_attribute = reader.read_uint32()

        # Read the attributes
        if msbp is None or not len(msbp.ALB1.labels):
            self.read_encoded_attributes(reader)
            self.block.seek_to_end(reader)
            return

        self.structure = msbp.get_attribute_structure()
        self.read_decoded_attributes(reader)

        self.block.seek_to_end(reader)

    def write(self, writer: Writer):
        """Writes the ATR1 block to a stream.

        :param `writer`: a Writer object.
        """
        self.block.magic = "ATR1"
        self.block.write_header(writer)
        self.block.data_start = writer.tell()

        self.bytes_per_attribute = 0
        self.attribute_count = len(self.attributes)
        writer.write_uint32(self.attribute_count)

        self.bytes_per_attribute = self.get_bytes_per_attribute()

        writer.write_uint32(self.bytes_per_attribute)
        if not self.attributes_decoded():
            self.write_encoded_attributes(writer)
            return

        self.write_decoded_attributes(writer)

        string_size = 8
        for string in self.strings:
            writer.write_utf16_string(string, use_double=True)
            string_size += len(string.encode(writer.get_utf16_encoding())) + 2

        self.block.size = self.attribute_count * self.bytes_per_attribute + string_size
        self.block.write_end_data(writer)
