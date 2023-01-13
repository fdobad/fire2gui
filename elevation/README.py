# # todo
# - translated .asc crs changes?
# - change gdal dependency to qGIS
# - plot (2y3d) jupyterlab interactive
#
# # install
#
# ```bash
# sudo apt install python3-gdal gdal-bin
# git clone
# # cd
# python3 -m venv pyvenv
# source pyvenv/bin/activate
# eio selfcheck
# ```

# # usage
# ## elevation to tif
# clip the SRTM1 30m DEM

# +
import elevation
# bounds 'left bottom right top' order.
# latitude and longitude coordinates (more precisely in geodetic coordinates in the WGS84 reference system EPSG:4326)
#bounds = (-70.64499, -33.44232, -70.64213, -33.43770) # sta lucia
#bounds = (-70.6543,-33.4444, -70.5698, -33.3793) # parque metropolitano
#bounds = (-71.5731237178895, -33.0493175478135, -71.5287880407362, -33.0258435387726) # incendion vina del mar
bounds = (-70.6517350942473, -33.4341245538389, -70.6084247534509, -33.4112941796125)


# else output goes to elevation.CACHE_DIR e.g.: ~/.cache/elevation/SRTM1/out.tif
import os
output = os.path.join( os.getcwd() , 'dem_30m.tif')
elevation.clip( bounds, product='SRTM1', output=output)
# -

# ## tif to raster(io) manipulations

# +
import rasterio
dataset = rasterio.open('dem_30m.tif')

# some properties
print(dataset.dtypes, dataset.width, dataset.height, dataset.res, dataset.bounds, dataset.crs)

# upper left corner
dataset.transform * (0, 0) 
# lower right corner
dataset.transform * (dataset.width, dataset.height)

# get data array
dataset.indexes
band1 = dataset.read(1) # returns 2d numpy array
# -

# print info
# !rio info dem_30m.tif --indent 2 --verbose

# get json info
import json
info = json.loads(os.popen('rio info dem_30m.tif').read())

# ## plot

from matplotlib import pyplot as plt
def plot( dataset):
    plt.clf()
    plt.imshow(dataset.read(1), cmap='terrain')
    plt.savefig('out.png')
    plt.show()


plot(dataset)

# ## translate dem
# NOTE: "!" means command is run in the terminal  
# ### tif -> asc

# ! gdal_translate -of AAIGrid dem_30m.tif dem_30m.asc

# ### tif -> asc /3 cellsize
# As SRTM1 data source is 30m but fire2cell uses 100m do:

dataset.res[0]*10/3

# !gdal_translate -tr 0.000925925925925926 0.000925925925925926 -of AAIGrid dem_30m.tif dem_100m.tif

# #### plot

dataset = rasterio.open('dem_100m.tif')
plot(dataset)

dataset = rasterio.open('dem_100m.asc')
plot(dataset)

# ## lat/long <-> (chile) utm
# ### gdal

# + active=""
# !gdaltransform -s_srs epsg:4326 -t_srs epsg:24879
# Enter X Y [Z [T]] values separated by space, and press Return.
# -70.645138888889 -33.442361111111
# 347264.443426759 6298834.38844403 0
# -

# ### qgis

from qgis.core import (
        QgsCoordinateReferenceSystem,
        QgsCoordinateTransform,
        QgsProject,
        QgsPointXY,
        )

crsSrc = QgsCoordinateReferenceSystem("EPSG:24879")
crsDest = QgsCoordinateReferenceSystem("EPSG:4326")
transformContext = QgsProject.instance().transformContext()
xform = QgsCoordinateTransform(crsSrc, crsDest, transformContext)

point24879 = QgsPointXY(7864180.88813121151179075, -3954168.27993376972153783)
point4326 = xform.transform(point24879)
point4326

point4326 = QgsPointXY(-70.645138888889, -33.442361111111)
point24879 = xform.transform(point4326, QgsCoordinateTransform.ReverseTransform)
point24879

# ### HINT
# - Desde, lat/long es: WGS84 reference system EPSG:4326
# - Hasta, en Chile:
#  - zona sur: EPSG:24879 > PSAD56 / UTM zone 19S
#  - zona norte: EPSG:29193 SAD69 / UTM zone 23S

# # references
# https://www.sirgaschile.cl/ConversionSC/transformadorDatum.html  
# https://epsg.io/24879  
# https://epsg.io/29193  
# https://gdal.org/programs/gdaltransform.html  
# https://gdal.org/programs/gdal_translate.html  
# https://www.researchgate.net/post/How-to-obtain-digital-elevation-data-in-ascii-format  
# https://www.openstreetmap.org  
# http://elevation.bopen.eu/en/stable/quickstart.html  
# https://rasterio.readthedocs.io/en/latest/quickstart.html  
#
# # plop
# https://stackoverflow.com/questions/55827778/elevation-xyz-data-to-slope-gradient-map-using-python  
# https://stackoverflow.com/search?q=python+elevation&s=676696f8-8555-45f8-b4ae-c2adceb79ded  
