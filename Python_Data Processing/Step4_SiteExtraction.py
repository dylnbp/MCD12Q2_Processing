import arcpy, os, glob
import time
import csv
import decimal
import numpy as np
import functions_GreenupProcessing as funStat
from osgeo import gdal, osr
from arcpy import env
from arcpy.sa import *
from scipy import stats
import pandas as pd
import multiprocessing

print("________________________________________________________")
print str(time.ctime()) + ("starting the processing")

inWorkspace = os.getcwd()  # set the workspace based on the location of images
siteStat_Output = inWorkspace + "/Step4_SiteExtraction"
os.chdir(siteStat_Output)  ## resetting the workspace
env.workspace = os.getcwd()
# print env.workspace
env.overwriteOutput = True
arcpy.CheckOutExtension("spatial")

StatFinal_Input = inWorkspace + "/Step3_GreenupPostProcessing/Combined_B1B2_Final/"

Cur_MeanGreenupList = glob.glob(StatFinal_Input + "CurYear_Mean_*.tif")
Cur_TrendGreenupList = glob.glob(StatFinal_Input + "CurYear_Trend_*.tif")
Cur_pValueGreenupList = glob.glob(StatFinal_Input + "CurYear_pValue_*.tif")
Cur_SD_GreenupList = glob.glob(StatFinal_Input + "CurYear_SD_*.tif")
Pre_MeanGreenupList = glob.glob(StatFinal_Input + "PreYear_Mean_*.tif")
Pre_TrendGreenupList = glob.glob(StatFinal_Input + "PreYear_Trend_*.tif")
Pre_pValueGreenupList = glob.glob(StatFinal_Input + "PreYear_pValue_*.tif")
Pre_SD_GreenupList = glob.glob(StatFinal_Input + "PreYear_SD_*.tif")

allSites_Input = inWorkspace + "/study_sites/"
allsitesShp = glob.glob(allSites_Input + "*.shp")
nameList = Cur_MeanGreenupList[0].split("\\")
studyAreaName = nameList[-1].split(".")[-2]

studyArea_Input = inWorkspace + "/" + studyAreaName + "/"
studyAreaList = glob.glob(studyArea_Input + "*.shp")

## select sites which are within a county polygon and extract values (SOS mean and trend) to these points
siteExtract_OutputName = studyAreaList[0].split("\\")[-1].replace(".shp", "_Sites.shp")
arcpy.MakeFeatureLayer_management(allsitesShp[0], 'allSites_lyr')
arcpy.SelectLayerByLocation_management('allSites_lyr', 'intersect', studyAreaList[0])
matchcount = int(arcpy.GetCount_management('allSites_lyr')[0])
if matchcount == 0:
    print('no features matched spatial and attribute criteria')
else:
    arcpy.CopyFeatures_management('allSites_lyr', siteExtract_OutputName)
## extracting mean and trend values and specify the field name
inRasterList = [[Cur_MeanGreenupList[0], "FirMean"], [Cur_TrendGreenupList[0], "FirTrend"],
                [Pre_MeanGreenupList[0], "SecMean"], [Pre_TrendGreenupList[0], "SecTrend"]]
ExtractMultiValuesToPoints(siteExtract_OutputName, inRasterList, "NONE")

## considering multiple processings when there are multiple buffer requirements
# setting arguments for using ExtractSiteValues function
buff_Threshold = 20
erase_Threshold = 5
pValue_Threshold = 0 ## 0, 1, 5, 50
SD_Threshold = 30

funStat.ExtractSiteValues("Fir", studyAreaList[0], siteExtract_OutputName, Cur_MeanGreenupList[0],
                          Cur_TrendGreenupList[0], Cur_pValueGreenupList[0], Cur_SD_GreenupList[0],
                          buff_Threshold, erase_Threshold, pValue_Threshold, SD_Threshold)

# funStat.ExtractSiteValues("Sec", studyAreaList[0], siteExtract_OutputName, Pre_MeanGreenupList[0],
#                           Pre_TrendGreenupList[0], Pre_pValueGreenupList[0], Pre_SD_GreenupList[0],
#                           buff_Threshold, erase_Threshold, pValue_Threshold, SD_Threshold)

print str(time.ctime()) + ("ending the processing")



## creating buffer areas around sites
buff_TH = 5
strBuff_TH = str(buff_TH) + " Kilometers"
erase_TH = 0 ## 0 or Integer, but should be < buff_Th
strErase_TH = str(erase_TH) + " Kilometers"
pValue_TH = 50  ## 0, 1, 5, 50
SD_TH = 30 ## NONE or Integer

sites_Input = siteExtr_OutputName
SOS_Input = Cur_MeanGreenupList[0]
trend_Input = Cur_TrendGreenupList[0]
pValue_Input = Cur_pValueGreenupList[0]
sd_Input = Cur_SD_GreenupList[0]

## generating the buffer
sitesBuff_OutputName = sites_Input.replace(".shp","_Buff.shp")
if(erase_TH > 0 and erase_TH < buff_TH):
    arcpy.Buffer_analysis(sites_Input, "tempBuffer.shp", strBuff_TH)
    arcpy.Buffer_analysis(sites_Input, "tempErase.shp", strErase_TH)
    arcpy.Erase_analysis("tempBuffer.shp", "tempErase.shp", sitesBuff_OutputName)
elif(erase_TH == 0):
    arcpy.Buffer_analysis(sites_Input, sitesBuff_OutputName, strBuff_TH)
else:
    print ("Please using an effective radius to define buffer!")

meanBuffPoint_OutputName = studyAreaList[0].split("\\")[-1].replace(".shp","_Sites_Buff_MeanPoint.shp")
trendBuffPoint_OutputName = studyAreaList[0].split("\\")[-1].replace(".shp","_Sites_Buff_TrendPoint.shp")

suffixMean = str(buff_TH) + "_" + str(erase_TH) + "_" + str(pValue_TH) + "_" + str(SD_TH) + "_Mean.shp"
#print suffixMean
suffixTrend = str(buff_TH) + "_" + str(erase_TH) + "_" + str(pValue_TH) + "_" + str(SD_TH) + "_Trend.shp"
meanJoin_OutputName = studyAreaList[0].split("\\")[-1].replace(".shp", suffixMean)
trendJoin_OutputName = studyAreaList[0].split("\\")[-1].replace(".shp", suffixTrend)

#inZoneData = sitesBuff_OutputName
#zoneField = "place_name"

if(pValue_TH == 0 and SD_TH == 0):
    meanBuff_Extract = ExtractByMask(SOS_Input, sitesBuff_OutputName)
    trendBuff_Extract = ExtractByMask(trend_Input, sitesBuff_OutputName)
    #arcpy.CopyRaster_management(meanBuff_Extract, "tempMeanBuffer.tif", "DEFAULTS", "", "32767", "", "", "16_BIT_SIGNED")
    #arcpy.CopyRaster_management(trendBuff_Extract, "tempTrendBuffer.tif", "DEFAULTS", "", "32767", "", "", "32_BIT_FLOAT")
    arcpy.RasterToPoint_conversion(meanBuff_Extract, meanBuffPoint_OutputName, "VALUE")
    arcpy.RasterToPoint_conversion(trendBuff_Extract, trendBuffPoint_OutputName, "VALUE")
    arcpy.SpatialJoin_analysis(meanBuffPoint_OutputName, sitesBuff_OutputName, meanJoin_OutputName,"JOIN_ONE_TO_MANY")
    arcpy.SpatialJoin_analysis(trendBuffPoint_OutputName, sitesBuff_OutputName, trendJoin_OutputName,"JOIN_ONE_TO_MANY")
    #meanStat = ZonalStatisticsAsTable(inZoneData, zoneField, meanBuff_Extract, meanStat_OutputName, "DATA", "ALL")
    #trendStat = ZonalStatisticsAsTable(inZoneData, zoneField, "tempIntTrend.tif", trendStat_OutputName, "DATA", "ALL")
elif(pValue_TH == 0 and SD_TH > 0):
    meanBuff_Extract = ExtractByMask(SOS_Input, sitesBuff_OutputName)
    trendBuff_Extract = ExtractByMask(trend_Input, sitesBuff_OutputName)
    sdBuff_Extract = ExtractByMask(sd_Input, sitesBuff_OutputName)
    mean_sdFilter = Con(sdBuff_Extract <= SD_TH, meanBuff_Extract)
    trend_sdFilter = Con(sdBuff_Extract <= SD_TH, trendBuff_Extract)
    #arcpy.CopyRaster_management(mean_sdFilter, "tempMean_SD_FilterBuff.tif", "DEFAULTS", "", "32767", "", "", "16_BIT_SIGNED")
    #arcpy.CopyRaster_management(trend_sdFilter, "tempTrend_SD_FilterBuff.tif", "DEFAULTS", "", "32767", "", "", "32_BIT_FLOAT")
    arcpy.RasterToPoint_conversion(mean_sdFilter, meanBuffPoint_OutputName, "VALUE")
    arcpy.RasterToPoint_conversion(trend_sdFilter, trendBuffPoint_OutputName, "VALUE")
    arcpy.SpatialJoin_analysis(meanBuffPoint_OutputName, sitesBuff_OutputName, meanJoin_OutputName,"JOIN_ONE_TO_MANY")
    arcpy.SpatialJoin_analysis(trendBuffPoint_OutputName, sitesBuff_OutputName, trendJoin_OutputName,"JOIN_ONE_TO_MANY")
elif(pValue_TH >0 and SD_TH == 0):
    meanBuff_Extract = ExtractByMask(SOS_Input, sitesBuff_OutputName)
    trendBuff_Extract = ExtractByMask(trend_Input, sitesBuff_OutputName)
    pValueBuff_Extract = ExtractByMask(pValue_Input, sitesBuff_OutputName)
    if(pValue_TH == 1):
        mean_pValueFilter = Con(pValueBuff_Extract == 1, meanBuff_Extract)
        trend_pValueFilter = Con(pValueBuff_Extract == 1, trendBuff_Extract)
    elif(pValue_TH == 5):
        mean_pValueFilter = Con((pValueBuff_Extract == 1) | (pValueBuff_Extract == 5), meanBuff_Extract)
        trend_pValueFilter = Con((pValueBuff_Extract == 1) | (pValueBuff_Extract == 5), trendBuff_Extract)
    elif(pValue_TH == 50):
        mean_pValueFilter = Con(pValueBuff_Extract != 0, meanBuff_Extract)
        trend_pValueFilter = Con(pValueBuff_Extract != 0, trendBuff_Extract)
    else:
        print "Invalid threshold ! "
        exit(1)
    arcpy.RasterToPoint_conversion(mean_pValueFilter, meanBuffPoint_OutputName, "VALUE")
    arcpy.RasterToPoint_conversion(trend_pValueFilter, trendBuffPoint_OutputName, "VALUE")
    arcpy.SpatialJoin_analysis(meanBuffPoint_OutputName, sitesBuff_OutputName, meanJoin_OutputName,"JOIN_ONE_TO_MANY")
    arcpy.SpatialJoin_analysis(trendBuffPoint_OutputName, sitesBuff_OutputName, trendJoin_OutputName,"JOIN_ONE_TO_MANY")
elif(pValue_TH >0 and SD_TH > 0):
    meanBuff_Extract = ExtractByMask(SOS_Input, sitesBuff_OutputName)
    trendBuff_Extract = ExtractByMask(trend_Input, sitesBuff_OutputName)
    pValueBuff_Extract = ExtractByMask(pValue_Input, sitesBuff_OutputName)
    sdBuff_Extract = ExtractByMask(sd_Input, sitesBuff_OutputName)
    if (pValue_TH == 1):
        temp_pValue_0 = Con(pValueBuff_Extract == 1, 1, 0)
        temp_pValue = Con(IsNull(temp_pValue_0), 0, temp_pValue_0)
    elif (pValue_TH == 5):
        temp_pValue_0 = Con((pValueBuff_Extract == 1) | (pValueBuff_Extract == 5), 1, 0)
        temp_pValue = Con(IsNull(temp_pValue_0), 0, temp_pValue_0)
    elif (pValue_TH == 50):
        temp_pValue_0 = Con(pValueBuff_Extract != 0, 1, 0)
        temp_pValue = Con(IsNull(temp_pValue_0), 0, temp_pValue_0)
    temp_SD_0 = Con(sdBuff_Extract <= SD_TH, 1,0)
    temp_SD = Con(IsNull(temp_SD_0), 0, temp_SD_0)

    filterTemplate = temp_pValue + temp_SD
    mean_Filter = Con(filterTemplate == 2, meanBuff_Extract)
    trend_Filter = Con(filterTemplate == 2, trendBuff_Extract)

    arcpy.RasterToPoint_conversion(mean_Filter, meanBuffPoint_OutputName, "VALUE")
    arcpy.RasterToPoint_conversion(trend_Filter, trendBuffPoint_OutputName, "VALUE")
    arcpy.SpatialJoin_analysis(meanBuffPoint_OutputName, sitesBuff_OutputName, meanJoin_OutputName,"JOIN_ONE_TO_MANY")
    arcpy.SpatialJoin_analysis(trendBuffPoint_OutputName, sitesBuff_OutputName, trendJoin_OutputName,"JOIN_ONE_TO_MANY")

