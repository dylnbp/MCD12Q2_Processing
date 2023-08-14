# Remotely Sensed Spring Phenology
[Remote sensing phenology](https://www.usgs.gov/special-topics/remote-sensing-phenology/science/remote-sensing-phenology) uses satellites to track seasonal changes in vegetation on regional, continental, and global scales. It is useful to record long-term phenological trends and monitor crop growth, drought severity, wildfire risk, invasive species and pests[1-2]. Vegetation phenology is one of the most sensitive indicators in response to climate change. Satellite-based phenological data play a vital role in assessing the impacts of climate change on ecosystems at multiple scales. 

Spring phenological events, such as the occurrence of first leaf or first bloom, are commonly utilized to indicate start of spring (SOS). Spring phenology governs the development of vegetation in the growing season, while it is influenced by climatic factors such as temperature and precipitation in the non-growing season. Therefore, the study of spring phenology can help understand climate change and and its associated effects on biological processes.

## Phenology product derived from satellite data
The MODIS Land Surface Dynamics Product (MCD12Q2) provides global land surface phenology metrics at 500m spatial resolution and annual time step since 2001. This product is based on time series of the 2-band Enhanced Vegetation Index (EVI2), calculated from MODIS nadir BRDF adjusted surface reflectances. The phenology metrics identify the day of year (DOY) for greenup, midgreenup, peak, maturity, midgreendown, senescence and dormancy over a vegetation cycle. 

The MCD12Q2 data (in HDF4 format) was downloaded from NASA's Land Processes Distributed Active Archive Center (LP DAAC), and its greenup layer (pixel-level SOS metrics in DOY) was used to represent spring phenology. Each SOS metric is defined as the date when EVI2 first crossed 15% of the segment EVI2 amplitude. This project processed SOS metrics from 2001 to 2016, and evaluated trends in spring phenology in Asia.

## Pixel-level analysis of SOS metrics
The timing of spring onset is crucial for understanding the health and changes in ecosystems.\

[Mean of SOS metrics](https://github.com/yan-055/remotely-sensed-spring-phenology/blob/master/Mean%20of%20SOS.png)

[Linear trend of SOS metrics](https://github.com/yan-055/remotely-sensed-spring-phenology/blob/master/Trend%20of%20SOS.png)


## References:
[1] Widespread spring phenology effects on drought recovery of Northern Hemisphere ecosystems \
[2] Investigation of wildfire impacts on land surface phenology from MODIS time series in the western US forests 






