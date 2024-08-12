import re
import struct
import logging

from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer
from LMS.Project.MSBP import MSBP
from LMS.Message.Preset import Preset

system_names = {0: "Ruby", 1: "Font", 2: "Size", 3: "Color", 4: "PageBreak"}


class Tag_Utility:
    """Static class used to house most tag related functions."""

    @staticmethod
    def contains_tag(message: str, group_name: str, tag_name: str) -> bool:
        """Returns if a message contains a specifc tag.

        :param `message`: the message to search.
        :param `group_name`: the group name of the tag.
        :param`tag_name`: the name of the tag."""
        for part in Tag_Utility.split_message_by_tag(message):
            if not Tag_Utility.tag_encoded(part):
                data = Tag_Utility.get_decoded_tag_information(part)
                if data["group_name"] == group_name and data["tag_name"] == tag_name:
                    return True

        return False

    @staticmethod
    def create_tag(
        group_name: str, tag_name: str, parameters: str | dict | None = None
    ) -> str:
        if isinstance(parameters, dict):
            parameters = Tag_Utility.get_str_parameter_representation(parameters)

        if parameters:
            return f"<{group_name}::{tag_name} {parameters}>"

        return f"<{group_name}::{tag_name}>"

    @staticmethod
    def get_group_and_tag_names(tag: str) -> tuple[str, str]:
        """Returns a list of the group and tag name given a tag.

        :param `tag`: The tag to get the information for."""
        result = re.search(r"<([^:]+)::([^ >]+)[^>]*>", tag)
        return (result.group(1), result.group(2))

    @staticmethod
    def has_parameters(tag: str) -> bool:
        """Returns if a tag has parameters or not.

        :param `tag`: The tag to check."""
        return True if Tag_Utility.get_dict_parameter_representation(tag) else False

    @staticmethod
    def is_tag(message: str) -> bool:
        """Returns if a message is a tag.

        :param `message`: The message to check."""
        return (
            not message.startswith("<\\")
            and message.startswith("<")
            and message.endswith(">")
        )

    @staticmethod
    def split_message_by_tag(message: str) -> tuple[str]:
        """Splits a message by the control tags.

        :param `message`: The message to split."""
        return tuple(re.split(r"(<[^>]+>)", message))

    @staticmethod
    def tag_encoded(tag: str) -> bool:
        """Returns if a tag is encoded or not.

        :param `tag`: The tag to check."""
        return "." in tag[: tag.find(":")]

    @staticmethod
    def read_tag(reader: Reader, preset: Preset) -> tuple:
        """Reads a tag from a stream, encoded or decoded.

        :param `reader`: a Reader object.
        :param `preset`: a Preset object.
        :param `msbp`: a MSBP object"""
        group_index = reader.read_uint16()
        tag_index = reader.read_uint16()

        # When the structure is a length of 1 it means that a preset was never loaded and it
        # contains just the 'System' functions. Using this check prevents reading from it
        if len(preset.structure) == 1 and group_index:
            return Tag_Utility.read_encoded_tag(reader, group_index, tag_index), None

        return Tag_Utility.read_decoded_tag(reader, preset, group_index, tag_index)

    @staticmethod
    def read_encoded_tag(reader: Reader, group_index: int, tag_index: int) -> str:
        """Reads an encoded tag from a stream.

        :param `reader`: a Reader object.
        :param `group_index`: the index of the tag group.
        :param `tag_index`: the index of the tag in the group.
        """
        parameter_size = reader.read_uint16()
        hex_parameters = reader.read_bytes(parameter_size).hex()
        encoded_parameters = "-".join(
            [
                hex_parameters[i] + hex_parameters[i + 1]
                for i in range(0, len(hex_parameters), 2)
            ]
        )
        if parameter_size == 1:
            parameter_size = 0

        return f"<n{group_index}.{tag_index}:{encoded_parameters}>"

    @staticmethod
    def read_decoded_tag(
        reader: Reader, preset: Preset, group_index: int, tag_index: int
    ) -> tuple:
        """Reads an encoded tag from a stream.

        :param `reader`: a Reader object.
        :param `preset`: a Preset object.
        :param `msbp`: a MSBP object
        :param `group_index`: the index of the tag group.
        :param `tag_index`: the index of the tag in the group.
        """
        start = reader.tell()
        parameters = {}

        read, _, parameter_info = preset.get_function_data(group_index, tag_index)

        if read is None:
            reader.seek(start)
            return Tag_Utility.read_encoded_tag(reader, group_index, tag_index), None

        group_name = preset.stream_functions[group_index].name
        tag_name = preset.stream_functions[group_index].tags[tag_index].name
        function_name = f"{group_name.lower()}_{tag_name.lower()}"

        parameter_size = reader.read_uint16()
        end = reader.tell() + parameter_size

        try:
            read(parameters, reader)
        except Exception as error:
            parameter = list(parameter_info.keys())[len(parameters)]

            error = f"An error occurred in the function '{function_name}', reading the parameter '{parameter}' at start offset {start}. {error}"
            reader.seek(start)
            return Tag_Utility.read_encoded_tag(reader, group_index, tag_index), error

        # Account for 0xCD padding
        reader.seek(end + 1 if parameter_size % 2 == 1 else end)
        return Tag_Utility.create_tag(group_name, tag_name, parameters), None

    @staticmethod
    def write_tag(writer: Writer, tag: str, preset: Preset) -> None | str:
        """Writes both encoded and decoded tags to a stream.

        :param `writer`: a Writer object.
        :param `tag`: the tag to write.
        :param `preset`: a Preset object.
        :param `msbp`: a MSBP object."""

        if Tag_Utility.tag_encoded(tag):
            return Tag_Utility.write_encoded_tag(writer, tag)

        return Tag_Utility.write_decoded_tag(writer, tag, preset)

    @staticmethod
    def write_encoded_tag(writer: Writer, tag: str) -> None:
        """Writes an encoded tag to a stream.

        :param `writer`: a Writer object.
        :param `tag`: the tag to write."""

        group_index = int(tag[2 : tag.index(".")])
        tag_index = int(tag[tag.index(".") + 1 : tag.index(":")])

        parameters = tag[tag.rindex(":") + 1 : len(tag) - 1].split("-")
        parameter_size = len(parameters)

        if parameter_size == 1:
            parameter_size = 0

        writer.write_uint16(int(group_index))
        writer.write_uint16(int(tag_index))
        writer.write_uint16(parameter_size)

        for parameter in parameters:
            if parameter:
                writer.write_bytes(bytes.fromhex(parameter))

    @staticmethod
    # It is simple to handle errors by returning a string when reading decoded tags
    def write_decoded_tag(writer: Writer, tag: str, preset: Preset) -> str | None:
        """Writes a decoded tag to a stream.

        :param `writer`: a Writer object.
        :param `tag`: the tag to write.
        :param `msbp`: a MSBP object.
        :param `preset`: a Preset object."""
        tag_info = Tag_Utility.get_decoded_tag_information(tag)

        group_index, tag_index = preset.get_indexes_by_name(
            tag_info["group_name"], tag_info["tag_name"]
        )
        write_function = preset.get_function_data(group_index, tag_index)[1]

        group_name = preset.stream_functions[group_index].name
        tag_name = preset.stream_functions[group_index].tags[tag_index].name
        function_name = f"{group_name}_{tag_name}"

        writer.write_uint16(group_index)
        writer.write_uint16(tag_index)
        size_offset = writer.tell()
        writer.write_uint16(0)
        start = writer.tell()

        try:
            write_function(tag_info["parameters"], writer)
        except Exception as exception:
            return f"An error occurred while writing the tag in the function {function_name} at start offset {start}. {exception}"

        size = writer.tell() - start

        if size % 2 == 1:
            size += 1
            writer.write_bytes(b"\xCD")

        writer.seek(size_offset)
        writer.write_uint16(size)
        writer.seek(size, 1)

    @staticmethod
    def get_decoded_tag_information(tag: str) -> dict:
        """Returns all the information of a decoded tag.

        :param `tag`: The tag to get the information for."""
        group_name, tag_name = Tag_Utility.get_group_and_tag_names(tag)

        if not Tag_Utility.has_parameters(tag):
            return {"group_name": group_name, "tag_name": tag_name, "parameters": {}}

        parameters = Tag_Utility.get_dict_parameter_representation(tag)
        return {
            "group_name": group_name,
            "tag_name": tag_name,
            "parameters": parameters,
        }

    @staticmethod
    def get_str_parameter_representation(parameters: dict) -> str:
        """Returns the parameters in a dictionary as the formatted part of a tag.

        :param `parameters`: The parameters with key being the name and the values being what is enclosed.
        """
        result = ""
        for parameter in parameters:
            result += f'{parameter}="{parameters[parameter]}" '
        return result.strip()

    @staticmethod
    def get_dict_parameter_representation(tag: str) -> dict:
        """Returns the parameters in a dictionary.

        :param `tag`: The tag to get the parameters for."""
        return dict(re.findall(r'(\w+)="([^"]*)"', tag))
