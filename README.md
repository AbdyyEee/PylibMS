# PylibMS
PyLMS is a library built in Python3.10+ for Nintendo's LMS (libMessageStudio) file formats. Intended for games on the Nintendo 3DS and Wii U revisions of the file format. Examples such as:
* Tomodachi Life 
* Nintendo Badge Arcade
* The Legend of Zelda: A Link Between Worlds
* Animal Crossing: Amiibo Festival
* Super Mario 3D World
* Super Mario 3D Land.
# Features
List and descriptions of support functionality.
## MSBT
* Reading and writing of TXT2, LBL1, and ATR1 blocks big and little endian.
* Support for decoding of attributes, given a MSBP.
* Support for decoding of control tags given a preset.
    * Example: `[n0.3:00-00-00-FF]` in Kuriimu returns `[System:Color: r="0" g="0" b="0" a="255"]`.
## MSBP
* Reading little and big endian MSBP files.
# Planned
## MSBT
* Reading + Writing of TSY1.
* Second tag decoding mode that only includes tag group and name.
## MSBP
* Writing support.
## MSBF
* Implement the entire format from FLW3 editor.
