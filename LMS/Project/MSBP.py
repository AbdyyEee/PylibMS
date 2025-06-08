from LMS.Common.LMS_FileInfo import LMS_FileInfo
from LMS.Project.Definitions.Attribute import LMS_AttributeInfo
from LMS.Project.Definitions.Color import LMS_Color
from LMS.Project.Definitions.Style import LMS_Style
from LMS.Project.Definitions.Tag import LMS_TagGroup


class MSBP:
    """A class that represents a MSBP file.

    https://nintendo-formats.com/libs/lms/msbp.html."""

    def __init__(
        self,
        info: LMS_FileInfo,
        colors: list[LMS_Color],
        config: list[LMS_AttributeInfo],
        tag_groups: list[LMS_TagGroup],
        styles: list[LMS_Style],
        source_files: list[str],
    ):
        self.name = None

        self._info = info

        self._colors = colors
        self._config = config
        self._tag_groups = tag_groups
        self._styles = styles
        self._source_files = source_files

        self.clb1_exists = False
        self.alb1_exists = False
        self.slb1_exists = False

    @property
    def info(self) -> LMS_FileInfo:
        """The stream info of the MSBP."""
        return self._info

    @property
    def colors(self) -> list[LMS_Color]:
        """The color definitions for the project."""
        return self._colors

    @property
    def attribute_info(self) -> list[LMS_AttributeInfo]:
        """The attribute definitions for the project instance."""
        return self._config

    @property
    def tag_groups(self) -> list[LMS_TagGroup]:
        """The tag group definitions for the project instance."""
        return self._tag_groups

    @property
    def style_list(self) -> list[LMS_Style]:
        """The style definitions for the project instance."""
        return self._styles

    @property
    def source_files(self) -> list[str]:
        """The source file definitions for the project instance."""
        return self._source_files
