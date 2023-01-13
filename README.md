README.md
	plan
		objetivo: socializar c2fSB desarrollando GUI
		usuario: cientificos sin experiencia en instalar y compilar
		deadline: principios de marzo
	tareas
		familiarizarse con cell2fire
			usage
				use cases
				(cmd line) options
			dependencies
				python modules
				c++ binaries
		definir roadmap
			features
				usuario elije cualquier terreno de un mapa, recibe DEM
					limitar/recomendar tama;o maximo?
					disponible en v1
				usuario prepara weather input, recibe forecast y...
					como generar escenarios?
					disponible v1: forecast actual c/3hr
						v2 generar escenario por cada estacion del a;o
						v3 vector->campo de vientos
				fuels painter ? fire behaviour options ? simulation options ? reports ?
			distribution pipeline
				ojala que no sea dificil de a;adir nueva caracteristica en el simulador
				problema con el binario de windows del simulador
			Minimun Viable Product
				TBD
		✓ explorar gui-libs y platform deploy options
			hyper-V VM
				instalacion
					enable windows additional feature
					download & run
				✗ Windows VM + wsl: pesa 60GB!
				✓ Ubuntu VM: 12GB
			windows + WSL
				✗ pendiente hasta que incluyan servidor X nativo en windows
				instalacion
					enable windows additional feature
					[SERA OBSOLETO!] install & configure X server (Xming, Xsrv, ...)
					clone, compile & run
			tk
				pro: python canonico
				con: dificil empaquetar a exe (matplotlib por ej)
				✗ es peor que usar PyQt y qgis
			jupyter-lab
				pro: formularios rapidos
				pro: gui es pagina web
					✓ se puede servir facilmente con un tunel ssh
					se puede servir publicamente con web de login adicional
				con: familiaridad con dataScience (sesion interactiva de python)
				con: empaquetar a instalador es + dificil que servir
				pro: .ipynb files son intercambiables a .py y .md
				✓ se usara para prototipar la logica del GUI
			docker
				pro: poco codigo, adaptable, facil de desarrollar y servir
				con: no es verdaderamente multiplatforma ni empaquetable, hace VM
				instalacion
					local: docker-desktop -> clone -> run
					servidor: publicar con web-gui
			qGIS
				pro:
					gis gui & algoritmos en un solo lugar
					hay version para windows
				plug-in
					publicados NO DEBEN CONTENER BINARIOS
					instalacion privada es solo copiar a carpeta qgis/python/plugins
				standalone
					pro: usa qgis sin el IDE
					con: hay que desarrollar casi una QT app completa
					con: Incertidumbre en el empaquetamiento (pero si se instala qGIS desktop aparte se ve facil)
				con: Incertidumbre con la rapidez, conectar con el paralelismo se ve dificil
	resultados
		cell2fireSB
			quite' dependencia de opencv-python
		exploracion gui-lib
			elegido qgis plugin .zip
		notebook prototyping
			get elevation
			get wind
		VM
			instrucciones para generar maquina virtual con el repo de cell2fireSB
		qgis skeletons
			minimal plugin
			minimal standalone
	mission critical
		probar que windows instala y ejecuta plugin en zip con binario de c2f
