# windows -basic- installer for qGIS plugin

Remove the comments when deploying!!

## Usage
1. `install_windows.bat` will: 
- activate Os4Geo environment
- upgrade pip 
- install requirements
- copy the plugin folder to qgis plugins

2. `install_debug.bat` does the same but verbose

3. `setup_and_test_IMREAD.bat` will
- create a python virtual environment
- activate it
- install imread from a .whl file pointed by requirements.txt when in windows
- test it loading a picture

4. `install_unix.sh` TODO
