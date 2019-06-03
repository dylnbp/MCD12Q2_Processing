# -*- coding: cp936 -*-
import arcpy,os,glob
import time
from osgeo import gdal, osr
from arcpy import env
from arcpy.sa import *

print("________________________________________________________")
print str(time.ctime())+("starting the processing")

workingDir = os.getcwd()
print workingDir

inWorkspace = workingDir  # set the workspace based on the location of images
env.workspace = inWorkspace
env.overwriteOutput = True
## env.nodata = "NONE" ## this doesn't work
arcpy.CheckOutExtension("spatial")

Tiff2DOY_Input = inWorkspace+"/Test_TIFF_MLCD_V6_Data/"
Tiff2DOY_Output = inWorkspace+"/Test_Step1_CalculationDOY_Results/"

greeup_InputList = glob.glob(Tiff2DOY_Input+"*GreenupB*.tif")
QA_All_InputList = glob.glob(Tiff2DOY_Input+"*QA_ALLB*.tif")
# print greeup_InputList
# print QA_All_InputList

for origRaster in greeup_InputList:
    print(origRaster)
    inRaster = Raster(origRaster)
    origRasterNameList = inRaster.name.split('\\')[0]
    yearValue = origRasterNameList.split('.')[2][1:5]
    greenupPart0 = origRasterNameList.split('.')[0][-2:]
    greenupPart1 = origRasterNameList.split('.')[1]
    greenupPart2 = origRasterNameList.split('.')[2]
    greenupPart3 = origRasterNameList.split('.')[3]

    # setting 32767 as null(nodata)
    #outRasterSetNull = SetNull(inRaster == 32767, inRaster)
    #print(outRasterSetNull)

    #calculating the day of year of MLCD phenology product (start from 1-1-1970)
    if yearValue == "2001":
        doyRaster = inRaster - 11323
    elif yearValue == "2002":
        doyRaster = inRaster - 11688
    elif yearValue == "2003":
        doyRaster = inRaster - 12053
    elif yearValue == "2004":
        doyRaster = inRaster - 12418
    elif yearValue == "2005":
        doyRaster = inRaster - 12784
    elif yearValue == "2006":
        doyRaster = inRaster - 13149
    elif yearValue == "2007":
        doyRaster = inRaster - 13514
    elif yearValue == "2008":
        doyRaster = inRaster - 13879
    elif yearValue == "2009":
        doyRaster = inRaster - 14245
    elif yearValue == "2010":
        doyRaster = inRaster - 14610
    elif yearValue == "2011":
        doyRaster = inRaster - 14975
    elif yearValue == "2012":
        doyRaster = inRaster - 15340
    elif yearValue == "2013":
        doyRaster = inRaster - 15706
    elif yearValue == "2014":
        doyRaster = inRaster - 16071
    elif yearValue == "2015":
        doyRaster = inRaster - 16436
    elif yearValue == "2016":
        doyRaster = inRaster - 16801

    ## filter greenup values based the overall QA files (best:0 and good:1)
    for QA in QA_All_InputList:
        QA_Raster = Raster(QA)
        QA_RasterNameList = QA_Raster.name.split('\\')[0]
        QA_Part0 = QA_RasterNameList.split('.')[0][-2:]
        QA_Part1 = QA_RasterNameList.split('.')[1]
        QA_Part2 = QA_RasterNameList.split('.')[2]
        QA_Part3 = QA_RasterNameList.split('.')[3]
        if(QA_Part0 == greenupPart0 and QA_Part1 == greenupPart1 and QA_Part2 == greenupPart2 and QA_Part3 == greenupPart3):
            print QA_RasterNameList
            conDoyRaster = Con((QA_Raster == 0)|(QA_Raster == 1), doyRaster) ## value = 0 (best) or 1 (good)
            # print conDoyRaster.pixelType

    # defining the outfile name
    outputName = "DOY_"+ origRasterNameList
    outputRaster = Tiff2DOY_Output + outputName
    print(outputRaster)
    #conDoyRaster.save(outputRaster)
    #try:
    arcpy.CopyRaster_management(conDoyRaster,outputRaster,"DEFAULTS","","32767","","","16_BIT_SIGNED")
    #except:
        #print "Copy Raster example failed."
        #print arcpy.GetMessages()

print("________________________________________________________")
print str(time.ctime())+("ending the processing")