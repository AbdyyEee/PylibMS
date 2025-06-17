# PylibMS
Python library built in Python 3.10+ or the libMessageStudio (LMS) proprietary file formats from Nintendo. Supports the following:

* Full reading and writing of MSBT files.
* Full reading of MSBP files.
* Supports encoded/decoded attributes and encoding/decoded tags.
* Additonal tag manipulation.

Games that work with the library, including but not limited to:
* Tomodachi Life 
* Nintendo Badge Arcade
* The Legend of Zelda: A Link Between Worlds
* Animal Crossing: Amiibo Festival
* Super Mario 3D World
* Super Mario 3D Land.
# Features and Usage
Simple preview of the library is below. See [the wiki](https://github.com/AbdyyEee/PylibMS/wiki) for more explanations and examples.
## Reading 
MSBT
```py
from LMS.Message.MSBTStream import read_msbt

with open("Game.msbt", "rb+") as f:
    msbt = read_msbt(f)
```
## Writing 
```py
from LMS.Message.MSBTStream import write_msbt

with open("Out.msbt", "wb") as f:
    write_msbt(f, msbt)
```
# Adding Presets
To add a Preset, you may create an issue with the relevant yaml file and the game it is for.

# Installation
```
pip install PylibMS
```
Python version must be `>=3.10.`
# Credits & Sources
* [Nintendo-File-Formats](nintendo-formats.com) by Kinnay: For existing information on the MSBT and MSBP file formats.
* [Trippixyz](https://github.com/Trippixyz): For helping me get started general decompilation of the formats and general help.
* [AeonSake](https://github.com/AeonSake): Inspiration for some the implementation of the library and a bit of general help.
