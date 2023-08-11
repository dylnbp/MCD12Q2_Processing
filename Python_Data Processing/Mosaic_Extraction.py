# -*- coding: cp936 -*-
import arcpy, os, glob
import time
from arcpy import env
from arcpy.sa import *
import keyword
import re

print("________________________________________________________")
print ("Starting!") + str(time.ctime())

workingDir = os.getcwd()  ## getting working directory
print workingDir
inWorkspace = workingDir  ##set the workspace based on the location of images
env.workspace = inWorkspace
env.overwriteOutput = True
arcpy.CheckOutExtension("spatial")

greenupDOY_Input = inWorkspace + "/Step1_CalculationDOY/"
mosaicResultFolder = "MosaicResults"

###------------------------------ part 1 -----------------------------###
### Mosaic tiles
###------------------------------------------------------------------###
os.chdir(greenupDOY_Input)  ##set working directory

greeupDOY_InputList = glob.glob(greenupDOY_Input + "*.tif")
print greeupDOY_InputList

mosaicIndex = [] ## using to store the common part of file names in each year
greenupNameList = []  ## using to store greenup file names after removing the directory path
for eachGreenup in greeupDOY_InputList:
    inRaster = Raster(eachGreenup)
    eachGreenupName = inRaster.name.split('\\')[0]
    greenupNameList.append(eachGreenupName)
    mosaicName = eachGreenupName.split('.')
    mosaicIndex.append(mosaicName[0] + "." + mosaicName[1] + "." + mosaicName[2])

mosaicIndex = list(dict.fromkeys(mosaicIndex)) ##removing duplicated values
print(len(mosaicIndex))

for i in range(0, len(mosaicIndex)):
    mosaic_list = [x for x in greenupNameList if re.search(mosaicIndex[i], x)]
    # print mosaic_list
    inputGreenupStr = "\"" + ';'.join(mosaic_list) + "\"" ## connecting every elements in the list
    mosaicOutputName = mosaicIndex[i] + ".tif"
    print mosaicOutputName
    arcpy.MosaicToNewRaster_management(inputGreenupStr, mosaicResultFolder, mosaicOutputName, "",
                                       "16_BIT_SIGNED", "", "1", "LAST", "FIRST")


###----------------------------- part 2 -----------------------------###
### Extracting greenup of study area from the mosaicing outcome
###------------------------------------------------------------------###

# redirecting the working space
os.chdir(workingDir)

mosaicInput = greenupDOY_Input + mosaicResultFolder + "/"
mosaicInputList = glob.glob(mosaicInput + "*.tif")

studyAreaFolder = "Pakistan"
studyAreaShp = glob.glob(inWorkspace + "/" + studyAreaFolder + "/*.shp")
print studyAreaShp[0]

studyAreaGreeupDOY_Output = inWorkspace + "/StudyArea_GreenupDOY/"

for eachRaster in mosaicInputList:
    inRaster = Raster(eachRaster)
    inputNameList = inRaster.name.split('\\')
    suffixOutput = "_" + studyAreaFolder + ".tif"
    outRasterName = studyAreaGreeupDOY_Output + inputNameList[0].replace(".tif",suffixOutput)
    print outRasterName
    outRasterExtByMask = ExtractByMask(inRaster, studyAreaShp[0])
    arcpy.CopyRaster_management(outRasterExtByMask, outRasterName, "DEFAULTS", "", "32767", "", "", "16_BIT_SIGNED")

## the following is used to delete all mosaic files for saving storage space
delAllInputList = glob.glob(mosaicInput + "*")
for each in delAllInputList:
    os.remove(each)

print("________________________________________________________")
print ("Ending!") + str(time.ctime())

