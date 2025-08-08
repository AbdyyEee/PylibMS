from dataclasses import dataclass


@dataclass
class LMS_Style:
    region_width: int
    line_number: int
    font_index: int
    color_index: int
    name: str | None = None
