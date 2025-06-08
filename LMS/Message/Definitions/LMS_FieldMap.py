from LMS.Field.LMS_Field import LMS_Field

# Typehint that represents a map of strings to field instances.
# Utilized as a means of storing attributes, or parameters in decoded tags mapped to their string names.
type LMS_FieldMap = dict[str, LMS_Field]
