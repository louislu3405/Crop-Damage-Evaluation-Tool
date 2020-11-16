# Author: Yu-Hsiang Lu
# Edit Date: 11/12/2020
# The Crop Damage Evaluation Tool to analyze the crop damage area using Sentinel-1 SLC images.
# The Tool is designed to be run in QGIS Python console. 


# ---Pop-up windows to ask the user to enter inputs---
input_img = QInputDialog.getText(None, "Input DVDI Image","Please enter the file path to your DVDI image: ")
outputCRS = QInputDialog.getText(None, "Assign CRS","Please specify your Coordiante System for the output raster in EPSG. E.g., 'EPSG:32615': ")
workplace = QInputDialog.getText(None, "Working Folder","Please specify your working folder: ")
threshold_dB = QInputDialog.getText(None, "Pixel Difference Threshold","Please specify your pixel difference threshold: ")
threshold_area = QInputDialog.getText(None, "Area Threshold","Please specify your area threshold: ")
# transfer the input to the usable string format.
input_bf_img = input_img[0]
outputCRS = outputCRS[0]
workplace = workplace[0]
threshold_dB = threshold_dB[0]
threshold_area = threshold_area[0]

# --- Reclassify ---

# Purpose: Reclassify the mosaicked raster by the first threshold: pixel-difference threhsold, to generate the preliminary damage map
clip_ras = QgsRasterLayer(input_bf_img)
output = r"%s\qgsRclThreshold1.tif"%workplace

params = {
    'INPUT_RASTER': clip_ras,
    'RASTER_BAND': 1,
    'TABLE': [-100, threshold_dB, 0, threshold_dB, 100, 1],
    'NO_DATA': 0,
    'OUTPUT': output
}

processing.run("qgis:reclassifybytable", params)


# --- Shrink and Expand (using the same value) ---

# Purpose: Remove the small isolated group of pixels and fill the holes in main damaged area
rcl_ras = QgsRasterLayer(r"%s\qgsRclThreshold1.tif"%workplace)
output = r"%s\qgsShrinkExpandTest.tif"%workplace
    
params = {
    'INPUT': rcl_ras,
    'OPERATION': 3,
    'CIRCLE': 0,
    'RADIUS': 2,
    'EXPAND': 1,
    'RESULT': output
}

processing.run("saga:shrinkandexpand", params)

# --- Raster to polygon ---

# Purpose: Conver the map to polygon in order to calculate the area. 
# After the area is calculated, use the second threshold to filtered out damaged area that the area is smaller than the threshold
shrink_ras = QgsRasterLayer(r"%s\qgsShrinkExpandTest.sdat"%workplace)
output = r"%s\qgsRtoV.shp"%workplace

params = {
    'input': shrink_ras,
    'type': 2,
    'column': 'value',
    '-s': False,
    '-v': False,
    '-z': False,
    '-b': False,
    '-t': False,
    'output': output,
    'GRASS_OUTPUT_TYPE_PARAMETER':0 ,
    'GRASS_REGION_CELLSIZE_PARAMETER': 0,
    'GRASS_REGION_PARAMETER' : None, 
    'GRASS_VECTOR_DSCO' : '', 
    'GRASS_VECTOR_EXPORT_NOCAT' : False, 
    'GRASS_VECTOR_LCO' : ''
}

processing.run("grass7:r.to.vect", params)

# --- select by area ---
# Purpose: add area to attribute
shp = r"%s\qgsRtoV.shp"%workplace
output = r"%s\qgsRtoVWithArea.shp"%workplace

params = {
    'INPUT': shp,
    'CALC_METHOD': 0,
    'OUTPUT': output,
}

processing.run("qgis:exportaddgeometrycolumns",params)

# --- Extract By Attribute ---

# extract polygons with area larger than the second threshold
shp = r"%s\qgsRtoVWithArea.shp"%workplace
output = r"%s\FinalVector.shp"%workplace

params = {
    'INPUT': shp,
    'FIELD': 'area',
    'OPERATOR': 2,
    'VALUE': threshold_area,
    'OUTPUT': output
}

processing.run("qgis:extractbyattribute", params)

# ---Rasterrize---

# Purpose: convert the polygons back to raster file
shp = r"%s\FinalVector.shp"%workplace
output = r"%s\FinalRaster.tif"%workplace

params = {
    'INPUT': shp,
    'FIELD': 'value',
    'BURN': 0,
    'UNITS': 1,
    'WIDTH': shrink_ras.rasterUnitsPerPixelX(),
    'HEIGHT': shrink_ras.rasterUnitsPerPixelY(),
    'EXTENT': shrink_ras.extent(),
    'NODATA': 0.0,
    'OPTIONS': '',
    'DATA_TYPE': 1,
    'OUTPUT': output
}

processing.run("gdal:rasterize", params)

# --- Calculate the total estimated damaged area ---
layer = QgsVectorLayer(r"%s\FinalVector.shp"%workplace)
features = layer.getFeatures()
damaged_area = 0
for feat in features:
    attr = feat.attributes()[2]
    damaged_area += int(attr)

msg = QMessageBox()
msg.setText("The total estimated damaged area is %s map units"%damaged_area)
msg.show()

### Appendices
'''
# show the settings in QGIS GUI
test = processing.createAlgorithmDialog("gdal:cliprasterbymasklayer", params)
test.show()
processing.algorithmHelp("algorithm name")  # show algorithm help
###QgsProject.instance().addMapLayer(bnd_layer)
'''