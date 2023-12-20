from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer
from LMS.Project.MSBP import MSBP
from LMS.Common.LMS_Enum import LMS_Types

from LMS.Common.Base_Preset import base_preset
import re


class TXT2:
    """A class that represents a TXT2 block in a MSBT file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBT-File-Format#txt2-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.messages: list[str] = []
        self.preset: list[dict] = base_preset
        self.preset_set = False

    def check_tag_information(self, tag: str, group_name: str, tag_name: str) -> bool:
        """Returns if a tag is apart of a specific group and tag name.

        :param `tag`: The tag to check.
        :param `group_name`: The group name to check.
        :param `tag_name`: The tag name to check."""
        if self.tag_encoded(tag):
            return False 
        
        if not self.is_tag(tag):
            return False
        
        group_name_tag = tag[1 : tag.find(":")]
        tag_name_tag = tag[tag.find(":") + 1 : tag.rfind(":")]

        if group_name_tag == group_name and tag_name_tag == tag_name:
            return True

        return False

    def is_tag(self, message: str) -> bool:
        """Returns if a message is a tag."""
        if message.startswith("<") and message.endswith(">"):
            return True

        return False

    def tag_encoded(self, tag: str) -> bool:
        """Returns if a tag is encoded or not.

        :param `tag`: The tag to check."""
        return "." in tag[: tag.find(":")]

    def get_decoded_tag_information(self, tag: str) -> dict:
        """Returns a dictionary of all the information on a tag if its decoded.

        :param `tag`: The tag to get
        the infomation for."""
        if not self.is_tag(tag):
            return

        result = {}
        if not self.tag_encoded(tag):
            group_name = tag[1 : tag.find(":")]
            tag_name = tag[tag.find(":") + 1 : tag.rfind(":")]

            result["group_name"] = group_name
            result["tag_name"] = tag_name
            dictionary_parameters = dict(
                re.findall(r'(\w+)\s*=\s*["\']([^"\']+)["\']', tag)
            )

            result["parameters"] = dictionary_parameters
            return result

    def split_message_by_tag(self, message: str) -> list[str]:
        """Splits a message by the control tags.

        :param `message`: The message to split."""
        return re.split(r"(<[^>]+>)", message)

    def generate_preset_msbp(self, name: str, project: MSBP) -> dict:
        """Generates an editable preset .py file for use with tag decoding mode of `preset`.

        :param `name`: Name for the file.
        :param `project`: A MSBP object."""

        with open(f"{name}.py", "w+") as preset:
            preset.write("from LMS.Stream.Reader import Reader\n")
            preset.write("from LMS.Stream.Writer import Writer\n\n")
            function_dictionary = 'preset = { "data": {'

            tag_groups = project.TGG2.groups[1:]

            for group_index, group in enumerate(tag_groups, start=1):
                group_name = group["name"]
                function_dictionary += (
                    f"\n\t{group_index}: {{\n\t'name': '{group_name}', \n\t'tags': [\n"
                )
                for tag_index in group["tag_indexes"]:
                    tag = project.TAG2.tags[tag_index]
                    tag_name = tag["name"]
                    read_function_name = f"read_{group_name}_{tag_name}"
                    write_function_name = f"write_{group_name}_{tag_name}"
                    function_dictionary += f"\t\t{{'name': '{tag_name}', 'read_function' : {read_function_name}, 'write_function': {write_function_name}}},\n"

                    preset.write(f"def {read_function_name}(reader: Reader):\n")
                    preset.write("\tdata = {}\n")

                    read_function = ""
                    write_function = ""
                    for parameter_index in tag["parameter_indexes"]:
                        parameter = project.TGP2.parameters[parameter_index]
                        parameter_name = parameter["name"]
                        parameter_type = parameter["type"]

                        if parameter_type in [
                            LMS_Types.uint8_0,
                            LMS_Types.uint8_1,
                            LMS_Types.float,
                        ]:
                            read_function += (
                                f"\tdata['{parameter_name}'] = reader.read_uint8()\n"
                            )
                            write_function += (
                                f"\twriter.write_uint8(int(data['{parameter_name}']))\n"
                            )

                        elif parameter_type in [
                            LMS_Types.uint16_0,
                            LMS_Types.uint16_1,
                            LMS_Types.uint16_2,
                        ]:
                            read_function += (
                                f"\tdata['{parameter_name}'] = reader.read_uint16()\n"
                            )
                            write_function += f"\twriter.write_uint16(int(data['{parameter_name}']))\n"

                        elif parameter_type in [LMS_Types.uint32_0, LMS_Types.uint32_1]:
                            read_function += (
                                f"\tdata['{parameter_name}'] = reader.read_uint32()\n"
                            )
                            write_function += f"\twriter.write_uint32(int(data['{parameter_name}']))\n"
                        elif parameter_type == LMS_Types.string:
                            read_function += f"\tdata['{parameter_name}'] = reader.read_len_prefixed_utf16_string()\n"
                            write_function += f"\twriter.write_len_prefixed_utf16_string(data['{parameter_name}'])\n"
                        else:
                            list_items = [
                                project.TGL2.items[item_index]
                                for item_index in parameter["item_indexes"]
                            ]
                            read_function += f"\tlist_items = {list_items}\n"
                            read_function += f"\tdata['{parameter_name}'] = list_items[reader.read_uint8()]\n"
                            write_function += f"\tvalue = data['{parameter_name}']\n"
                            write_function += f"\tlist_items = {list_items}\n"
                            write_function += (
                                f"\twriter.write_uint8(list_items.index(value))\n"
                            )

                        read_function += "\n"
                        write_function += "\n"

                    read_function += "\treturn data\n"
                    write_function += "\treturn\n"
                    preset.write(read_function + "\n\n")
                    preset.write(
                        f"def {write_function_name}(writer: Writer, data: dict):\n"
                    )
                    preset.write(write_function + "\n\n")

                function_dictionary += f"\t]}},"
            function_dictionary += "}}"
            preset.write(function_dictionary)

    def set_preset(self, preset: dict) -> None:
        self.preset = {}
        self.preset["data"] = {}
        self.preset["data"] = base_preset["data"]

        for group in preset["data"]:
            self.preset["data"][group] = preset["data"][group]

        self.preset_set = True

    def read(self, reader: Reader, tag_decoding_mode: str = "default") -> None:
        """Reads the TXT2 block from a stream.

        :param `reader`: A Reader object.
        :param `tag_decoding_mode`: The mode at which to decode tags.
            * `default` uses near Kuriimu syntax `[n0.4:]`, `[n0.3:00-00-00-FF]`,
            * `preset` completely decodes it completely. `[System:PageBreak:]`, `[System:Color r="0" g="0" b="0" a="255]`.
                * A preset must be set using `TXT2.generate_preset_msbp` and set via `TXT2.set_preset`.
        """

        self.tag_decoding_mode = tag_decoding_mode

        if self.tag_decoding_mode != "default" and self.tag_decoding_mode != "preset":
            raise Exception(
                "An invalid tag decoding mode was provided, expected default or preset."
            )

        self.block.read_header(reader)
        message_count = reader.read_uint32()

        encoding = "UTF-16-LE" if reader.byte_order == "little" else "UTF-16-BE"
        tag_indicator = b"\x0E\x00" if reader.byte_order == "little" else b"\x00\x0E"

        # Read the messages
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
                    if tag_decoding_mode == "default":
                        message += self.read_encoded_control_tag(reader, encoding)
                        continue
                    message += self.read_decoded_control_tag(reader, encoding)
                else:
                    message += bytes

            self.messages.append(message.decode(encoding))

        self.block.seek_to_end(reader)

    def read_encoded_control_tag(self, reader: Reader, encoding: str) -> bytes:
        """Reads an encoded control tag from a stream.

        :param `reader`: A Reader object
        :param `encoding`: The encoding of the file."""
        group_index = reader.read_uint16()
        tag_index = reader.read_uint16()
        parameter_size = reader.read_uint16()
        end = reader.tell() + parameter_size

        if group_index in base_preset["data"]:
            group_name = base_preset["data"][group_index]["name"]
            tag_name = base_preset["data"][group_index]["tags"][tag_index]["name"]
            read_function = base_preset["data"][group_index]["tags"][tag_index][
                "read_function"
            ]
            data = read_function(reader)

            parsed_parameters = ""
            for parameter in data:
                parsed_parameters += f'{parameter}="{data[parameter]}" '

            tag = f"<{group_name}:{tag_name}: {parsed_parameters}".strip() + f">"
            reader.seek(end)
            return tag.encode(encoding)

        hex_parameters = reader.read_bytes(parameter_size).hex()
        encoded_parameters = "-".join(
            [
                hex_parameters[i] + hex_parameters[i + 1]
                for i in range(0, len(hex_parameters), 2)
            ]
        )

        return f"<n{group_index}.{tag_index}:{encoded_parameters}>".encode(encoding)

    def read_decoded_control_tag(self, reader: Reader, encoding: str) -> bytes:
        """Reads a decoded control tag from a stream.

        :param `reader`: A Reader object
        :param `encoding`: The encoding of the file."""

        start = reader.tell()
        group_index = reader.read_uint16()
        tag_index = reader.read_uint16()
        parameter_size = reader.read_uint16()
        parameter_start = reader.tell()

        end = parameter_start + parameter_size

        group_name = self.preset["data"][group_index]["name"]
        tag_name = self.preset["data"][group_index]["tags"][tag_index]["name"]
        read_function = self.preset["data"][group_index]["tags"][tag_index][
            "read_function"
        ]
        # Revert to unencoded tag if a tag isnt in the preset
        try:
            data = read_function(reader)
        except Exception:
            print(
                f"An occured while reading tag in function '{read_function.__name__}' parameter start at {parameter_start}, reverting to default."
            )
            reader.seek(start)
            return self.read_encoded_control_tag(reader, encoding)

        parsed_parameters = ""
        for parameter in data:
            parsed_parameters += f'{parameter}="{data[parameter]}" '

        tag = f"<{group_name}:{tag_name}: {parsed_parameters}".strip() + f">"
        reader.seek(end)
        return tag.encode(encoding)

    def write_encoded_control_tag(self, writer: Writer, tag: str) -> None:
        """Writes an encoded control tag to a stream.

        :param `reader`: A Reader object.
        :param `tag_data`: The tag."""
        group_index = tag[2 : tag.index(".")]
        tag_index = int(tag[tag.index(".") + 1 : tag.index(":")])

        parameters = tag[tag.rindex(":") + 1 : len(tag) - 1].split("-")
        parameter_size = len(parameters)

        # 1 indicates empty parameters due to split function returning an empty list
        if parameter_size == 1:
            parameter_size = 0

        writer.write_uint16(int(group_index))
        writer.write_uint16(int(tag_index))
        writer.write_uint16(parameter_size)

        for parameter in parameters:
            if parameter != "":
                writer.write_bytes(bytes.fromhex(parameter))

    def write_decoded_control_tag(self, writer: Writer, tag: str) -> None:
        """Writes a decoded control tag to a stream.

        :param `reader`: A Reader object.
        :param `tag_data`: The tag."""
        has_parameters = tag[tag.rfind(":") + 1] != ">"
        tag_info = self.get_decoded_tag_information(tag) if has_parameters else {}
        
        preset_groups = [group["name"] for group in self.preset["data"].values()]
        group_index = preset_groups.index(tag_info["group_name"])
        preset_tags = [entry["name"] for entry in self.preset["data"][group_index]["tags"]]
        tag_index = preset_tags.index(tag_info["tag_name"])
        
        # Start writing the tag data
        writer.write_uint16(group_index)
        writer.write_uint16(tag_index)

        size_offset = writer.tell()
        # Write 0 as placeholder for size
        writer.write_uint16(0)
        start = writer.tell()

        # Run the write function preset
        write_function = self.preset["data"][group_index]["tags"][tag_index]["write_function"]
        write_function(writer, tag_info["parameters"])

        end = writer.tell()
        size = end - start
        # Tag parameters must be of even length
        # Nintendo pads tags of uneven length with 0xCD character
        if size % 2 == 1:
            size += 1
            writer.seek(end)
            writer.write_bytes(b"\xCD")
            end += 1

        writer.seek(size_offset)
        writer.write_uint16(size)
        writer.seek(end)

    def write(self, writer: Writer) -> None:
        self.block.magic = "TXT2"
        self.block.size = 0
        self.block.write_header(writer)
        self.block.data_start = writer.tell()
        message_count = len(self.messages)
        writer.write_uint32(message_count)
        message_offset = message_count * 4 + 4

        tag_indicator = b"\x0E\x00" if writer.byte_order == "little" else b"\x00\x0E"

        encoded_messages = []
        for message in self.messages:
            split_message = self.split_message_by_tag(message)
            message_writer = Writer(b"", writer.byte_order)

            for part in split_message:
                if self.is_tag(part):
                    message_writer.write_bytes(tag_indicator)
                    
                    if self.tag_encoded(part):
                        self.write_encoded_control_tag(message_writer, part)
                        continue 

                    self.write_decoded_control_tag(message_writer, part)
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
