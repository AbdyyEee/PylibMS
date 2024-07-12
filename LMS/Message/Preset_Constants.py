ALLOWED_ATTRIBUTES = [
    "get_utf16_encoding",
    "change_byte_order",
    "skip",
    "read_bytes",
    "seek",
    "tell",
    "read_uint8",
    "read_uint16",
    "read_float",
    "read_uint32",
    "read_string_len",
    "read_string_nt",
    "read_utf16_string",
    "read_len_prefixed_utf16_string",
    "write_uint8",
    "write_uint16",
    "write_uint32",
    "write_len_prefixed_utf16_string",
    "write_utf16_string",
    "write_bytes",
    "write_string_nt",
    "write_string",
]

RESTRICTED_GLOBALS = [
        "python", "io", "os", "debug", "package", "dofile",
        "load", "loadfile", "require", "collectgarbage",
        "rawget", "rawset", "getmetatable", "setmetatable", "coroutine"
]

SYSTEM_STRUCTURE = {
    "name": "System",
    "tags": [
      {
        "name": "Ruby",
        "parameters": [
          {
            "name": "rt",
            "type": 8,
            "list_items": []
          }
        ]
      },
      {
        "name": "Font",
        "parameters": [
          {
            "name": "face",
            "type": 8,
            "list_items": []
          }
        ]
      },
      {
        "name": "Size",
        "parameters": [
          {
            "name": "percent",
            "type": 1,
            "list_items": []
          }
        ]
      },
      {
        "name": "Color",
        "parameters": [
          {
            "name": "r",
            "type": 0,
            "list_items": []
          },
          {
            "name": "g",
            "type": 0,
            "list_items": []
          },
          {
            "name": "b",
            "type": 0,
            "list_items": []
          },
          {
            "name": "a",
            "type": 0,
            "list_items": []
          },
        ]
      },
      {
        "name": "PageBreak",
        "parameters": []
      }
    ]
}