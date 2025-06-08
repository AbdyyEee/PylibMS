class LMS_Error(Exception):
    """Exception for non-specifc errors"""

    pass


class LMS_UnexpectedMagicError(Exception):
    """Exception for wrong magic of a LMS file"""

    pass


class LMS_MisalignedSizeError(Exception):
    """Exception for when size is not aligned."""

    pass
