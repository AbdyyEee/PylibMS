# PylibMS
Python library built in Python 3.10+ or the libMessageStudio (LMS) proprietary file formats from Nintendo. Supports MSBT, MSBP, and MSBF. Games that work with the library, including but not limited to:
* Tomodachi Life 
* Nintendo Badge Arcade
* The Legend of Zelda: A Link Between Worlds
* Animal Crossing: Amiibo Festival
* Super Mario 3D World
* Super Mario 3D Land.
# Features and Usage
# Reading 
MSBT
```py
from LMS.Message.MSBTStream import read_msbt

# Create the MSBT object
with open("Drama.msbt", "rb+") as f:
    msbt = read_msbt(f)
```
# Writing 
```py
from LMS.Message.MSBTStream import write_msbt

with open("Out.msbt", "wb") as f:
    write_msbt(f, msbt)
```
See [the wiki](https://github.com/AbdyyEee/PylibMS/wiki) for more explanations and examples on how to use the library.
# Installation
```
pip install PylibMS
```
Python version must be `>=3.10.`
