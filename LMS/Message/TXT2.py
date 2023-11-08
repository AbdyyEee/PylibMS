from LMS.Common.LMS_Block import LMS_Block
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer
from LMS.Project.MSBP import MSBP
from LMS.Common.LMS_Enum import LMS_Types
import re


class TXT2:
    """A class that represents a TXT2 block in a MSBT file.

    https://github.com/kinnay/Nintendo-File-Formats/wiki/MSBT-File-Format#txt2-block"""

    def __init__(self):
        self.block: LMS_Block = LMS_Block()
        self.messages: list[str] = []
        self.preset: list[dict] = []

    def generate_preset_msbp(self, name: str, project: MSBP) -> dict:
        """Generates an editable preset .py file for use with tag decoding mode of `preset`.

        :param `name`: Name for the file.
        :param `project`: A MSBP object."""
        with open(f"{name}.py", "w+") as preset:
            preset.write("from LMS.Stream.Reader import Reader\n")
            preset.write("from LMS.Stream.Writer import Writer\n\n")
            function_dictionary = 'preset = { "data": {'

            for group_index, group in enumerate(project.TGG2.groups):
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
        self.preset = preset

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

        if self.tag_decoding_mode == "preset" and self.preset == {}:
            raise Exception(
                "Tag decoding mode of preset was provided without a preset being set!"
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

        hex_parameters = reader.read_bytes(parameter_size).hex()
        encoded_parameters = "-".join(
            [
                hex_parameters[i] + hex_parameters[i + 1]
                for i in range(0, len(hex_parameters), 2)
            ]
        )

        return f"[n{group_index}.{tag_index}:{encoded_parameters}]".encode(encoding)

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

        tag = f"[{group_name}:{tag_name}: {parsed_parameters}".strip() + f"]"
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
        has_parameters = tag[tag.rfind(":") + 1] != "]"
        decoded_parameters = {}
        if has_parameters:
            # Use this RE expression to avoid spaces in quotes cause im too lazy
            string_parameters = tag[tag.rfind(":") + 2 : len(tag) - 1]
            split_parameters = re.findall('(?:".*?"|\S)+', string_parameters)

            # Parse each individual parameter
            for parameter in split_parameters:
                name = parameter[0 : parameter.index("=")]
                value = parameter[parameter.index('"') + 1 : parameter.rindex('"')]
                decoded_parameters[name] = value

        group_name = tag[1 : tag.index(":")]
        tag_name = tag[tag.index(":") + 1 : tag.rindex(":")]

        # Start writing the tag data
        for group in self.preset["data"]:
            for tag_index, tag in enumerate(self.preset["data"][group]["tags"]):
                if (
                    group_name == self.preset["data"][group]["name"]
                    and tag["name"] == tag_name
                ):
                    writer.write_uint16(group)
                    writer.write_uint16(tag_index)

                    size_offset = writer.tell()
                    # Write 0 as placeholder for size
                    writer.write_uint16(0)
                    start = writer.tell()
                    # Run the write function preset
                    tag["write_function"](writer, decoded_parameters)

                    end = writer.tell()
                    size = end - start

        # Tags must be even size, padded with the padding char defined in preset
        # Only write the character if the character is provided, to prevent any read errors
        # if the user wishes to re-read the file without the padded tags.
        if size % 2 == 1:
            if "padding_char" in self.preset:
                size += 1
                writer.seek(end)
                writer.write_bytes(bytes.fromhex(self.preset["padding_char"]))
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

        in_tag = False
        encoded_messages = []
        for message in self.messages:
            encoded_message = b""
            message_writer = Writer(encoded_message, writer.byte_order)
            for i in range(len(message)):
                if message[i] == "[":
                    # Start parsing the tag (in a hacky way xD)
                    in_tag = True
                    start_index = i
                    end_index = i

                    # Get the end index of the tag
                    while True:
                        end_character = message[end_index]
                        if end_character == "]":
                            end_index += 1
                            break
                        end_index += 1

                    # Get the tag data
                    tag = message[start_index:end_index]
                    is_encoded = "." in tag[: tag.find(":")]

                    tag_indicator = (
                        b"\x0E\x00"
                        if message_writer.byte_order == "little"
                        else b"\x00\x0E"
                    )
                    message_writer.write_bytes(tag_indicator)

                    # Parse parameters
                    if is_encoded:
                        self.write_encoded_control_tag(message_writer, tag)
                        continue

                    self.write_decoded_control_tag(message_writer, tag)

                    i += end_index
                elif message[i] == "]":
                    in_tag = False
                else:
                    if in_tag:
                        continue
                    message_writer.write_utf16_string(message[i])

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
