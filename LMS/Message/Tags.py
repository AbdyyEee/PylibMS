import re
import struct

from bs4 import BeautifulSoup
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer
from LMS.Project.MSBP import MSBP
from LMS.Message.Preset import Preset

system_names = {0: "Ruby", 1: "Font", 2: "Size", 3: "Color", 4: "PageBreak"}

class Tag_Utility:
    """Static class used to house most tag related functions."""

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
        soup = BeautifulSoup(tag, "html.parser")
        data = soup.find()
        return len(data.attrs) > 0

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
    def read_tag(reader: Reader, preset: Preset) -> str:
        """Reads a tag from a stream, encoded or decoded.

        :param `reader`: a Reader object.
        :param `preset`: a Preset object.
        :param `msbp`: a MSBP object"""
        group_index = reader.read_uint16()
        tag_index = reader.read_uint16()

        # When the structure is a length of 1 it means that a preset was never loaded and it
        # contains just the 'System' functions. Using this check prevents reading from it
        if len(preset.structure) == 1 and group_index:
            return Tag_Utility.read_encoded_tag(reader, group_index, tag_index)

        return Tag_Utility.read_decoded_tag(
            reader, preset, group_index, tag_index
        )

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
        return f"<n{group_index}.{tag_index}:{encoded_parameters}>"

    @staticmethod
    def read_decoded_tag(
        reader: Reader, preset: Preset, group_index: int, tag_index: int
    ) -> str:
        """Reads an encoded tag from a stream.

        :param `reader`: a Reader object.
        :param `preset`: a Preset object.
        :param `msbp`: a MSBP object
        :param `group_index`: the index of the tag group.
        :param `tag_index`: the index of the tag in the group.
        """
   
        parameters = {}
        structure = preset.structure
        
        group_name = structure[group_index]["name"]
        tag_name = structure[group_index]["tags"][tag_index]["name"]

        function_name = f"{group_name.lower()}_{tag_name.lower()}"

        start = reader.tell()
        parameter_size = reader.read_uint16()
        end = reader.tell() + parameter_size
        
        read_function = preset.stream_functions[function_name]()[1]
        try:
            read_function(parameters, reader)
        # UnicodeDecodeErrors and struct errors tend to occur in tags that read wrong.
        except (UnicodeDecodeError, struct.error) as error:
            print(f"An error occurred while reading the tag in the function {function_name} at start offset {start}. {error}")
            reader.seek(start)
            return Tag_Utility.read_encoded_tag(reader, group_index, tag_index)

        if parameter_size % 2 == 1:
            end += 1

        reader.seek(end)

        if not parameters:
            return f"<{group_name}::{tag_name}>"

        string_parameters = Tag_Utility.get_str_parameter_representation(parameters)
        return f"<{group_name}::{tag_name} {string_parameters.strip()}>"

    @staticmethod
    def write_tag(writer: Writer, tag: str, preset: Preset) -> None:
        """Writes both encoded and decoded tags to a stream.

        :param `writer`: a Writer object.
        :param `tag`: the tag to write.
        :param `preset`: a Preset object.
        :param `msbp`: a MSBP object."""

        if Tag_Utility.tag_encoded(tag):
            Tag_Utility.write_encoded_tag(writer, tag)
            return

        Tag_Utility.write_decoded_tag(writer, tag, preset)

    @staticmethod
    def write_encoded_tag(writer: Writer, tag: str) -> None:
        """Writes an encoded tag to a stream.

        :param `writer`: a Writer object.
        :param `tag`: the tag to write."""

        group_index = int(tag[2 : tag.index(".")])
        tag_index = int(tag[tag.index(".") + 1 : tag.index(":")])

        parameters = tag[tag.rindex(":") + 1 : len(tag) - 1].split("-")
        parameter_size = len(parameters)

        writer.write_uint16(int(group_index))
        writer.write_uint16(int(tag_index))
        writer.write_uint16(parameter_size)

        for parameter in parameters:
            if parameter != "":
                writer.write_bytes(bytes.fromhex(parameter))

    @staticmethod
    def write_decoded_tag(writer: Writer, tag: str, preset: Preset) -> None:
        """Writes a decoded tag to a stream.

        :param `writer`: a Writer object.
        :param `tag`: the tag to write.
        :param `msbp`: a MSBP object.
        :param `preset`: a Preset object."""
        
        tag_info = Tag_Utility.get_decoded_tag_information(tag)

        
        structure = preset.structure

        group_index = [group["name"] for group in structure].index(tag_info["group_name"])
        tag_index = [tag["name"] for tag in structure[group_index]["tags"]].index(tag_info["tag_name"])
            
        function_name = (
            f"{tag_info['group_name'].lower()}_{tag_info['tag_name'].lower()}"
        )

        writer.write_uint16(group_index)
        writer.write_uint16(tag_index)
        size_offset = writer.tell()
        writer.write_uint16(0)
        start = writer.tell()

        write_function = preset.stream_functions[function_name]()[2]
        try:
            write_function(tag_info["parameters"], writer)
        except Exception as e:
            print(
                f"An error occurred while writing the tag in the function {function_name} at start offset {start}."
            )
            return

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
