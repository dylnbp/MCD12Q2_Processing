# Remotely Sensed Spring Phenology
[Remote sensing phenology](https://www.usgs.gov/special-topics/remote-sensing-phenology/science/remote-sensing-phenology) uses satellites to track seasonal changes in vegetation on regional, continental, and global scales. It is useful to record long-term phenological trends and monitor crop growth, drought severity, wildfire risk, invasive species and pests[1-4]. Vegetation phenology is one of the most sensitive indicators in response to climate change. Satellite-based phenological data play a vital role in assessing the impacts of climate change on ecosystems at multiple scales. 

Spring phenological events, such as first leaf or first flower, are commonly utilized to indicate start of spring (SOS). Spring phenology governs vegetation development in the growing season, while it is influenced by climatic factors such as temperature and precipitation in the non-growing season. Therefore, the study of spring phenology can help understand climate change and and its associated effects on biological processes.

## Phenology metrics derived from satellite data
The MODIS Land Surface Dynamics Product (MCD12Q2) provides global land surface phenology metrics yearly since 2001 with a spatial resolution of 500m. The phenology metrics refer to the day of year (DOY) for greenup, midgreenup, peak, maturity, midgreendown, senescence and dormancy over a vegetation cycle. This product is derived from time series of the 2-band Enhanced Vegetation Index (EVI2), calculated using MODIS nadir BRDF adjusted surface reflectances. 

The MCD12Q2 data files (in HDF4 format) were downloaded from NASA's Land Processes Distributed Active Archive Center (LP DAAC), and the greenup layer (providing pixel-level SOS metrics in DOY) was used to represent spring phenology. The SOS metric is defined as the date when EVI2 first crossed 15% of the segment EVI2 amplitude. This project processed SOS metrics of 2001 - 2016 over countries in Asia and assessed trends in spring phenology.

Data processing was conducted using Python and R.

Python package: scipy, arcpy, numpy, pandas, gdal, osr, multiprocessing \
R package: getPass, httr, MODIS, gdalUtils, raster, rgdal

## Analysis of SOS metrics
Multi-year SOS metrics were analyzed at the pixel level. For each pixel, the following statistics were calculated:
* Mean of SOS metrics - the timing of spring onset 
* Standard deviation of SOS metrics - the degree of SOS variation
* Linear regression of SOS metrics - the coefficient indicates a spring phenological trend: < 0 means earlier SOS, > 0 means later SOS
* P-value for the linear regression - the significance level is 0.1
<img src="./Mean%20of%20SOS.png" 
     align="center" 
     width="1000" />
<img src="./SD%20of%20SOS.png" 
     align="center" 
     width="1000" />
<img src="./Trend%20of%20SOS.png" 
     align="center" 
     width="1000" />
<img src="./Sig%20trend%20of%20SOS.png" 
     align="center" 
     width="1000" />

## References:
[1] Li, Yang, et al. "Widespread spring phenology effects on drought recovery of Northern Hemisphere ecosystems." *Nature Climate Change* 13.2 (2023): 182-188. \
[2] Wang, Jianmin, and Xiaoyang Zhang. "Investigation of wildfire impacts on land surface phenology from MODIS time series in the western US forests." *ISPRS Journal of Photogrammetry and Remote Sensing* 159 (2020): 281-295. \
[3] Grünig, Marc, et al. "Applying deep neural networks to predict incidence and phenology of plant pests and diseases." *Ecosphere* 12.10 (2021): e03791.\
[4] Fatima, Zartash, et al. "The fingerprints of climate warming on cereal crops phenology and adaptation options." *Scientific Reports* 10.1 (2020): 18013.

