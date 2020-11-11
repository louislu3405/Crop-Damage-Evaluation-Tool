# Crop-Damage-Evaluation-Tool
The Crop Damage Evaluation Tool takes advantages of satellite images to assess the crop damaged by severe weather events such as storm, hail, etc.

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
