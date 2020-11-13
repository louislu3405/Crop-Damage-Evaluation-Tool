# Crop-Damage-Evaluation-Tool
The Crop Damage Evaluation Tool takes advantages of satellite images to assess the crop damaged by severe weather events such as storm, hail, etc.

This tool uses:
* **QGIS 3.10**
* **Google Earth Engine**
* **Sentinel-1 Toolbox (SNAP)**

The inputs of this tool are:
* **Satellite images**: satellite images before and after the area of interest
* **pixel-difference threshold**: to decide how much change in value will pixels be regarded as damaged area
* **area threshold**: to filter out small isolate groups of pixels. In reality, it is unreasonable to have a farm with only 100 square meter. Use this parameter to filter out small damaged area.

The output of this tool are:
* **Crop Damaged Map (raster)**
* **Crop Damaged Map (vector)**
* **Estimated Damaged Area**



To use the Crop Evaluation Tool, we need to first decide what kind of satellite images we want to use. Is it optical satellite image, or is it synthetic apreture radar (SAR) satellite images? This tool provides us to choose any optical satellite images or Sentinel-1 SAR images as the input.

## Sentinel-1 SAR images as input

### Image Preprocessing
If we want to use Sentinel-1 SAR images as the input, first we need to preprocess the Sentinel-1 SAR images. The image we should prepare for this tool is the GRDH data. Through the [ASF Data Search Website](https://search.asf.alaska.edu/#/) we can search and get any Sentinel-1 SAR images we want. Make sure you choose the file type as **GRDH(GRD-HD)** because later we will use [Sentinel-1 Toolbox (SNAP)](http://step.esa.int/main/download/) to process the GRDH images that we've downloaded. 

Next, we download and install [Sentinel-1 Toolbox (SNAP)](http://step.esa.int/main/download/). Also, download the **GRDH_process_For_Crops.xml** in this repository. This is a graph that we will use in SNAP later.

After the installation is done, open SNAP, go to **Batch Processing** on the tool bar. Go to File/Load Graph, and select the **GRDH_process_For_Crops.xml** as the input graph. Now, we leave all the parameter as default and only adjust the output directory. Once everything is done, hit the Run button.

The output file of this step is the preprocessed Sentinel-1 SAR images that is ready for use!

### Run the Crop Damage Evaluation Tool with Sentinel-1 SAR images
First, we download the **QGIS py console code customize2.0.py** from this repository. The code in this python file must be run in **QGIS Python Console**. Next, Open the **QGIS desktop with GRASS** on your desktop, and copy & paste all the code in QGIS py console code customized2.0.py to the python console. QGIS will automatically ask us to enter the inputs and run the process. 

Inputs that we need to enter for the tools are:
* **Number of Frames to Be Used**: The number of frames (images) that we are planning to use to cover the whole area of interest
* **Working Folder**: the folder to save the final result and the intermediate files
* **Pixel-Difference Threshold**: The threshold that defines how much change in pixel value will the pixel be considered as damaged crop. 
* **Area Threshold**: To filter small farms (area lower than the threshold) that should not exist in reality
* **Output CRS**: The coordinate system for the output files

The following inputs must be entered iterately. The before and after image should share the same path and frame. The only difference is their acquired date.
* **The "Before" Image of a frame**
* **The "After" Image of a frame**
* **The boundary file of a frame**: To remove the error edge line due to the different positions of Before and After image. This file must be manually drawn.

To give an idea about how the thresholds should be set, here is an example of my previous work. I use the tool to detect the crop damage caused by a derecho storm in Iowa in 08.2020. The Pixel-Difference Threshold was set to 1.5, and the Area threshold was set to 10,000(m2). The unit of the area threshold is decide by the assigned output coordinate system. We can play around with different thresholds to check which thresholds best fit our observe or our data.

The output of this tool is a raster crop damage map and a vector crop damage map. We can sum the area of the vector crop damage map to get the final estimated crop damaged area. 

## Optical Satellites generated DVDI images as input

The tool can only process a single frame for now. If we have a large ROI, consider using Sentinel-1 SAR image rather than DIDV images.

### Image Preprocessing
The image preprocessing for DVDI images is simple, we can just use [Google Earth Engine (GEE)](https://earthengine.google.com/) to finish the task. The first thing we need to do is get the authorization from Google to use GEE. Next, we download the GEE DVDI.js to get the JavaScript code for Google Earth Engine. Before we dump the code into GEE, we need to modify the first few lines of codes in order to fit our region of interest. The codes include dates, region of interest, export description, and export folder. After the code is run, click the task tab on the top right and export the preprocessed DVDI image to our google drive. 

### Run the Crop Damage Evaluation Tool with DVDI images
First, we go to this GitHub Repository and download the **QGIS py console code GEE 1.0.py**. This is the file that we can use for analyzing and generating the crop damage map. The usage of this tool is similar to the usage of the SAR tool. Copy and paste the code to python console in **QGIS with GRASS**, several windows will pop up and ask you to enter the inputs. After entering all the required inputs, the tool will start to run and we will get the output!

