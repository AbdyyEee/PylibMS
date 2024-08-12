from LMS.Project.MSBP import MSBP
from LMS.Common.LMS_Enum import LMS_BinaryTypes
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer

from LMS.Message.Preset_Constants import (
    RESTRICTED_GLOBALS,
    ALLOWED_ATTRIBUTES,
    SYSTEM_STRUCTURE,
)

from lupa.lua54 import LuaRuntime

import importlib.resources
import json


def filter_attribute_access(obj, attr_name, is_setting):
    if isinstance(attr_name, str) and attr_name not in ALLOWED_ATTRIBUTES:
        raise AttributeError("You cannot access this attribute.")
    return attr_name


class Preset:
    """A static class for loading and storing a preset."""

    def __init__(self, global_list: list[str] = None):
        self.lua_runtime = LuaRuntime(attribute_filter=filter_attribute_access)
        self.structure: list[dict] = [SYSTEM_STRUCTURE]

        # Load the base Preset
        with importlib.resources.open_text("LMS.Message", "System.lua") as file:
            self.base_preset = dict(self.lua_runtime.execute(file.read()))
            self.stream_functions = self.base_preset

        globals = self.lua_runtime.globals()

        restricted_globals = global_list if global_list else RESTRICTED_GLOBALS
        for name in restricted_globals:
            globals[name] = None

    def get_indexes_by_name(self, group_name: str, tag_name: str) -> tuple:
        """Get the indexes of the group and tag in the Preset.

        :param `group_name`: the name of the group.
        :param `tag_name`: the name of the tag."""
        group_index = None
        tag_index = None

        for i in self.stream_functions:
            if self.stream_functions[i].name == group_name:
                group_index = i

        for i in self.stream_functions[group_index].tags:
            if self.stream_functions[group_index].tags[i].name == tag_name:
                tag_index = i

        return group_index, tag_index

    def get_function_data(self, group: int | str, tag: int | str) -> tuple:
        """Get the table of data in a function.

        :param `group`: the name/index of the group.
        :param `tag`: the name/index of the tag."""
        if isinstance(group, str) and isinstance(tag, str):
            group, tag = self.get_indexes_by_name(group, tag)

        stream_function = self.stream_functions[group].tags[tag].stream_function

        if stream_function is None:
            return None, None, None

        result = stream_function()
        return result[1], result[2], result[3]

    def load_preset_file(self, preset_path: str) -> None:
        """Loads a preset file.

        :param `preset_path`: the path of the .lua Preset.
        """
        self.structure = [SYSTEM_STRUCTURE]
        self.stream_functions = self.base_preset

        with open(preset_path, "r") as file:
            self.stream_functions.update(dict(self.lua_runtime.execute(file.read())))

    @staticmethod
    def create_preset_file(preset_path: str, msbp: MSBP | None = None) -> None:
        """Creates a lua Preset.

        :param `preset_path`: the path to generate the Lua preset.
        :param `msbp`: a project object for a specifc game.
        """
        """Creates a preset file."""
        if msbp is None:
            structure = []
        else:
            structure = msbp.get_tag_structure()

        function_template = """
local function {name}()
{parameter_info}
    local function read(data, reader)
{read_body}    end
    local function write(data, writer)
{write_body}    end 
    return {{read, write, parameter_info}}
end
"""
        # Index function for writing the index of list ltems
        index_function = "local function index(table, value) for i, v in ipairs(table) do if v == value then return i - 1 end end end\n"

        lua_code = ["local stream_functions = {}\n\n", index_function]

        # Slice by 1 to avoid the System group
        for group in structure[1:]:
            for tag in group.tags:
                parameter_info, read_body, write_body = (
                    Preset._generate_function_bodies(tag)
                )

                lua_code.append(
                    function_template.format(
                        name=f"{group.name.lower()}_{tag.name.lower()}",
                        parameter_info=parameter_info,
                        read_body=read_body,
                        write_body=write_body,
                    )
                )

        # Build the final stream_functions table
        lua_code.append("\nstream_functions = {\n")

        for i, group in enumerate(structure[1:], start=1):
            lua_code.append(
                f"\t[{i}] = {{\n\t\tname = '{group.name}',\n\t\ttags = {{\n"
            )

            for i, tag in enumerate(group.tags):
                lua_code.append(
                    f"\t\t\t[{i}] = {{name = '{tag.name}', stream_function = {group.name.lower()}_{tag.name.lower()}}},\n"
                )

            lua_code.append("\t\t}\n\t},\n")

        lua_code.append("}\n\nreturn stream_functions")
        lua_code.insert(
            0,
            """--[[ 
   This is a preset used for parsing tags. 
   DO NOT edit any variable which are list items (tables that appear at the top of a tag function). It will lead to errors.
   Make sure you peserve parameter names when editing a function.
--]]\n\n""",
        )

        with open(preset_path, "w+") as file:
            file.truncate()
            file.write("".join(lua_code))

    def _generate_function_bodies(tag):
        info_body = ["\tlocal parameter_info = {\n"]
        read_body = []
        write_body = []

        body_template = {
            LMS_BinaryTypes.FLOAT: (
                "\t\tdata['{parameter_name}'] = reader.read_float()\n",
                "\t\twriter.write_float(tonumber(data['{parameter_name}']))\n",
            ),
            LMS_BinaryTypes.LIST_INDEX: (
                "\t\tdata['{parameter_name}'] = parameter_info['{parameter_name}'].list_items[reader.read_uint8({{lua_index=true}})]\n",
                "\t\twriter.write_uint8(index(parameter_info['{parameter_name}'].list_items, data['{parameter_name}']))\n",
            ),
            LMS_BinaryTypes.STRING: (
                "\t\tdata['{parameter_name}'] = reader.read_len_prefixed_utf16_string()\n",
                "\t\twriter.write_len_prefixed_utf16_string(data['{parameter_name}'])\n",
            ),
        }

        data_table = "\t\t{parameter_name} = {{type = {parameter_type}, list_items = {list_items}}},\n"

        for parameter in tag.parameters:
            info_body.append(
                data_table.format(
                    parameter_name=parameter.name,
                    parameter_type=parameter.type.value,
                    list_items=(
                        set(parameter.list_items) if parameter.list_items else "{}"
                    ),
                )
            )

            if parameter.type not in body_template:
                read_body.append(
                    f"\t\tdata['{parameter.name}'] = reader.read_uint{LMS_BinaryTypes._get_bits(parameter.type)}()\n"
                )
                write_body.append(
                    f"\t\twriter.write_uint{LMS_BinaryTypes._get_bits(parameter.type)}(tonumber(data['{parameter.name}']))\n"
                )
            else:
                read, write = body_template[parameter.type]
                read_body.append(read.format(parameter_name=parameter.name))
                write_body.append(write.format(parameter_name=parameter.name))

        info_body.append("}")
        return "".join(info_body), "".join(read_body), "".join(write_body)
