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
    if isinstance(attr_name, str):
        if attr_name not in ALLOWED_ATTRIBUTES:
            raise AttributeError("You cannot access this attribute.")
        return attr_name

class Preset:
    """A static class for loading and storing a preset."""

    def __init__(self, global_list: list[str] = None):
        self.lua_runtime = LuaRuntime(attribute_filter=filter_attribute_access)
        self.structure: list[dict] = [SYSTEM_STRUCTURE]

        with importlib.resources.open_text("LMS.Message", "System.lua") as file:
            self.base_preset = dict(self.lua_runtime.execute(file.read()))
            self.stream_functions = self.base_preset

        globals = self.lua_runtime.globals()

        if global_list is not None:
            for name in global_list:
                globals[name] = None
        else:
            for name in RESTRICTED_GLOBALS:
                globals[name] = None

    @staticmethod
    def msbp_structure_to_dict(msbp: MSBP):
        # Skip System
        structure = msbp.get_tag_structure()[1:]

        result = []
        for group in structure:
            group_dict = {"name": group.name, "tags": []}

            for i, tag in enumerate(group.tags):
                group_dict["tags"].append({"name": tag.name, "parameters": []})

                for parameter in tag.parameters:
                    group_dict["tags"][i]["parameters"].append(
                        {
                            "name": parameter.name,
                            "type": parameter.type.value,
                            "list_items": parameter.list_items,
                        }
                    )

            result.append(group_dict)

        return result

    def load_preset_file(self, preset_path: str, structure_path: str) -> None:
        """Loads a preset file.

        :param `preset_path`: The path to of the lua preset.
        :param `structure_path`: The path to of the json structure.
        """
        # Reset the structure and stream_functions to just include System definitions
        self.structure = [SYSTEM_STRUCTURE]
        self.stream_functions = self.base_preset

        with open(preset_path, "r") as file:
            self.stream_functions.update(dict(self.lua_runtime.execute(file.read())))

        with open(structure_path, "r") as file:
            self.structure += json.load(file)

    @staticmethod
    def create_preset_file(preset_path: str, structure_path: str, msbp: MSBP) -> None:
        """Loads a preset file.

        :param `preset_path`: the path to create the lua preset.
        :param `structure_path`: the path to create the json structure.
        :param `msbp`: project object associated with a game.
        """
        structure = msbp.get_tag_structure()
        
        function_template = """
local function {name}()
{list_items}
    local function read(data, reader)
{read_body}    end
    local function write(data, writer)
{write_body}    end 
    return {{read, write}}
end
"""
        # Lua lacks a .index function for tables, so define a table.index method for use with list items
        # Define it without function_template as its a one liner
        index_function = "local function index(table, value) for i, v in ipairs(table) do if v == value then return i - 1 end end end\n"

        # Tags can use special characters like paranthesis which lua dislikes
        # Instead, set the functions in a list so that function names can be edited
        # and still indexed properly with the raw name
        function_names = []

        with open(f"{preset_path}", "a+") as file:
            file.write("""
--[[ 
   This is a preset used for parsing tags. 
   DO NOT edit any variable which are list items (tables that appear at the top of a tag function). It will lead to errors.
   Make sure you peserve parameter names when editing a function.
--]]
"""
            )
            file.truncate()

            file.write("local stream_functions = {}\n\n")
            file.write(index_function)

            # Slice the structure, ignoring the "System" group as it has already been defined.
            for group in structure[1:]:
                for tag in group.tags:
                    read_body = ""
                    write_body = ""
                    list_body = ""

                    name = f"{group.name.lower()}_{tag.name.lower()}"
                    function_names.append(name)

                    for parameter in tag.parameters:
                        list_items = parameter.list_items
                        if list_items:
                            list_body += (
                                f"\tlocal {parameter.name}_items = {set(list_items)}\n"
                            )

                        # Determine the action
                        match parameter.type:
                            case LMS_BinaryTypes.FLOAT:
                                read_body += f"\t\t\tdata['{parameter.name}'] = reader.read_float()\n"
                                write_body += f"\t\t\twriter.write_float(tonumber(data['{parameter.name}']))\n"
                            case LMS_BinaryTypes.LIST_INDEX:
                                read_body += f"\t\t\tdata['{parameter.name}'] = {parameter.name}_items[reader.read_uint8({{lua_index=true}})]\n"
                                write_body += f"\t\twriter.write_uint8(index({parameter.name}_items, data['{parameter.name}']))\n"
                            case LMS_BinaryTypes.STRING:
                                read_body += f"\t\t\tdata['{parameter.name}'] = reader.read_len_prefixed_utf16_string()\n"
                                write_body += f"\t\t\twriter.write_len_prefixed_utf16_string(data['{parameter.name}'])\n"
                            # UInt8, UInt16, UInt32 handling here
                            case _:
                                bit_value = LMS_BinaryTypes._get_bits(parameter.type)
                                read_body += f"\t\t\tdata['{parameter.name}'] = reader.read_uint{bit_value}()\n"
                                write_body += f"\t\t\twriter.write_uint{bit_value}(tonumber(data['{parameter.name}']))\n"

                    file.write(
                        function_template.format(
                            name=name,
                            list_items=list_body,
                            read_body=read_body,
                            write_body=write_body,
                        )
                    )

            file.write("\nstream_functions = {\n")

            for name in function_names:
                file.write(f"\t['{name}'] = {name},\n")
            file.write("}\n\n")

            file.write("return stream_functions")

            with open(structure_path, "w+") as file:
                json.dump(Preset.msbp_structure_to_dict(msbp), file, indent=2)
