class LMS_Style:
    def __init__(
        self,
        name: str,
        region_width: int = None,
        line_number: int = None,
        font_index: int = None,
        color_index: int = None,
    ):
        self.name = name
        self.region_width = region_width
        self.line_number = line_number
        self.font_index = font_index
        self.color_index = color_index
