
Pedidas equipo fire2
- Revisar ParseInputs, 
    = entregar copia con los defaults que el usuario del plugin deberia ocupar
    - si quieren cambiar los titulos de los parser groups
    - revisar opciones de WeatherOpt ? son constant, distribution, random, rows ???? cuales son, cual deberia ocupar para cada 
        - ? random ? genera random de cuantos rows? cuando le avisa al usuario cual fue el generado ?

- donde saco y escribo los 4 escenarios de humedad?



TODO:
- cargar resultados
    if nsims == 1
        - cargar todos los ForestGrid.csv adentro de un grupo
        - el ultimo forestgrid##.csv como asc
        - mejora usar tif en vez de asc???
    else:
        joder david y rodgrigo para que actualizen el repo (parece que la opcion es --geotiff, cual es la opcion)
        -> burn_probability_map 
        dpv
        bc

Instance

-1. nunca usar import *

0. escribir en el logfile u otro los argumentos leidos

1. malditas comas por puntos, ?
    $ sed -i -e 's/,/\./g' *.asc

2. fcc o ccf :resuelto ccf en ingles fcc espa;ol

3. input folder / al final... zancadilla oscura para el usuario dev!

4. DataGenerator se marea con instancia grande:

    File "/home/fdo/source/C2FSB/Cell2Fire/DataGeneratorC.py", line 154, in DataGrids
        CBD[aux] = float(c)
    IndexError: index 42084 is out of bounds for axis 0 with size 42084

    Cambiar a:
    import numpy as np
    a = np.loadtxt( 'cbd.asc', skiprows=6)
    a.shape
    (1638, 2176)

Development Notes

0.  Para comunicarle al usuario un print 'en tiempo + real' (ver buffered vs unbuffered stdout y stderr streams)
    print(...) -> print(... ,flush=True)
    print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

    print('Ha comenzado', flush=True)
    print('%tag: 1.0', flush=True)
    print('%tag: 99.0', flush=True)
    print('%tag: 100.0', flush=True)
    print('Ha terminado', flush=True)
 

1. Object Naming Convention : 
To coordinate from argparse dest names to QtDesigner, modules follow this prefix_suffix standard:

1.1 Prefix simplified component type: 
	prefixName	:	<class type> 
	layerComboBox	:	QgsMapLayerComboBox 
	fileWidget	:	QgsFileWidget
	radioButton	:	QRadioButton
	spinBox		:	QSpingBox
	doubleSpinBox	:	QDoubleSpingBox

1.2 Suffix:
	suffixName 	:	<argparse.item.dest>
	ROS_CV		:	ROS_CV

1.3 Mandatory for double|spinBoxes, example: doubleSpinBox_ROS_CV. They are retrieved like this:

        args.update( { o.objectName()[ o.objectName().index('_')+1: ]: o.value() 
            for o in self.dlg.findChildren( (QDoubleSpinBox, QSpinBox), 
                                        options= Qt.FindChildrenRecursively)})

1.4 RadioButton Groups share the same startin suffix name, then Uppercase diverge:
	radioButton_weatherFile, 
	radioButton_weatherFolder, 
	radioButton_weatherRandom, 
	radioButton_weatherConst
	
	radioButton_ignitionRandom, 
	radioButton_ignitionPoints, 
	radioButton_ignitionProbMap

2. ParseDialog nunca ocupa ningun nombre en ParseInputs.py
