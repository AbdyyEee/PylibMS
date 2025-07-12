from LMS.Common.LMS_DataType import LMS_DataType
from LMS.TitleConfig.Definitions.Tags import TagDefinition
from LMS.TitleConfig.Definitions.Value import ValueDefinition


def get_system_tag(group: int | str) -> TagDefinition:
    return SYSTEM_INT_MAP[group] if isinstance(group, int) else SYSTEM_STR_MAP[group]


RUBY_TAG = TagDefinition(
    group_name="System",
    group_index=0,
    tag_name="Ruby",
    tag_index=0,
    description="Displays a RUBY character.",
    parameters=[
        ValueDefinition(
            name="rt", description="The ruby character.", datatype=LMS_DataType.STRING
        )
    ],
)

FONT_TAG = TagDefinition(
    group_name="System",
    group_index=0,
    tag_name="Font",
    tag_index=1,
    description="Sets the font file of text.",
    parameters=[
        ValueDefinition(
            name="face", description="The font face name.", datatype=LMS_DataType.STRING
        )
    ],
)

SIZE_TAG = TagDefinition(
    group_name="System",
    group_index=0,
    tag_name="Size",
    tag_index=2,
    description="Alters the size of text.",
    parameters=[
        ValueDefinition(
            name="percent",
            description="The new size as a percent.",
            datatype=LMS_DataType.UINT16,
        )
    ],
)
COLOR_TAG = TagDefinition(
    group_name="System",
    group_index=0,
    tag_name="Color",
    tag_index=3,
    description="Sets the color of text in a message in RGBA form.",
    parameters=[
        ValueDefinition(
            name="r", description="The red color value.", datatype=LMS_DataType.UINT8
        ),
        ValueDefinition(
            name="g", description="The green color value.", datatype=LMS_DataType.UINT8
        ),
        ValueDefinition(
            name="b", description="The blue color value.", datatype=LMS_DataType.UINT8
        ),
        ValueDefinition(
            name="a",
            description="The alpha transprency value.",
            datatype=LMS_DataType.UINT8,
        ),
    ],
)

PAGEBREAK_TAG = TagDefinition(
    group_name="System",
    group_index=0,
    tag_name="PageBreak",
    tag_index=4,
    description="Displays text in the same label on different pages.",
)
