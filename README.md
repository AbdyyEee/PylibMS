# PylibMS
Python library built in Python 3.10+ or the libMessageStudio (LMS) proprietary file formats from Nintendo. Supports the following:

* Full reading and writing of MSBT files.
* Full reading of MSBP files.
* Supports encoded/decoded attributes and encoding/decoded tags.
* Additonal tag manipulation.

This library is designed to support LMS revision 3.0 and above, with the associated file formats used across the following Nintendo platforms:
* Wii (Specific titles only)
* Nintendo 3DS
* Wii U
* Mobile (Specific titles only)
* Nintendo Switch

# Features and Usage
Simple preview of the library is below. See [the wiki](https://github.com/AbdyyEee/PylibMS/wiki) for more explanations and examples.
## Reading 
MSBT
```py
from lms.message.msbtio import read_msbt_path

msbt = read_msbt_path("Game.msbt")
```
## Writing 
```py
from lms.message.msbtio import write_msbt_path

write_msbt_path("Out_Game.msbt")
```
# Adding/Editing Presets
To add or edit Preset, you may create an issue with the relevant `yaml` file and the game it is for. 

# Installation
```
pip install PylibMS
```

Python version must be `>=3.12.`
# Credits & Sources
* [Nintendo-File-Formats](https://nintendo-formats.com) by Kinnay: For existing information on the MSBT and MSBP file formats.
* [Trippixyz](https://github.com/Trippixyz): For helping me get started general decompilation of the formats and general help.
* [AeonSake](https://github.com/AeonSake): Inspiration for some the implementation of the library and a bit of general help.
