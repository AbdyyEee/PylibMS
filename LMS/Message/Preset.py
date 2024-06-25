from LMS.Project.MSBP import MSBP
from LMS.Common.LMS_Enum import LMS_BinaryTypes
from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer

from LMS.Message.Preset_Constants import RESTRICTED_GLOBALS, ALLOWED_ATTRIBUTES

from lupa.lua54 import LuaRuntime
from typing_extensions import Callable


def filter_attribute_access(obj, attr_name, is_setting):
     if not isinstance(obj, (Reader, Writer)):
         raise AttributeError("Object is not a Reader or Writer!")
     
     if isinstance(attr_name, str):
        if attr_name not in ALLOWED_ATTRIBUTES:
            raise AttributeError('You cannot access this attribute.')
        return attr_name

class Preset:
    """A static class for loading and storing a preset."""
    def __init__(self, globals: list[str] = None):
        self.lua_runtime = LuaRuntime(attribute_filter=filter_attribute_access)

        self.stream_functions: dict[str:Callable] = {}

        with open("LMS/Message/System.lua", "r") as file:
            self.stream_functions = dict(self.lua_runtime.execute(file.read()))
        
        globals = self.lua_runtime.globals()

        if globals is not None:
            for name in globals:
                globals[name] = None
        else:
            for name in RESTRICTED_GLOBALS:
                globals[name] = None 
        
    def load_preset_file(self, file_name: str) -> None:
        with open(file_name, "r+") as file:
            self.stream_functions.update(dict(self.lua_runtime.execute(file.read())))

    @staticmethod
    def create_preset_file(file_name: str, msbp: MSBP) -> None:
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
        # Instead, set the functions in a dictionary so that function names can be edited
        # and still indexed properly with the raw name 
        stream_functions = {}

        comment_message = """
--[[ 
   This is a preset used for parsing tags. 
   DO NOT edit any variable which are list items (tables that appear at the top of a tag function). It will lead to errors.
   Make sure you peserve parameter names when editing a function.
--]]
"""
        with open(file_name, "a") as file:
            file.write(comment_message)
            file.truncate()

            file.write("local stream_functions = {}\n\n")
            file.write(index_function)
            for group in structure[1:]:
                for tag in group.tags:
                    read_body = ""
                    write_body = ""
                    list_body = ""

                    name = f"{group.name.lower()}_{tag.name.lower()}"
                    stream_functions[name] = name 
                    for parameter in tag.parameters:
                        list_items = parameter.list_items
                        if len(list_items):
                            list_body += f"\tlocal {parameter.name}_items = {set(list_items)}\n"

                        match parameter.type:
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

                    file.write(function_template.format(name=name, list_items=list_body, read_body=read_body, write_body=write_body))
            
            file.write("\nstream_functions = {\n")
            
            for name in stream_functions:
                file.write(f"\t['{name}'] = {name},\n")
            file.write("}\n\n")
            
            file.write("return stream_functions")


            
                



           
        

    