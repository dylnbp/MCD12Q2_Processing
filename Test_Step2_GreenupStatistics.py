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

workingDir = os.getcwd()
print workingDir

inWorkspace = workingDir  # set the workspace based on the location of images
env.workspace = inWorkspace
env.overwriteOutput = True
arcpy.CheckOutExtension("spatial")

greenUp_DOY_Input = inWorkspace + "/Test_Step1_CalculationDOY_Results/"
#greenUp_DOY_Input = inWorkspace+"/Tiff2DOY_Results/"
greenupStatistics_Output = inWorkspace + "/Test_Step2_GreenupStatistics/"

tileNames_Input = inWorkspace + "/Test_TIFF_MLCD_V6_Data/"
tileNameFile = glob.glob(tileNames_Input + "/*.csv")
# define two bands of greenup
# bandList = ['B1', 'B2']

if __name__ == "__main__":
    for everyline in open(tileNameFile[0]):
        fileName = everyline.split()[-1].split('.')  # for each tile in the name list .csv file
        print fileName

        greenupOpenFiles_B1 = "*B1." + eval(fileName[0] + ".*" + fileName[2] + "." + fileName[3])
        greenUp_DOY_List_B1 = glob.glob(greenUp_DOY_Input + greenupOpenFiles_B1)  # selecting 16-year greenup data for each tile
        #print greenUp_DOY_List_B1
        comOutputName_B1 = "B1." + eval(fileName[0] + "." + fileName[1] + "." + fileName[2] + "." + fileName[3])
        trendOutputName_B1 = greenupStatistics_Output + "Trend_Greenup" + comOutputName_B1
        pValueOutputName_B1 = greenupStatistics_Output + "P_ValueGreenup" + comOutputName_B1
        meanOutputName_B1 = greenupStatistics_Output + "Mean_Greenup" + comOutputName_B1
        medOutputName_B1 = greenupStatistics_Output + "MED_Greenup" + comOutputName_B1
        sdOutputName_B1 = greenupStatistics_Output + "SD_Greenup" + comOutputName_B1

        greenupOpenFiles_B2 = "*B2." + eval(fileName[0] + ".*" + fileName[2] + "." + fileName[3])
        greenUp_DOY_List_B2 = glob.glob(greenUp_DOY_Input + greenupOpenFiles_B2)  # selecting 16-year greenup data for each tile
        #print greenUp_DOY_List_B2
        comOutputName_B2 = "B2." + eval(fileName[0] + "." + fileName[1] + "." + fileName[2] + "." + fileName[3])
        trendOutputName_B2 = greenupStatistics_Output + "Trend_Greenup" + comOutputName_B2
        pValueOutputName_B2 = greenupStatistics_Output + "P_ValueGreenup" + comOutputName_B2
        meanOutputName_B2 = greenupStatistics_Output + "Mean_Greenup" + comOutputName_B2
        medOutputName_B2 = greenupStatistics_Output + "MED_Greenup" + comOutputName_B2
        sdOutputName_B2 = greenupStatistics_Output + "SD_Greenup" + comOutputName_B2

        if ((funStat.check_yearOrder(greenUp_DOY_List_B1) == 1) and (funStat.check_yearOrder(greenUp_DOY_List_B2) == 1)):
            print str(time.ctime()) + ("starting")
            yearLimit = 12
            p1 = multiprocessing.Process(target=funStat.CalB1_GreenupStat, args=(
            greenUp_DOY_List_B1, yearLimit, trendOutputName_B1, pValueOutputName_B1, meanOutputName_B1, medOutputName_B1,
            sdOutputName_B1))
            p2 = multiprocessing.Process(target=funStat.CalB2_GreenupStat, args=(
            greenUp_DOY_List_B2, yearLimit, trendOutputName_B2, pValueOutputName_B2, meanOutputName_B2, medOutputName_B2,
            sdOutputName_B2))
            # funCol.CalB1_GreenupStat(greenUp_DOY_List_B1, 12, trendOutputName_B1, pValueOutputName_B1, meanOutputName_B1,
            # medOutputName_B1, sdOutputName_B1)
            p1.start()
            p2.start()

            p1.join()
            p2.join()
            print str(time.ctime()) + ("ending")
        else:
            print ("Tile files do not cover the 16 years")
