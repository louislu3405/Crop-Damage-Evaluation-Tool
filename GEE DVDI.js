var Des_Moines =  // Remember to modify the Des_Moines to your ROI.
    /* color: #d63000 */
    /* displayProperties: [
      {
        "type": "rectangle"
      }
    ] */
    ee.Geometry.Polygon(
        [[[-93.81231209708844, 41.72078831226466],
          [-93.81231209708844, 41.51237246545039],
          [-93.43053719474469, 41.51237246545039],
          [-93.43053719474469, 41.72078831226466]]], null, false),
    L8 = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR");


var L8_bnd = L8.filterBounds(Des_Moines);  //adjust the ROI(Des_Moines) to your own ROI
var date_start = '07-01';  // adjust date_start and date_end. The images between the date since 2013 will be
var date_end = '08-07';    // used for making the historical NDVI max and medium.
var L8_after_storm = L8_bnd.filterDate('2020-08-11','2020-08-12').first();  // modify the date to find a suitable 
                                                                            // date to calculate mVCIb
var L8_before_storm = L8_bnd.filterDate('2020-07-01','2020-08-09').first(); // modify the date to find a suitable
                                                                            // date to calculate mVCIa
var export_description = ''; // change to your export description for the output DVDI image
var export_folder = ''; // change to your desinated export folder

// create imageCollection for each year
var L8_2013_col = L8_bnd.filterDate(('2013-' + date_start), ('2013-' + date_end));
var L8_2014_col = L8_bnd.filterDate(('2014-' + date_start), ('2014-' + date_end));
var L8_2015_col = L8_bnd.filterDate(('2015-' + date_start), ('2015-' + date_end));
var L8_2016_col = L8_bnd.filterDate(('2016-' + date_start), ('2016-' + date_end));
var L8_2017_col = L8_bnd.filterDate(('2017-' + date_start), ('2017-' + date_end));
var L8_2018_col = L8_bnd.filterDate(('2018-' + date_start), ('2018-' + date_end));
var L8_2019_col = L8_bnd.filterDate(('2019-' + date_start), ('2019-' + date_end));
var L8_2020_col = L8_bnd.filterDate(('2020-' + date_start), ('2020-' + date_end));

// add each year's imageCollection to the same collection to generate the historical NDVI
var L8_2013_to_2020_July = L8_2013_col.merge(L8_2014_col)
                                      .merge(L8_2015_col)
                                      .merge(L8_2016_col)
                                      .merge(L8_2017_col)
                                      .merge(L8_2018_col)
                                      .merge(L8_2019_col)
                                      .merge(L8_2020_col);
                                      
// NDVI function
var addNDVI = function(image) {
  var ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI');
  return image.addBands(ndvi);
};

// add NDVI to every image in the historical image collection
var history_withNDVI = L8_2013_to_2020_July.map(addNDVI);
//print(history_withNDVI.select('NDVI'));

// calcuate the NDVImax and NDVImedian
var NDVI_median = history_withNDVI.select('NDVI').median();
var NDVI_max = history_withNDVI.select('NDVI').max();
//Map.addLayer(NDVI_median);
//Map.addLayer(NDVI_max);
print(NDVI_median);
print(NDVI_max);

// calulate the NDVI for image after derecho
var NDVI_current = addNDVI(L8_after_storm).select('NDVI');
Map.addLayer(NDVI_current,null,'After NDVI');
var NDVI_before = addNDVI(L8_before_storm).select('NDVI');
Map.addLayer(NDVI_before,null,'Before NDVI');

// calculate the mVCIa and mVCIb
var mVCIb = NDVI_current.subtract(NDVI_median).divide(NDVI_max.subtract(NDVI_median));
var mVCIa = NDVI_before.subtract(NDVI_median).divide(NDVI_max.subtract(NDVI_median));

//calculate DVDI
var DVDI = mVCIa.subtract(mVCIb);
Map.addLayer(DVDI,null,'DVDI');

// export the DVDI image
Export.image.toDrive({
  image:DVDI,
  description:export_description,
  folder:export_folder,
  scale:30,
  maxPixels:1e10,
});