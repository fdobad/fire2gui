#!/bin/env python3
'''
Generating fuels data

# lookup table
'''
import pandas as pd

''' knownFuelTypes '''
df = pd.read_csv('spain_lookup_table.csv')
kFT = df.grid_value.unique()

''' get raster to copy, as elevation '''
import rasterio
e = rasterio.open('elevation.asc')

H,W = e.read(1).shape

fuels = np.random.choice( kFT, size=(H,W))

f = rasterio.open('fuels.asc', mode='w', driver=e.driver, width=e.width, height=e.height, count=1, crs=e.crs, dtype=e.read(1).dtype)

f.write(fuels,1)
f.close()
