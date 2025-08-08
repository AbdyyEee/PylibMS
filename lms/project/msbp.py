from lms.common.lms_fileinfo import LMS_FileInfo
from lms.project.definitions.attribute import LMS_AttributeDefinition
from lms.project.definitions.color import LMS_Color
from lms.project.definitions.style import LMS_Style
from lms.project.definitions.tag import LMS_TagGroup


class MSBP:
    """A class that represents a MSBP file.

    https://nintendo-formats.com/libs/lms/msbp.html."""

    def __init__(
        self,
        info: LMS_FileInfo,
        colors: list[LMS_Color],
        config: list[LMS_AttributeDefinition],
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

    @property
    def info(self) -> LMS_FileInfo:
        """The stream info of the MSBP."""
        return self._info

    @property
    def colors(self) -> list[LMS_Color]:
        """The color definitions for the project."""
        return self._colors

    @property
    def attribute_info(self) -> list[LMS_AttributeDefinition]:
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
