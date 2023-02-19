Development Notes

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
