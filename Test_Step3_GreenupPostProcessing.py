import arcpy,os,glob
import time
import csv
import re ## for research
import decimal
import numpy as np
import functions_GreenupProcessing as funStat
from osgeo import gdal, osr
from arcpy import env
from arcpy.sa import *
from scipy import stats

print("________________________________________________________")
print str(time.ctime())+("starting the processing")

workingDir = os.getcwd()
print workingDir

inWorkspace = workingDir  # set the workspace based on the location of images
env.workspace = inWorkspace
env.overwriteOutput = True
arcpy.CheckOutExtension("spatial")

###--------------------------------part 1------------------------------------###
### making statistical results in uniform formats
###--------------------------------------------------------------------------###

greeupStatistics_Input = inWorkspace+"/Test_Step2_GreenupStatistics/"
greeupStatistics_Output = inWorkspace+"/Test_Step3_GreenupPostProcessing/"

greeupStatistics_List = glob.glob(greeupStatistics_Input + "/*.tif")
print greeupStatistics_List

for eachRaster in greeupStatistics_List:
    print(eachRaster)
    inRaster = Raster(eachRaster)
    # defining the outfile name
    inputNameList = inRaster.name.split('\\')
    #print inputNameList[0]
    outRasterExtByMask = SetNull(inRaster == 32767, inRaster)
    outRasterName = greeupStatistics_Output + inputNameList[0]
    #print outRasterName
    statIndex = inputNameList[0].split('_GreenupB')[0]
    if(statIndex == 'Trend' or statIndex == 'SD'):
        floatRaster = Float(outRasterExtByMask)
        outDivide = Divide(floatRaster, 100) # convert the integer to float
        arcpy.CopyRaster_management(outDivide, outRasterName, "DEFAULTS", "", "32767", "", "", "32_BIT_FLOAT")
    else:
        arcpy.CopyRaster_management(outRasterExtByMask, outRasterName, "DEFAULTS", "", "32767", "", "", "16_BIT_SIGNED")


###--------------------------------part 2------------------------------------###
### combining greenup band1 and band1 according values in the previous or current year
###--------------------------------------------------------------------------###

tileNames_Input = inWorkspace+"/TIFF_MLCD_V6_Data/"
tileNameFile = glob.glob(tileNames_Input + "/*.csv")

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

for everyline in open(tileNameFile[0]):
    fileName = everyline.split()[-1]
    newFileName = eval(''.join(fileName))
    print newFileName
    for eachB1Mean in B1_MeanGreenupList:
        if (newFileName == eachB1Mean.split('\\')[-1].split('Mean_GreenupB1.')[1]):
            B1MeanRaster = Raster(eachB1Mean)
            break
    for eachB2Mean in B2_MeanGreenupList:
        if (newFileName == eachB2Mean.split('\\')[-1].split('Mean_GreenupB2.')[1]):
            B2MeanRaster = Raster(eachB2Mean)
            break
    preMeanOutputName = combinedStatistics_Output + "PreYear_Mean_Greenup." + newFileName
    curMeanOutputName = combinedStatistics_Output + "CurYear_Mean_Greenup." + newFileName
    for eachB1Trend in B1_TrendGreenupList:
        if (newFileName == eachB1Trend.split('\\')[-1].split('Trend_GreenupB1.')[1]):
            B1TrendRaster = Raster(eachB1Trend)
            break
    for eachB2Trend in B2_TrendGreenupList:
        if (newFileName == eachB2Trend.split('\\')[-1].split('Trend_GreenupB2.')[1]):
            B2TrendRaster = Raster(eachB2Trend)
            break
    preTrendOutputName = combinedStatistics_Output + "PreYear_Trend_Greenup." + newFileName
    curTrendOutputName = combinedStatistics_Output + "CurYear_Trend_Greenup." + newFileName
    for eachB1pValue in B1_pValueGreenupList:
        if (newFileName == eachB1pValue.split('\\')[-1].split('P_ValueGreenupB1.')[1]):
            B1pValueRaster = Raster(eachB1pValue)
            break
    for eachB2pValue in B2_pValueGreenupList:
        if (newFileName == eachB2pValue.split('\\')[-1].split('P_ValueGreenupB2.')[1]):
            B2pValueRaster = Raster(eachB2pValue)
            break
    pre_pValueOutputName = combinedStatistics_Output + "PreYear_pValue_Greenup." + newFileName
    cur_pValueOutputName = combinedStatistics_Output + "CurYear_pValue_Greenup." + newFileName
    for eachB1_SD in B1_SD_GreenupList:
        if (newFileName == eachB1_SD.split('\\')[-1].split('SD_GreenupB1.')[1]):
            B1_SD_Raster = Raster(eachB1_SD)
            break
    for eachB2_SD in B2_SD_GreenupList:
        if (newFileName == eachB2_SD.split('\\')[-1].split('SD_GreenupB2.')[1]):
            B2_SD_Raster = Raster(eachB2_SD)
            break
    pre_SD_OutputName = combinedStatistics_Output + "PreYear_SD_Greenup." + newFileName
    cur_SD_OutputName = combinedStatistics_Output + "CurYear_SD_Greenup." + newFileName

    minB1 = B1MeanRaster.minimum
    minB2 = B2MeanRaster.minimum
    curYear = newFileName.split('.')[1][1:5]
    previousYear = int(curYear) - 1

    if (minB1 < 0 and minB2 > 0):
        tempB1_0 = Con(B1MeanRaster > 0, 1, 0)
        tempB1_1 = Con(IsNull(tempB1_0), 0, tempB1_0)  ##setting the nodata as 0
        #tempB1_1.save("tempB1_1.tif")
        tempB2_0 = Con(B2MeanRaster > 0, 1)  ##B2Raster has no negative pixel values
        tempB2_1 = Con(IsNull(tempB2_0), 0, tempB2_0)  ##setting the nodata as 0
        #tempB2_1.save("tempB2_1.tif")
        combined_B1B2 = tempB1_1 + tempB2_1  ##add tempB1_1 values (1) to tempB2_1 values (2)
        #extracting pixel values of 1 by setting the double calculated pixel as 0
        tempSingleCurPixel = Con(combined_B1B2 == 2, 0, combined_B1B2)
        singleCurPixel = SetNull(tempSingleCurPixel == 0, tempSingleCurPixel)
        #singleCurPixel.save("singleCurPixel.tif")
        #singleCurPixel is the template of current year (with pixel values of 1)
        tempCurYear_B1 = Con(singleCurPixel == 1, tempB1_1)
        #tempCurYear_B1.save("tempCurYear_B1.tif")
        tempCurYear_B2 = Con(singleCurPixel == 1, tempB2_1)
        #tempCurYear_B2.save("tempCurYear_B2.tif")

        curYear_Mean_Output = Con(tempCurYear_B1 == 1, B1MeanRaster, 0) + Con(tempCurYear_B2 == 1, B2MeanRaster, 0)
        #arcpy.CopyRaster_management(curYear_Mean_Output, curMeanOutputName, "DEFAULTS", "", "32767", "", "", "16_BIT_SIGNED")
        curYear_Trend_Output = Con(tempCurYear_B1 == 1, B1TrendRaster, 0) + Con(tempCurYear_B2 == 1, B2TrendRaster, 0)
        #arcpy.CopyRaster_management(curYear_Trend_Output, curTrendOutputName, "DEFAULTS", "", "32767", "", "", "32_BIT_FLOAT")
        curYear_pValue_Output = Con(tempCurYear_B1 == 1, B1pValueRaster, 0) + Con(tempCurYear_B2 == 1, B2pValueRaster, 0)
        #arcpy.CopyRaster_management(curYear_pValue_Output, cur_pValueOutputName, "DEFAULTS", "", "32767", "", "", "16_BIT_SIGNED")
        curYear_SD_Output = Con(tempCurYear_B1 == 1, B1_SD_Raster, 0) + Con(tempCurYear_B2 == 1, B2_SD_Raster, 0)
        #arcpy.CopyRaster_management(curYear_SD_Output, cur_SD_OutputName, "DEFAULTS", "", "32767", "", "", "32_BIT_FLOAT")
        funStat.export_combinedStat(curYear_Mean_Output,curMeanOutputName,curYear_Trend_Output,curTrendOutputName,
                                   curYear_pValue_Output, cur_pValueOutputName,curYear_SD_Output, cur_SD_OutputName)

        #the template of extracting pixel values in the previous year
        tempPreYear = SetNull(tempB1_0 > 0, tempB1_0)
        tempPreYear_Mean = Con(tempPreYear == 0, B1MeanRaster)
        if (previousYear % 4 == 0 and previousYear % 100 != 0) or (previousYear % 4 == 0 and previousYear % 400 == 0):
            preYear_Mean_Output = tempPreYear_Mean + 366
        else:
            preYear_Mean_Output = tempPreYear_Mean + 365
        preYear_Trend_Output = Con(tempPreYear == 0, B1TrendRaster)
        preYear_pValue_Output = Con(tempPreYear == 0, B1pValueRaster)
        preYear_SD_Output = Con(tempPreYear == 0, B1_SD_Raster)
        funStat.export_combinedStat(preYear_Mean_Output, preMeanOutputName,preYear_Trend_Output, preTrendOutputName,
                                   preYear_pValue_Output, pre_pValueOutputName,preYear_SD_Output, pre_SD_OutputName)

    elif (minB1 > 0 and minB2 < 0):
        tempB1_0 = Con(B1MeanRaster > 0, 1)
        tempB1_1 = Con(IsNull(tempB1_0), 0, tempB1_0)  ##setting the nodata as 0
        tempB2_0 = Con(B2MeanRaster > 0, 1,0)  ##B1Raster has no negative pixel values
        tempB2_1 = Con(IsNull(tempB2_0), 0, tempB2_0)  ##setting the nodata as 0
        combined_B1B2 = tempB1_1 + tempB2_1  ##add tempB1_1 values (1) to tempB2_1 values (2)
        #extracting pixel values of 1 by setting the double calculated pixel as 0
        tempSingleCurPixel = Con(combined_B1B2 == 2, 0, combined_B1B2)
        singleCurPixel = SetNull(tempSingleCurPixel == 0, tempSingleCurPixel)
        #singleCurPixel is the template of current year (with pixel values of 1)
        tempCurYear_B1 = Con(singleCurPixel == 1, tempB1_1)
        tempCurYear_B2 = Con(singleCurPixel == 1, tempB2_1)

        curYear_Mean_Output = Con(tempCurYear_B1 == 1, B1MeanRaster, 0) + Con(tempCurYear_B2 == 1, B2MeanRaster, 0)
        curYear_Trend_Output = Con(tempCurYear_B1 == 1, B1TrendRaster, 0) + Con(tempCurYear_B2 == 1, B2TrendRaster, 0)
        curYear_pValue_Output = Con(tempCurYear_B1 == 1, B1pValueRaster, 0) + Con(tempCurYear_B2 == 1, B2pValueRaster, 0)
        curYear_SD_Output = Con(tempCurYear_B1 == 1, B1_SD_Raster, 0) + Con(tempCurYear_B2 == 1, B2_SD_Raster, 0)
        funStat.export_combinedStat(curYear_Mean_Output, curMeanOutputName, curYear_Trend_Output, curTrendOutputName,
                                   curYear_pValue_Output, cur_pValueOutputName, curYear_SD_Output, cur_SD_OutputName)

        #template for extracting pixel values in the previous year
        tempPreYear = SetNull(tempB2_0 > 0, tempB2_0)
        tempPreYear_Mean = Con(tempPreYear == 0, B2MeanRaster)
        #tempPreYear_Mean.save ("temPreMean.tif")
        if (previousYear % 4 == 0 and previousYear % 100 != 0) or (previousYear % 4 == 0 and previousYear % 400 == 0):
            preYear_Mean_Output = tempPreYear_Mean + 366
        else:
            preYear_Mean_Output = tempPreYear_Mean + 365
        preYear_Trend_Output = Con(tempPreYear == 0, B2TrendRaster)
        preYear_pValue_Output = Con(tempPreYear == 0, B2pValueRaster)
        preYear_SD_Output = Con(tempPreYear == 0, B2_SD_Raster)
        funStat.export_combinedStat(preYear_Mean_Output, preMeanOutputName, preYear_Trend_Output, preTrendOutputName,
                                   preYear_pValue_Output, pre_pValueOutputName, preYear_SD_Output, pre_SD_OutputName)

    elif (minB1 < 0 and minB2 < 0): ## here hasn't been examined using data
        tempB1_0 = Con(B1MeanRaster > 0, 1, -1)
        tempB1_1 = Con(IsNull(tempB1_0), 0, tempB1_0)  ##setting the nodata as 0
        tempB2_0 = Con(B2MeanRaster > 0, 1,-1)  ##B2Raster has no negative pixel values
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
        curYear_pValue_Output = Con(tempCurYear_B1 == 1, B1pValueRaster, 0) + Con(tempCurYear_B2 == 1, B2pValueRaster,0)
        curYear_SD_Output = Con(tempCurYear_B1 == 1, B1_SD_Raster, 0) + Con(tempCurYear_B2 == 1, B2_SD_Raster, 0)
        funStat.export_combinedStat(curYear_Mean_Output, curMeanOutputName, curYear_Trend_Output, curTrendOutputName,
                                   curYear_pValue_Output, cur_pValueOutputName, curYear_SD_Output, cur_SD_OutputName)

        # template for extracting pixel values in the previous year
        tempSinglePrePixel = Con(combined_B1B2 == -2, 0, combined_B1B2)
        singlePrePixel = SetNull(tempSinglePrePixel == 0, tempSinglePrePixel)
        tempPreYear_B1 = Con(singlePrePixel == -1, tempB1_1)
        tempPreYear_B2 = Con(singlePrePixel == -1, tempB2_1)

        tempPreYear_Mean = Con(tempCurYear_B1 == -1, B1MeanRaster, 0) + Con(tempCurYear_B2 == -1, B2MeanRaster, 0)
        if (previousYear % 4 == 0 and previousYear % 100 != 0) or (previousYear % 4 == 0 and previousYear % 400 == 0):
            preYear_Mean_Output = tempPreYear_Mean + 366
        else:
            preYear_Mean_Output = tempPreYear_Mean + 365
        preYear_Trend_Output = Con(tempCurYear_B1 == -1, B1TrendRaster, 0) + Con(tempCurYear_B2 == -1, B2TrendRaster, 0)
        preYear_pValue_Output = Con(tempCurYear_B1 == -1, B1pValueRaster, 0) + Con(tempCurYear_B2 == -1, B2pValueRaster,0)
        preYear_SD_Output = Con(tempCurYear_B1 == -1, B1_SD_Raster, 0) + Con(tempCurYear_B2 == -1, B2_SD_Raster, 0)
        funStat.export_combinedStat(preYear_Mean_Output, preMeanOutputName, preYear_Trend_Output, preTrendOutputName,
                                   preYear_pValue_Output, pre_pValueOutputName, preYear_SD_Output, pre_SD_OutputName)
    else: ## here hasn't been examined using data
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
print str(time.ctime())+("ending the processing")
