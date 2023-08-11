import arcpy, os, glob
import time
import csv
import re  ## for research
import decimal
import numpy as np
import functions_GreenupProcessing as funStat
from osgeo import gdal, osr
from arcpy import env
from arcpy.sa import *
from scipy import stats

print("________________________________________________________")
print str(time.ctime()) + ("starting the processing")

workingDir = os.getcwd()
print workingDir

inWorkspace = workingDir  # set the workspace based on the location of images
env.workspace = inWorkspace
env.overwriteOutput = True
arcpy.CheckOutExtension("spatial")

greeupStatistics_Input = inWorkspace + "/Step2_GreenupStatistics/"
greeupStatistics_Output = inWorkspace + "/Step3_GreenupPostProcessing/"


###--------------------------------part 1------------------------------------###
### making statistical results in uniform formats
###--------------------------------------------------------------------------###

greeupStatistics_List = glob.glob(greeupStatistics_Input + "/*.tif")
print greeupStatistics_List

for eachRaster in greeupStatistics_List:
    print(eachRaster)
    inRaster = Raster(eachRaster)
    # defining the outfile name
    inputNameList = inRaster.name.split('\\')
    # print inputNameList[0]
    outRasterExtByMask = SetNull(inRaster == 32767, inRaster)
    outRasterName = greeupStatistics_Output + inputNameList[0]
    # print outRasterName
    statIndex = inputNameList[0].split('_GreenupB')[0]
    if (statIndex == 'Trend' or statIndex == 'SD'):
        floatRaster = Float(outRasterExtByMask)
        outDivide = Divide(floatRaster, 100)  # convert the integer to float
        arcpy.CopyRaster_management(outDivide, outRasterName, "DEFAULTS", "", "32767", "", "", "32_BIT_FLOAT")
    else:
        arcpy.CopyRaster_management(outRasterExtByMask, outRasterName, "DEFAULTS", "", "32767", "", "", "16_BIT_SIGNED")


###--------------------------------part 2------------------------------------###
### combining greenup band1 and band1 according values in the previous or current year
###--------------------------------------------------------------------------###

greenupStat_Input = greeupStatistics_Output
B1_MeanGreenupList = glob.glob(greenupStat_Input + "Mean_GreenupB1*.tif")
B1_TrendGreenupList = glob.glob(greenupStat_Input + "Trend_GreenupB1*.tif")
B1_pValueGreenupList = glob.glob(greenupStat_Input + "P_ValueGreenupB1*.tif")
B1_SD_GreenupList = glob.glob(greenupStat_Input + "SD_GreenupB1*.tif")
B2_MeanGreenupList = glob.glob(greenupStat_Input + "Mean_GreenupB2*.tif")
B2_TrendGreenupList = glob.glob(greenupStat_Input + "Trend_GreenupB2*.tif")
B2_pValueGreenupList = glob.glob(greenupStat_Input + "P_ValueGreenupB2*.tif")
B2_SD_GreenupList = glob.glob(greenupStat_Input + "SD_GreenupB2*.tif")

combinedStatistics_Output = greenupStat_Input + "/Combined_B1B2_Final/"

newFileName = Raster(B1_MeanGreenupList[0]).name.split(".")[1]
print newFileName

B1MeanRaster = Raster(B1_MeanGreenupList[0])
B2MeanRaster = Raster(B2_MeanGreenupList[0])
preMeanOutputName = combinedStatistics_Output + "PreYear_Mean_Greenup." + newFileName + ".tif"
curMeanOutputName = combinedStatistics_Output + "CurYear_Mean_Greenup." + newFileName + ".tif"

B1TrendRaster = Raster(B1_TrendGreenupList[0])
B2TrendRaster = Raster(B2_TrendGreenupList[0])
preTrendOutputName = combinedStatistics_Output + "PreYear_Trend_Greenup." + newFileName + ".tif"
curTrendOutputName = combinedStatistics_Output + "CurYear_Trend_Greenup." + newFileName + ".tif"

B1pValueRaster = Raster(B1_pValueGreenupList[0])
B2pValueRaster = Raster(B2_pValueGreenupList[0])
pre_pValueOutputName = combinedStatistics_Output + "PreYear_pValue_Greenup." + newFileName + ".tif"
cur_pValueOutputName = combinedStatistics_Output + "CurYear_pValue_Greenup." + newFileName + ".tif"

B1_SD_Raster = Raster(B1_SD_GreenupList[0])
B2_SD_Raster = Raster(B2_SD_GreenupList[0])
pre_SD_OutputName = combinedStatistics_Output + "PreYear_SD_Greenup." + newFileName + ".tif"
cur_SD_OutputName = combinedStatistics_Output + "CurYear_SD_Greenup." + newFileName + ".tif"

minB1 = B1MeanRaster.minimum
minB2 = B2MeanRaster.minimum

if (minB1 < 0 and minB2 > 0):
    tempB1_0 = Con(B1MeanRaster > 0, 1, 0)
    tempB1_1 = Con(IsNull(tempB1_0), 0, tempB1_0)  ##setting the nodata as 0
    # tempB1_1.save("tempB1_1.tif")
    tempB2_0 = Con(B2MeanRaster > 0, 1)  ##B2Raster has no negative pixel values
    tempB2_1 = Con(IsNull(tempB2_0), 0, tempB2_0)  ##setting the nodata as 0
    # tempB2_1.save("tempB2_1.tif")
    combined_B1B2 = tempB1_1 + tempB2_1  ##add tempB1_1 values (1) to tempB2_1 values (2)
    # extracting pixel values of 1 by setting the double calculated pixel as 0
    tempSingleCurPixel = Con(combined_B1B2 == 2, 0, combined_B1B2)
    singleCurPixel = SetNull(tempSingleCurPixel == 0, tempSingleCurPixel)
    # singleCurPixel.save("singleCurPixel.tif")
    # singleCurPixel is the template of current year (with pixel values of 1)
    tempCurYear_B1 = Con(singleCurPixel == 1, tempB1_1)
    # tempCurYear_B1.save("tempCurYear_B1.tif")
    tempCurYear_B2 = Con(singleCurPixel == 1, tempB2_1)
    # tempCurYear_B2.save("tempCurYear_B2.tif")

    curYear_Mean_Output = Con(tempCurYear_B1 == 1, B1MeanRaster, 0) + Con(tempCurYear_B2 == 1, B2MeanRaster, 0)
    # arcpy.CopyRaster_management(curYear_Mean_Output, curMeanOutputName, "DEFAULTS", "", "32767", "", "", "16_BIT_SIGNED")
    curYear_Trend_Output = Con(tempCurYear_B1 == 1, B1TrendRaster, 0) + Con(tempCurYear_B2 == 1, B2TrendRaster, 0)
    # arcpy.CopyRaster_management(curYear_Trend_Output, curTrendOutputName, "DEFAULTS", "", "32767", "", "", "32_BIT_FLOAT")
    curYear_pValue_Output = Con(tempCurYear_B1 == 1, B1pValueRaster, 0) + Con(tempCurYear_B2 == 1, B2pValueRaster, 0)
    # arcpy.CopyRaster_management(curYear_pValue_Output, cur_pValueOutputName, "DEFAULTS", "", "32767", "", "", "16_BIT_SIGNED")
    curYear_SD_Output = Con(tempCurYear_B1 == 1, B1_SD_Raster, 0) + Con(tempCurYear_B2 == 1, B2_SD_Raster, 0)
    # arcpy.CopyRaster_management(curYear_SD_Output, cur_SD_OutputName, "DEFAULTS", "", "32767", "", "", "32_BIT_FLOAT")
    funStat.export_combinedStat(curYear_Mean_Output, curMeanOutputName, curYear_Trend_Output, curTrendOutputName,
                                curYear_pValue_Output, cur_pValueOutputName, curYear_SD_Output, cur_SD_OutputName)

    # the template of extracting pixel values in the previous year
    tempPreYear = SetNull(tempB1_0 > 0, tempB1_0)

    tempPreYear_Mean = Con(tempPreYear == 0, B1MeanRaster)
    preYear_Mean_Output = tempPreYear_Mean + 365
    preYear_Trend_Output = Con(tempPreYear == 0, B1TrendRaster)
    preYear_pValue_Output = Con(tempPreYear == 0, B1pValueRaster)
    preYear_SD_Output = Con(tempPreYear == 0, B1_SD_Raster)
    funStat.export_combinedStat(preYear_Mean_Output, preMeanOutputName, preYear_Trend_Output, preTrendOutputName,
                                preYear_pValue_Output, pre_pValueOutputName, preYear_SD_Output, pre_SD_OutputName)

elif (minB1 > 0 and minB2 < 0):
    tempB1_0 = Con(B1MeanRaster > 0, 1)
    tempB1_1 = Con(IsNull(tempB1_0), 0, tempB1_0)  ##setting the nodata as 0
    tempB2_0 = Con(B2MeanRaster > 0, 1, 0)  ##B1Raster has no negative pixel values
    tempB2_1 = Con(IsNull(tempB2_0), 0, tempB2_0)  ##setting the nodata as 0
    combined_B1B2 = tempB1_1 + tempB2_1  ##add tempB1_1 values (1) to tempB2_1 values (2)
    # extracting pixel values of 1 by setting the double calculated pixel as 0
    tempSingleCurPixel = Con(combined_B1B2 == 2, 0, combined_B1B2)
    singleCurPixel = SetNull(tempSingleCurPixel == 0, tempSingleCurPixel)
    # singleCurPixel is the template of current year (with pixel values of 1)
    tempCurYear_B1 = Con(singleCurPixel == 1, tempB1_1)
    tempCurYear_B2 = Con(singleCurPixel == 1, tempB2_1)

    curYear_Mean_Output = Con(tempCurYear_B1 == 1, B1MeanRaster, 0) + Con(tempCurYear_B2 == 1, B2MeanRaster, 0)
    curYear_Trend_Output = Con(tempCurYear_B1 == 1, B1TrendRaster, 0) + Con(tempCurYear_B2 == 1, B2TrendRaster, 0)
    curYear_pValue_Output = Con(tempCurYear_B1 == 1, B1pValueRaster, 0) + Con(tempCurYear_B2 == 1, B2pValueRaster, 0)
    curYear_SD_Output = Con(tempCurYear_B1 == 1, B1_SD_Raster, 0) + Con(tempCurYear_B2 == 1, B2_SD_Raster, 0)
    funStat.export_combinedStat(curYear_Mean_Output, curMeanOutputName, curYear_Trend_Output, curTrendOutputName,
                                curYear_pValue_Output, cur_pValueOutputName, curYear_SD_Output, cur_SD_OutputName)

    # template for extracting pixel values in the previous year
    tempPreYear = SetNull(tempB2_0 > 0, tempB2_0)
    tempPreYear_Mean = Con(tempPreYear == 0, B2MeanRaster)
    # tempPreYear_Mean.save ("temPreMean.tif")

    preYear_Mean_Output = tempPreYear_Mean + 365
    preYear_Trend_Output = Con(tempPreYear == 0, B2TrendRaster)
    preYear_pValue_Output = Con(tempPreYear == 0, B2pValueRaster)
    preYear_SD_Output = Con(tempPreYear == 0, B2_SD_Raster)
    funStat.export_combinedStat(preYear_Mean_Output, preMeanOutputName, preYear_Trend_Output, preTrendOutputName,
                                preYear_pValue_Output, pre_pValueOutputName, preYear_SD_Output, pre_SD_OutputName)

elif (minB1 < 0 and minB2 < 0):  ## here hasn't been examined using data
    tempB1_0 = Con(B1MeanRaster > 0, 1, -1)
    tempB1_1 = Con(IsNull(tempB1_0), 0, tempB1_0)  ##setting the nodata as 0
    tempB2_0 = Con(B2MeanRaster > 0, 1, -1)  ##B2Raster has no negative pixel values
    tempB2_1 = Con(IsNull(tempB2_0), 0, tempB2_0)  ##setting the nodata as 0
    combined_B1B2 = tempB1_1 + tempB2_1  ##add tempB1_1 values (1) to tempB2_1 values (2)
    # extracting pixel values of 1 by setting the double calculated pixel as 0
    tempSingleCurPixel = Con(combined_B1B2 == 2, 0, combined_B1B2)
    singleCurPixel = SetNull(tempSingleCurPixel == 0, tempSingleCurPixel)
    # singleCurPixel is the template of current year (with pixel values of 1)
    tempCurYear_B1 = Con(singleCurPixel == 1, tempB1_1)
    tempCurYear_B2 = Con(singleCurPixel == 1, tempB2_1)

    curYear_Mean_Output = Con(tempCurYear_B1 == 1, B1MeanRaster, 0) + Con(tempCurYear_B2 == 1, B2MeanRaster, 0)
    curYear_Trend_Output = Con(tempCurYear_B1 == 1, B1TrendRaster, 0) + Con(tempCurYear_B2 == 1, B2TrendRaster, 0)
    curYear_pValue_Output = Con(tempCurYear_B1 == 1, B1pValueRaster, 0) + Con(tempCurYear_B2 == 1, B2pValueRaster, 0)
    curYear_SD_Output = Con(tempCurYear_B1 == 1, B1_SD_Raster, 0) + Con(tempCurYear_B2 == 1, B2_SD_Raster, 0)
    funStat.export_combinedStat(curYear_Mean_Output, curMeanOutputName, curYear_Trend_Output, curTrendOutputName,
                                curYear_pValue_Output, cur_pValueOutputName, curYear_SD_Output, cur_SD_OutputName)

    # template for extracting pixel values in the previous year
    tempSinglePrePixel = Con(combined_B1B2 == -2, 0, combined_B1B2)
    singlePrePixel = SetNull(tempSinglePrePixel == 0, tempSinglePrePixel)
    tempPreYear_B1 = Con(singlePrePixel == -1, tempB1_1)
    tempPreYear_B2 = Con(singlePrePixel == -1, tempB2_1)

    preYear_Mean_Output = tempPreYear_Mean + 365
    preYear_Trend_Output = Con(tempCurYear_B1 == -1, B1TrendRaster, 0) + Con(tempCurYear_B2 == -1, B2TrendRaster, 0)
    preYear_pValue_Output = Con(tempCurYear_B1 == -1, B1pValueRaster, 0) + Con(tempCurYear_B2 == -1, B2pValueRaster, 0)
    preYear_SD_Output = Con(tempCurYear_B1 == -1, B1_SD_Raster, 0) + Con(tempCurYear_B2 == -1, B2_SD_Raster, 0)
    funStat.export_combinedStat(preYear_Mean_Output, preMeanOutputName, preYear_Trend_Output, preTrendOutputName,
                                preYear_pValue_Output, pre_pValueOutputName, preYear_SD_Output, pre_SD_OutputName)
else:  ## here hasn't been examined using data
    tempB1_0 = Con(B1MeanRaster > 0, 1)
    tempB1_1 = Con(IsNull(tempB1_0), 0, tempB1_0)  ##setting the nodata as 0
    tempB2_0 = Con(B2MeanRaster > 0, 1)  ##B2Raster has no negative pixel values
    tempB2_1 = Con(IsNull(tempB2_0), 0, tempB2_0)  ##setting the nodata as 0
    combined_B1B2 = tempB1_1 + tempB2_1  ##add tempB1_1 values (1) to tempB2_1 values (2)
    # extracting pixel values of 1 by setting the double calculated pixel as 0
    tempSingleCurPixel = Con(combined_B1B2 == 2, 0, combined_B1B2)
    singleCurPixel = SetNull(tempSingleCurPixel == 0, tempSingleCurPixel)
    # singleCurPixel is the template of current year (with pixel values of 1)
    tempCurYear_B1 = Con(singleCurPixel == 1, tempB1_1)
    tempCurYear_B2 = Con(singleCurPixel == 1, tempB2_1)

    curYear_Mean_Output = Con(tempCurYear_B1 == 1, B1MeanRaster, 0) + Con(tempCurYear_B2 == 1, B2MeanRaster, 0)
    curYear_Trend_Output = Con(tempCurYear_B1 == 1, B1TrendRaster, 0) + Con(tempCurYear_B2 == 1, B2TrendRaster, 0)
    curYear_pValue_Output = Con(tempCurYear_B1 == 1, B1pValueRaster, 0) + Con(tempCurYear_B2 == 1, B2pValueRaster, 0)
    curYear_SD_Output = Con(tempCurYear_B1 == 1, B1_SD_Raster, 0) + Con(tempCurYear_B2 == 1, B2_SD_Raster, 0)
    funStat.export_combinedStat(curYear_Mean_Output, curMeanOutputName, curYear_Trend_Output, curTrendOutputName,
                                curYear_pValue_Output, cur_pValueOutputName, curYear_SD_Output, cur_SD_OutputName)
print("________________________________________________________")
print str(time.ctime()) + ("ending the processing")
