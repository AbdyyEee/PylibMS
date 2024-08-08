from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer
from LMS.Project.MSBP import MSBP

from LMS.Message.Tags import Tag_Utility


class TXT2:
    """A class that represents a TXT2 block in a MSBT file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBT-File-Format#txt2-block"""

    def __init__(self):
        from LMS.Message.MSBT import MSBT

        self.msbt: MSBT = None

        self.block: LMS_Block = LMS_Block()
        self.messages: list[str] = []

        self.errors: dict[str:dict] = {}

    def read(self, reader: Reader, preset, lbl1) -> None:
        """Reads the TXT2 block from a stream.

        :param `reader`: A Reader object.
        :param `msbp`: A MSBP object used for decoding attributes and tags
        """
        self.block.read_header(reader)
        message_count = reader.read_uint32()

        encoding = reader.get_utf16_encoding()
        tag_indicator = b"\x0E\x00" if reader.byte_order == "little" else b"\x00\x0E"

        offsets = self.block.get_item_offsets(reader, message_count)

        for i, offset in enumerate(offsets):
            if i < len(offsets) - 1:
                next_offset = offsets[i + 1]
            else:
                next_offset = self.block.data_start + self.block.size

            reader.seek(offset)

            message = b""
            while reader.tell() < next_offset:
                bytes = reader.read_bytes(2)
                if bytes == tag_indicator:
                    tag, error = Tag_Utility.read_tag(reader, preset)
                    
                    if error:
                        label = lbl1.labels[i]
                        self.errors[label]["read"].append(error)
                        message += tag.encode(encoding)
                    else:
                        message += tag.encode(encoding)
                else:
                    message += bytes 

            self.messages.append(message.decode(encoding))

        

        self.block.seek_to_end(reader)

    def write(self, writer: Writer, preset, lbl1) -> None:
        """Writes the TXT2 block to a stream.

        :param `writer`: A Writer object.
        :param `msbp`: a MSBP object used for writing decoded attributes and tags.
        :param `lbl1`: a LBL1 object used for preset errors.
        """
        message_count = len(self.messages)
        self.block.write_initial_data(writer, message_count)
        message_offset = message_count * 4 + 4

        tag_indicator = b"\x0E\x00" if writer.byte_order == "little" else b"\x00\x0E"

        encoded_messages = []
        for i, message in enumerate(self.messages):
            split_message = Tag_Utility.split_message_by_tag(message)
            # Use a writer object to simplfy the encoding process
            message_writer = Writer(b"", writer.byte_order)

            for part in split_message:
                if Tag_Utility.is_tag(part):
                    message_writer.write_bytes(tag_indicator)
                    error = Tag_Utility.write_tag(message_writer, part, preset)
                    print(error)
                    if error:
                        label = lbl1.labels[i]
                        self.errors[label]["write"].append(error)
                else:
                    message_writer.write_utf16_string(part)

            encoded_messages.append(message_writer.get_data())

        size = message_count * 4 + 4
        for message in encoded_messages:
            writer.write_uint32(message_offset)
            message_offset += len(message)
            size += len(message)

        for message in encoded_messages:
            writer.write_bytes(message)

        self.block.size = size
        self.block.write_end_data(writer)
