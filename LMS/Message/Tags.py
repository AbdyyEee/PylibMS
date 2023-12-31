from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer
from LMS.Project.MSBP import MSBP
from LMS.Common.LMS_Enum import LMS_BinaryTypes
import re
from bs4 import BeautifulSoup


class Tag_Utility:
    """Static class used to house most tag related functions."""

    def get_group_and_tag_names(tag: str) -> tuple[str, str]:
        """Returns a list of the group and tag name given a tag.

        :param `tag`: The tag to get the information for."""
        soup = BeautifulSoup(tag, "html.parser")
        return soup.find().name.split("::")

    @staticmethod
    def has_parameters(tag: str) -> bool:
        """Returns if a tag has parameters or not.

        :param `tag`: The tag to check."""
        soup = BeautifulSoup(tag, 'html.parser')
        data = soup.find()
        return len(data.attrs) > 0

    @staticmethod
    def is_tag(message: str) -> bool:
        """Returns if a message is a tag.

        :param `message`: The message to check."""
        if message.startswith("<") and message.endswith(">"):
            return True

        return False

    @staticmethod
    def split_message_by_tag(message: str) -> list[str]:
        """Splits a message by the control tags.

        :param `message`: The message to split."""
        return re.split(r"(<[^>]+>)", message)

    @staticmethod
    def tag_encoded(tag: str) -> bool:
        """Returns if a tag is encoded or not.

        :param `tag`: The tag to check."""
        return "." in tag[: tag.find(":")]

    @staticmethod
    def read_encoded_tag(reader: Reader) -> str:
        """Reads an encoded tag from a stream.

        :param `reader`: A Reader object."""
        group_index = reader.read_uint16()
        tag_index = reader.read_uint16()

        # As the system group is excluded when reading a MSBP, read it here so it can be caught.
        if group_index == 0:
            match tag_index:
                case 0:
                    return f'<System::Ruby rt="{reader.read_len_prefixed_utf16_string()}">'
                case 1:
                    return f'<System::Font face="{reader.read_len_prefixed_utf16_string()}">'
                case 2:
                    return f'<System::Size percent="{reader.read_uint16()}">'
                case 3:
                    return f'<System::Color r="{reader.read_uint8()}" g="{reader.read_uint8()}" b="{reader.read_uint8()}" a="{reader.read_uint8()}">'
                case 4:
                    reader.skip(2)
                    return f'<System::PageBreak>'

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
    def read_decoded_tag(reader: Reader, msbp: MSBP) -> str:
        """Reads a decoded tag from a stream given a MSBP.

        :param `reader`: A Reader object.
        :param `msbp`: A MSBP object."""
        encoding = "UTF-16-LE" if reader.byte_order == "little" else "UTF-16-BE"
        parsed_parameters = {}
        structure = msbp.get_tag_structure()

        group_index = reader.read_uint16()
        tag_index = reader.read_uint16()

        size = reader.read_uint16()
        end = reader.tell() + size

        group = structure[group_index]
        tag = group["tags"][tag_index]

        for parameter in tag["parameters"]:
            if msbp.binary._8_bit_type(parameter["type"]):
                parsed_parameters[parameter["name"]] = reader.read_uint8()
            elif msbp.binary._16_bit_type(parameter["type"]):
                parsed_parameters[parameter["name"]] = reader.read_uint16()
            elif msbp.binary._32_bit_type(parameter["type"]):
                parsed_parameters[parameter["name"]] = reader.read_uint32()
            elif parameter["type"] is LMS_BinaryTypes.STRING:
                # Check for the 0xCD byte that often prefixes strings for certain parameters
                if reader.read_bytes(1) == b"\xCD":
                    # Set the cd_predix value accordingly so when writing later on, it is accurate.
                    parameter_index = [parameter["name"] for parameter in msbp.TGP2.parameters].index(
                        parameter["name"])
                    msbp.TGP2.parameters[parameter_index]["cd_prefix"] = True
                else:
                    reader.seek(reader.tell() - 1)

                length = reader.read_uint16()
                string = reader.read_bytes(length)

                parsed_parameters[parameter["name"]] = string.decode(encoding)
                continue

            if parameter["type"] is LMS_BinaryTypes.LIST_INDEX:
                parsed_parameters[parameter["name"]
                                  ] = parameter["list_items"][reader.read_uint8()]

        # Skip CD padding
        if size % 2 == 1:
            end += 1

        reader.seek(end)
        string_parameters = Tag_Utility.get_str_parameter_representation(
            parsed_parameters)
        tag = f"<{group["name"]}::{tag["name"]} {string_parameters}>"
        return tag

    @staticmethod
    def write_encoded_control_tag(writer: Writer, tag: str) -> None:
        """Writes an encoded control tag to a stream.

        :param `reader`: A Reader object.
        :param `tag_data`: The tag."""
        group_index = tag[2: tag.index(".")]
        tag_index = int(tag[tag.index(".") + 1: tag.index(":")])

        parameters = tag[tag.rindex(":") + 1: len(tag) - 1].split("-")
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

    @staticmethod
    def write_decoded_control_tag(writer: Writer, tag: str, msbp: MSBP) -> None:
        """Writes a decoded control tag to a stream.

        :param `writer`: A Writer object.
        :param `tag`: The tag."""
        tag_info = Tag_Utility.get_decoded_tag_information(tag)
        structure = msbp.get_tag_structure()

        group_index = [group["name"].lower()
                       for group in msbp.TGG2.groups].index(tag_info["group_name"])
        tag_index = [tag["name"].lower() for tag in structure[group_index]
                     ["tags"]].index(tag_info["tag_name"])

        writer.write_uint16(group_index)
        writer.write_uint16(tag_index)
        size_offset = writer.tell()
        writer.write_uint16(0)
        start = writer.tell()

        for parameter in structure[group_index]["tags"][tag_index]["parameters"]:
            value = tag_info["parameters"][parameter["name"].lower()]
            if msbp.binary._8_bit_type(parameter["type"]):
                writer.write_uint8(int(value))
            elif msbp.binary._16_bit_type(parameter["type"]):
                writer.write_uint16(int(value))
            elif msbp.binary._32_bit_type(parameter["type"]):
                writer.write_uint32(int(value))
            elif parameter["type"] is LMS_BinaryTypes.STRING:
                if parameter["cd_prefix"]:
                    writer.write_bytes(b"\xCD")

                writer.write_len_prefixed_utf16_string(value)
                continue
            else:
                index = parameter["list_items"].index(value)
                writer.write_uint8(index)
                continue

        size = writer.tell() - start
        # Write the padding
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
            return {
                "group_name": group_name,
                "tag_name": tag_name,
                "parameters": {}
            }

        parameters = Tag_Utility.get_dict_parameter_representation(tag)
        return {
            "group_name": group_name,
            "tag_name": tag_name,
            "parameters": parameters
        }

    @staticmethod
    def get_str_parameter_representation(parameters: dict):
        """Returns the parameters in a dictionary as the formatted part of a tag.

        :param `parameters`: The parameters with key being the name and the values being what is enclosed."""
        result = ""
        for parameter in parameters:
            result += f'{parameter}="{parameters[parameter]}" '
        return result.strip()

    @staticmethod
    def get_dict_parameter_representation(tag: str):
        """Returns the parameters in a dictionary.

        :param `tag`: The tag to get the parameters for."""
        soup = BeautifulSoup(tag, 'html.parser')
        data = soup.find()
        return data.attrs
