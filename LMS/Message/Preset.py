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

        self._initialize_globals(global_list)

    def _initialize_globals(self, global_list):
        globals = self.lua_runtime.globals()

        restricted_globals = global_list if global_list else RESTRICTED_GLOBALS
        for name in restricted_globals:
            globals[name] = None

    @staticmethod
    def msbp_structure_to_dict(msbp: MSBP) -> dict:
        # Skip System
        structure = msbp.get_tag_structure()[1:]

        def parameter_to_dict(parameter):
            return {
                "name": parameter.name,
                "type": parameter.type.value,
                "list_items": parameter.list_items,
            }

        def tag_to_dict(tag):
            return {
                "name": tag.name,
                "parameters": [parameter_to_dict(param) for param in tag.parameters],
            }

        return [{"name": group.name, "tags": [tag_to_dict(tag) for tag in group.tags]} for group in structure]

    def load_preset_file(self, preset_path: str, structure_path: str) -> None:
        """Loads a preset file.
        
        :param `preset_path`: the path of the .lua Preset.
        :param `preset_path`: the path of the JSON structure.
        """
        self.structure = [SYSTEM_STRUCTURE]
        self.stream_functions = self.base_preset

        with open(preset_path, "r") as file:
            self.stream_functions.update(dict(self.lua_runtime.execute(file.read())))

        with open(structure_path, "r") as file:
            self.structure += json.load(file)

    @staticmethod
    def create_preset_file(preset_path: str, structure_path: str, msbp: MSBP) -> None:
        """Creates a lua Preset.
        
        :param `preset_path`: the path to generate the Lua preset.
        :param `structure_path`: the path to generate the JSON structure.
        :param `msbp`: a project object for a specifc game.
        """
        """Creates a preset file."""
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
        # Index function for writing the index of list ltems
        index_function = "local function index(table, value) for i, v in ipairs(table) do if v == value then return i - 1 end end end\n"

        function_names = []
        lua_code = ["local stream_functions = {}\n\n", index_function]

        # Slice by 1 to avoid the System group
        for group in structure[1:]:
            for tag in group.tags:
                name = f"{group.name.lower()}_{tag.name.lower()}"
                function_names.append(name)

                list_body, read_body, write_body = Preset._generate_function_bodies(tag)

                lua_code.append(function_template.format(
                    name=name,
                    list_items=list_body,
                    read_body=read_body,
                    write_body=write_body,
                ))

        # Add the function table 
        lua_code.append("\nstream_functions = {\n")
        lua_code.extend(f"\t['{name}'] = {name},\n" for name in function_names)
        lua_code.append("}\n\nreturn stream_functions")

        lua_code.insert(0, """--[[ 
   This is a preset used for parsing tags. 
   DO NOT edit any variable which are list items (tables that appear at the top of a tag function). It will lead to errors.
   Make sure you peserve parameter names when editing a function.
--]]\n\n""")
        
        with open(preset_path, "w+") as file:
            file.truncate()
            file.write("".join(lua_code))

        with open(structure_path, "w+") as file:
            json.dump(Preset.msbp_structure_to_dict(msbp), file, indent=2)

    @staticmethod
    def _generate_function_bodies(tag):
        list_body = ""
        read_body = ""
        write_body = ""

        body_template = {
                LMS_BinaryTypes.FLOAT: (
                    "\t\t\t\tdata['{parameter_name}'] = reader.read_float()\n",
                    "\t\t\t\twriter.write_float(tonumber(data['{parameter_name}']))\n"
                ),
                LMS_BinaryTypes.LIST_INDEX: (
                    "\t\t\t\tdata['{parameter_name}'] = {parameter_name}_items[reader.read_uint8({{lua_index=true}})]\n",
                    "\t\t\t\twriter.write_uint8(index({parameter_name}_items, data['{parameter_name}']))\n"
                ),
                LMS_BinaryTypes.STRING: (
                    "\t\t\t\tdata['{parameter_name}'] = reader.read_len_prefixed_utf16_string()\n",
                    "\t\t\t\twriter.write_len_prefixed_utf16_string(data['{parameter_name}'])\n"
                )
            }
        
        for parameter in tag.parameters:
            if parameter.list_items:
                list_body += f"\t\tlocal {parameter.name}_items = {set(parameter.list_items)}\n"

            if parameter.type not in body_template:
                read_body += f"\t\t\t\tdata['{parameter.name}'] = reader.read_uint{LMS_BinaryTypes._get_bits(parameter.type)}()\n"
                write_body += f"\t\t\t\twriter.write_uint{LMS_BinaryTypes._get_bits(parameter.type)}(tonumber(data['{parameter.name}']))\n"
            else:
                read, write = body_template[parameter.type]
                read_body += read.format(parameter_name=parameter.name)
                write_body += write.format(parameter_name=parameter.name)

        return list_body, read_body, write_body
