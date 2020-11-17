# Author: Yu-Hsiang Lu
# Edit Date: 11/07/2020
# The Crop Damage Evaluation Tool to analyze the crop damage area using Sentinel-1 SLC images.
# The Tool is designed to be run in QGIS Python console. 


# ---Pop-up windows to ask the user to enter inputs---
number_of_frame = QInputDialog.getText(None, "Number of Sets", "How many frame of images do you plan to use? ") # get the number of sets (frames) of images that will be used in the tool
number_of_frame = int(number_of_frame[0]) # convert the input to integer
image_set = []  # stores the input images to [[Before Image 1, After Image 1, Boundary1], [Before Image 2, After Image 2, Boundary1] ......]




for input_a_set in range(number_of_frame): # Input multiple sets of different images
    input_bf_img = QInputDialog.getText(None, "Before Image","Please enter the file path to your *FRAME:%d* \"Before\" image: "%(input_a_set+1))
    input_af_img = QInputDialog.getText(None, "After Image", "Please etner the file path to your *FRAME:%d* \"After\" image: "%(input_a_set+1))
    boundary_file = QInputDialog.getText(None, "Boundary Shapefile","Please specify your bounary file for *FRAME:%d* : "%(input_a_set+1))
    # transfer the input to the usable string format.
    input_bf_img = input_bf_img[0]
    input_af_img = input_af_img[0]
    boundary_file = boundary_file[0]
    image_set.append([input_bf_img,input_af_img,boundary_file]) # append the new frame data to the image set

outputCRS = QInputDialog.getText(None, "Assign CRS","Please specify your Coordiante System for the output raster in EPSG. E.g., 'EPSG:32615': ")
workplace = QInputDialog.getText(None, "Working Folder","Please specify your working folder: ")
threshold_dB = QInputDialog.getText(None, "Pixel Difference Threshold","Please specify your pixel difference threshold: ")
threshold_area = QInputDialog.getText(None, "Area Threshold","Please specify your area threshold: ")

# transfer the input to the usable string format.
outputCRS = outputCRS[0]
workplace = workplace[0]
threshold_dB = threshold_dB[0]
threshold_area = threshold_area[0]

def create_pixel_difference_map(frame_data, frame_num,workplace):   # (frame data [before img, after img, boundary file], frame number No., working folder)

    # --- Raster Calculator ---

    # Purpose: Generate the Pixel-difference Map for each image
    # load an before and after image. 
    lyr1 = QgsRasterLayer(frame_data[0])
    lyr2 = QgsRasterLayer(frame_data[1])
    output = r"%s\pixelDifferenceFrame%s.tif" %(workplace, frame_num)
    entries = []
    # set the attributes of lyr1 and lyr2, and them to the entries for calculation
    # first raster
    ras = QgsRasterCalculatorEntry()
    ras.ref = 'ras@1'
    ras.raster = lyr1
    ras.bandNumber = 1
    entries.append(ras)
    # second raster
    ras = QgsRasterCalculatorEntry()
    ras.ref = 'ras@2'
    ras.raster = lyr2
    ras.bandNumber = 1
    entries.append(ras)
    # raster calculator
    calc = QgsRasterCalculator('ras@2 - ras@1', output, 'GTiff', lyr1.extent(), lyr1.width(), lyr1.height(), entries)
    calc.processCalculation()
    # --- Clip ---
    # Purpose: Clip the pixel-difference map to remove the "error edge line"
    # load the extent layer
    path_to_boundary = frame_data[2]
    bnd_layer = QgsVectorLayer(path_to_boundary,"boundary")
    # clip raster by mask layer
    diff_ras = QgsRasterLayer(r"%s\pixelDifferenceFrame%s.tif" %(workplace, frame_num),"diff_map")
    output = r"%s\pixel_differenceClip%s.tif"%(workplace, frame_num)
    crs = str(diff_ras.crs())[31:-1]
    params = {
        'INPUT': diff_ras,
        'MASK': bnd_layer,
        'SOURCE_CRS': crs,
        'TARGET_CRS': QgsCoordinateReferenceSystem(outputCRS),
        'NODATA': None,
        'DATA_TYPE': 6,
        'OUTPUT': output
    }
    processing.run("gdal:cliprasterbymasklayer", params)
    return(output)


pixel_difference_frames = []
# create pixel difference map for each frame
for i in range(number_of_frame):
    output_file = create_pixel_difference_map(image_set[i],i,workplace)
    pixel_difference_frames.append(output_file)



# --- mosaic the outputs to a new raster ---
grid_list = pixel_difference_frames
output = r"%s\mosaicPixelDifference.sdat"%workplace

params = {
    'GRIDS': grid_list,
    'NAME': 'Mosaic',
    'TYPE': 7,
    'RESAMPLING': 0,
    'OVERLAP': 4,
    'BLEND_DIST': 10,
    'MATCH': 0,
    'TARGET_USER_XMIN TARGET_USER_XMAX TARGET_USER_YMIN TARGET_USER_YMAX': None,
    'TARGET_USER_SIZE': 16,
    'TARGET_USER_FITS': 1,
    'TARGET_OUT_GRID': output
}
processing.run("saga:mosaicrasterlayers", params)

# --- Reclassify ---

# Purpose: Reclassify the mosaicked raster by the first threshold: pixel-difference threhsold, to generate the preliminary damage map
clip_ras = QgsRasterLayer(r"%s\mosaicPixelDifference.sdat"%workplace)
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
