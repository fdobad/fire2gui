__qGIS python development__

# What's here
```
firemodule/                 :   plug in builder widget dialog based
minimal/                    :   qgis-minimal-plugin based 
ProcessingScriptExample/    :   Processing > ToolBox > Scripts > Open/Add... example
QgisRequests/               :   qgis web-api requests 
qgisUserFolder/             :   user sandbox
standalone/                 :   app that uses qgis but not qgis desktop
tmp/                        :   dev space
```

# testing
## run QGIS Desktop
Run qgis from a terminal in the provided folder
```
$ cd fire2gui/qgis/qgisUserFolder/
$ qgis project.qgz
```

## minimal manual install
```
<plugin-folder>
linux : ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
win   : C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\minimal

$ git clone https://github.com/wonder-sk/qgis-minimal-plugin minimal
$ mkdir -p <plugin-folder>/minimal
$ cd <plugin-folder>/minimal
$ ln -s path/to/minimal/metadata.txt .
$ ln -s path/to/minimal/__init__.py .

(mklink replaces ln -s in windows)
```

## first install 
- `./deploy_linux.sh` to remove and re-symlink the plugin directory  
- Menu > Plugins > Manage ... > enable plugins  
- type "fire.."  
- click install plugin  
Now you'll see a new menu icon on the right called Fire  

## soft reload
- install 'Plugin Reloader' plugin  
- configure it to reload 'fire..' plugin  
- click to reload when making small changes to the code  

# debian dev env
Install QGIS Desktop from the software app
```
# Qt+python
sudo apt install python3-venv ipython
sudo apt install pyqt5-dev pyqt5-dev-tools python3-pyqt5 python3-dbus.mainloop.pyqt5 python3-dbus.mainloop.pyqt5-dbg
# ugly
sudo apt install gdal-bin python3-gdal
# for using plugin builder
pip install nose pb_tool
```

# paths
## debian default install
```
~/.local/share/QGIS/QGIS3/profiles/default/python/  
/usr/share/qgis/python/plugins  
```

# references
## pyqgis
- [pyqgis docs](https://www.qgis.org/pyqgis/master/)
- [developer cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/intro.html)
- [qobject multithreading?](https://github.com/wonder-sk/qgis-mtr-example-plugin/blob/master/plugin.py)

## plugins
- [minimal plugin repo](https://github.com/wonder-sk/qgis-minimal-plugin)
- [plugin debugger](https://github.com/wonder-sk/qgis-first-aid-plugin)
- [no binaries!!](https://plugins.qgis.org/publish/)
- [homepage](https://plugins.qgis.org/)
- [windows python packages?](https://landscapearchaeology.org/2018/installing-python-packages-in-qgis-3-for-windows/)
- [windows python packages ugly](https://www.lutraconsulting.co.uk/blog/2016/03/02/installing-third-party-python-modules-in-qgis-windows/)

## qgis
- [core developer tips](https://woostuff.wordpress.com/)
- [core developer tips](http://nyalldawson.net/)
- [workshop](https://madmanwoo.gitlab.io/foss4g-python-workshop/)
- [custom processing script](https://madmanwoo.gitlab.io/foss4g-python-workshop/processing/)
- [qgisblog](https://kartoza.com/search?q=qgis)
- []()
