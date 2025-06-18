# Regex formats for control tags

# Regular format for any tag
TAG_FORMAT = r"(\[[^\]]+\])"

DECODED_FORMAT = r"\[(\w+):(\w+)(.*?)\]"
ENCODED_FORMAT = r"\[([A-Za-z0-9]+):([A-Za-z0-9]+)\s?([0-9A-Fa-f\-]*)?\]"

# Key value pair regex for decoded tags
PARAMETER_FORMAT = r'(\w+)="([^"]*)"'
