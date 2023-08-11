library(MODIS)
library(gdalUtils)
library(raster)
library(rgdal)

## We'll pre-check to make sure there is a valid GDAL install and that raster and rgdal are also installed.
#gdal_setInstallation()
# valid_install <- !is.null(getOption("gdalUtils_gdalPath"))
# if(require(raster) && require(rgdal) && valid_install)
# {  
#   writing codes here
# }
directory_name <- getwd()
print(directory_name)

downloadedData <- "Downloaded_MLCD_V6_Data"
dl_dir <- paste(directory_name,"\\",downloadedData,sep="")   # Set dir to download files to
setwd(dl_dir)   

##files <- dir(pattern = ".hdf")

hdfFiles <- list.files(dl_dir, pattern=".hdf")
#print(hdfFiles)

tiffNameList <- c()
NumCycle_List <- c()
GreenUpB1_List <- c()
GreenUpB2_List <- c()
QA_AllB1_List <- c()
QA_AllB2_List <- c()
for(i in 1:length(hdfFiles)){
  originalName <- head(strsplit(hdfFiles[i], "[.]")[[1]], n = 3)
  tiffName <- paste(originalName[1],".",originalName[2],".",originalName[3],".tif",sep = "")
  tiffNameList[i] <- tiffName
  tempNumCycle <- paste("NumCycle.",originalName[1],".",originalName[2],".",originalName[3],".tif",sep = "")
  NumCycle_List[i] <- tempNumCycle
  
  tempGreenupB1 <- paste("GreenupB1.",originalName[1],".",originalName[2],".",originalName[3],".tif",sep = "")
  GreenUpB1_List[i] <- tempGreenupB1  
  tempGreenupB2 <- paste("GreenupB2.",originalName[1],".",originalName[2],".",originalName[3],".tif",sep = "")
  GreenUpB2_List[i] <- tempGreenupB2 
  
  tempQA_AllB1 <- paste("QA_AllB1.",originalName[1],".",originalName[2],".",originalName[3],".tif",sep = "")
  QA_AllB1_List[i] <- tempQA_AllB1 
  tempQA_AllB2 <- paste("QA_AllB2.",originalName[1],".",originalName[2],".",originalName[3],".tif",sep = "")
  QA_AllB2_List[i] <- tempQA_AllB2 
}
write.table(tiffNameList, file="Tiff_NameList.csv",col.names=F,row.names = F) 


sdsIndex.NumCycle <- 1
sdsIndex.Greenup <- 2 # for MCD12Q2:Greenup, SUBDATASET_2_DESC=[2400x2400x2] Greenup MCD12Q2 (16-bit integer)"  
sdsIndex.QA_All <- 12
for(i in 1:length(hdfFiles)){
  print(i)
  #gdalinfo(hdfFiles[i])
  sdsDatasets <- get_subdatasets(hdfFiles[i])
  ## b=1: select band; tr=c(500,500): resolution; r="nearest":resample method
  gdal_translate(sdsDatasets[sdsIndex.NumCycle], dst_dataset = tiffNameList[i], t=c(500,500)) 
  gdalwarp(tiffNameList[i], NumCycle_List[i], s_srs='+proj=sinu +a=6371007.181 +b=6371007.181 +units=m', t_srs='EPSG:4326', overwrite = T)
  
  gdal_translate(sdsDatasets[sdsIndex.Greenup], dst_dataset = tiffNameList[i], t=c(500,500),b=1) 
  gdalwarp(tiffNameList[i], GreenUpB1_List[i], s_srs='+proj=sinu +a=6371007.181 +b=6371007.181 +units=m', t_srs='EPSG:4326', overwrite = T)
  gdal_translate(sdsDatasets[sdsIndex.Greenup], dst_dataset = tiffNameList[i], t=c(500,500),b=2) 
  gdalwarp(tiffNameList[i], GreenUpB2_List[i], s_srs='+proj=sinu +a=6371007.181 +b=6371007.181 +units=m', t_srs='EPSG:4326', overwrite = T)
  
  gdal_translate(sdsDatasets[sdsIndex.QA_All], dst_dataset = tiffNameList[i], t=c(500,500), b=1) 
  gdalwarp(tiffNameList[i], QA_AllB1_List[i], s_srs='+proj=sinu +a=6371007.181 +b=6371007.181 +units=m', t_srs='EPSG:4326', overwrite = T)
  gdal_translate(sdsDatasets[sdsIndex.QA_All], dst_dataset = tiffNameList[i], t=c(500,500), b=2) 
  gdalwarp(tiffNameList[i], QA_AllB2_List[i], s_srs='+proj=sinu +a=6371007.181 +b=6371007.181 +units=m', t_srs='EPSG:4326', overwrite = T)

}

