#!/bin/bash
# todo test: $1 to install outside the directory
plugin_name=$(sed -e '/^name=/!d' -e 's/name=//' -e 's/\r//' $1/metadata.txt)
#plugin_name=$(sed -e '/^name=/!d' -e 's/name=//' -e 's/\r//' metadata.txt)
echo "plugin name: $plugin_name"
#from=$PWD
from=$PWD/$1
echo "from: $from"
to=$HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins
echo "to  : $to"

if [[ -d $to/$plugin_name ]]; then 
	echo 'Destiny directory exists, removing'; 
	rm -rf $to/$plugin_name
else 
	echo 'Destiny directory doesnt exist, creating it';
fi
mkdir -p $to/$plugin_name

cd $to/$plugin_name
echo "Created $PWD"

# todo test : remove dependecy from plugin_files
# then just link de directory ?
#for F in $(cat $from/plugin_files.txt) ; do
for F in $(ls $from) ; do
	#echo $F
	ln -s $from/$F .
done
#ln -s $HOME/source/C2FSB .
echo 'New files in directory:'
ls -l
