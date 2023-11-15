from LMS.Stream.Reader import Reader
from LMS.Stream.Writer import Writer


def read_System_Ruby(reader: Reader):
    data = {}
    data["rt"] = reader.read_len_prefixed_utf16_string()

    return data


def write_System_Ruby(writer: Writer, data: dict):
    writer.write_len_prefixed_utf16_string(data["rt"])

    return


def read_System_Font(reader: Reader):
    data = {}
    data["face"] = reader.read_len_prefixed_utf16_string()

    return data


def write_System_Font(writer: Writer, data: dict):
    writer.write_len_prefixed_utf16_string(data["face"])

    return


def read_System_Size(reader: Reader):
    data = {}
    data["percent"] = reader.read_uint16()

    return data


def write_System_Size(writer: Writer, data: dict):
    writer.write_uint16(int(data["percent"]))

    return


def read_System_Color(reader: Reader):
    data = {}
    data["r"] = reader.read_uint8()

    data["g"] = reader.read_uint8()

    data["b"] = reader.read_uint8()

    data["a"] = reader.read_uint8()

    return data


def write_System_Color(writer: Writer, data: dict):
    writer.write_uint8(int(data["r"]))

    writer.write_uint8(int(data["g"]))

    writer.write_uint8(int(data["b"]))

    writer.write_uint8(int(data["a"]))

    return


def read_System_PageBreak(reader: Reader):
    data = {}
    return data


def write_System_PageBreak(writer: Writer, data: dict):
    return

base_preset = { "data": {
	0: {
	'name': 'System', 
	'tags': [
		{'name': 'Ruby', 'read_function' : read_System_Ruby, 'write_function': write_System_Ruby},
		{'name': 'Font', 'read_function' : read_System_Font, 'write_function': write_System_Font},
		{'name': 'Size', 'read_function' : read_System_Size, 'write_function': write_System_Size},
		{'name': 'Color', 'read_function' : read_System_Color, 'write_function': write_System_Color},
		{'name': 'PageBreak', 'read_function' : read_System_PageBreak, 'write_function': write_System_PageBreak},
	]},
}}