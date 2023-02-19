<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis minScale="1e+08" version="3.10.14-A Coruña" maxScale="0" hasScaleBasedVisibilityFlag="0" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <customproperties>
    <property value="Value" key="identify/format"/>
  </customproperties>
  <pipe>
    <rasterrenderer opacity="1" grayBand="1" gradient="BlackToWhite" type="singlebandgray" alphaBand="-1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>MinMax</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <contrastEnhancement>
        <minValue>0</minValue>
        <maxValue>1</maxValue>
        <algorithm>StretchToMinimumMaximum</algorithm>
      </contrastEnhancement>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeOn="0" colorizeBlue="128" colorizeGreen="128" saturation="0" grayscaleMode="0" colorizeRed="255" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
