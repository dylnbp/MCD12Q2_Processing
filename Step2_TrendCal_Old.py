import arcpy,os,glob
import time
import csv
import re ## for research
import decimal
import numpy as np
import functions_collection as funCol
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

greenUp_DOY_Input = inWorkspace+"/Tiff2DOY_Results/"
greenupStatistics_Output = inWorkspace+"/GreenupStatistics_Results/"

tileNames_Input = inWorkspace+"/TIFF_MLCD_V6_Data/"
tileNameFile = glob.glob(tileNames_Input + "/*.csv")
# define two bands of greenup
bandList = ['B1', 'B2']

for everyline in open(tileNameFile[0]):
    fileName = everyline.split()[-1].split('.') # for each tile in the name list .csv file
    for band in bandList:
        greenupOpenFiles = "*" + band + "." + eval(fileName[0] + ".*" + fileName[2] + "." + fileName[3])
        greenUp_DOY_List = glob.glob(greenUp_DOY_Input + greenupOpenFiles) # selecting 16-year greenup data for each tile
        comOutputName = band + "." + eval(fileName[0] + "." + fileName[1] + "." + fileName[2] + "." + fileName[3])
        pValueOutputName = greenupStatistics_Output + "P_ValueGreenup" + comOutputName
        trendOutputName = greenupStatistics_Output + "Trend_Greenup" + comOutputName
        meanOutputName = greenupStatistics_Output + "Mean_Greenup" + comOutputName
        medOutputName = greenupStatistics_Output + "MED_Greenup" + comOutputName
        sdOutputName = greenupStatistics_Output + "SD_Greenup" + comOutputName
        """
        QA_ALLOpenFiles = "QA_All" + band + "." + eval(fileName[0] + ".*" + fileName[2] + "." + fileName[3])
        QA_All_List = glob.glob(QA_All_Input + QA_ALLOpenFiles) ## selecting 16-year overall quality assurance data for each tile
        print QA_All_List
        """
        # checking the year in the order of 2001, 2002, ..., 2016
        if (greenUp_DOY_List[0].split("MCD12Q2.")[1][1:5]=='2001' and greenUp_DOY_List[1].split("MCD12Q2.")[1][1:5]=='2002' and
        greenUp_DOY_List[2].split("MCD12Q2.")[1][1:5]=='2003' and greenUp_DOY_List[3].split("MCD12Q2.")[1][1:5]=='2004' and
        greenUp_DOY_List[4].split("MCD12Q2.")[1][1:5]=='2005' and greenUp_DOY_List[5].split("MCD12Q2.")[1][1:5]=='2006' and
        greenUp_DOY_List[6].split("MCD12Q2.")[1][1:5]=='2007' and greenUp_DOY_List[7].split("MCD12Q2.")[1][1:5]=='2008' and
        greenUp_DOY_List[8].split("MCD12Q2.")[1][1:5]=='2009' and greenUp_DOY_List[9].split("MCD12Q2.")[1][1:5]=='2010' and
        greenUp_DOY_List[10].split("MCD12Q2.")[1][1:5]=='2011' and greenUp_DOY_List[11].split("MCD12Q2.")[1][1:5]=='2012' and
        greenUp_DOY_List[12].split("MCD12Q2.")[1][1:5]=='2013' and greenUp_DOY_List[13].split("MCD12Q2.")[1][1:5]=='2014' and
        greenUp_DOY_List[14].split("MCD12Q2.")[1][1:5]=='2015' and greenUp_DOY_List[15].split("MCD12Q2.")[1][1:5]=='2016'):
            # getting values from 16 MLCD12Q2 files of one tile from 2001 to 2016
            band0, geoTransform0, proj0, cols0, rows0 = funCol.return_band(greenUp_DOY_List[0], 1)
            band1, geoTransform1, proj1, cols1, rows1 = funCol.return_band(greenUp_DOY_List[1], 1)
            band2, geoTransform2, proj2, cols2, rows2 = funCol.return_band(greenUp_DOY_List[2], 1)
            band3, geoTransform3, proj3, cols3, rows3 = funCol.return_band(greenUp_DOY_List[3], 1)
            band4, geoTransform4, proj4, cols4, rows4 = funCol.return_band(greenUp_DOY_List[4], 1)
            band5, geoTransform5, proj5, cols5, rows5 = funCol.return_band(greenUp_DOY_List[5], 1)
            band6, geoTransform6, proj6, cols6, rows6 = funCol.return_band(greenUp_DOY_List[6], 1)
            band7, geoTransform7, proj7, cols7, rows7 = funCol.return_band(greenUp_DOY_List[7], 1)
            band8, geoTransform8, proj8, cols8, rows8 = funCol.return_band(greenUp_DOY_List[8], 1)
            band9, geoTransform9, proj9, cols9, rows9 = funCol.return_band(greenUp_DOY_List[9], 1)
            band10, geoTransform10, proj10, cols10, rows10 = funCol.return_band(greenUp_DOY_List[10], 1)
            band11, geoTransform11, proj11, cols11, rows11 = funCol.return_band(greenUp_DOY_List[11], 1)
            band12, geoTransform12, proj12, cols12, rows12 = funCol.return_band(greenUp_DOY_List[12], 1)
            band13, geoTransform13, proj13, cols13, rows13 = funCol.return_band(greenUp_DOY_List[13], 1)
            band14, geoTransform14, proj14, cols14, rows14 = funCol.return_band(greenUp_DOY_List[14], 1)
            band15, geoTransform15, proj15, cols15, rows15 = funCol.return_band(greenUp_DOY_List[15], 1)

            if((cols0==cols1==cols2==cols3==cols4==cols5==cols6==cols7==cols8==cols9==cols10==cols11==cols12==cols13==cols14==cols15)
            and(rows0==rows1==rows2==rows3==rows4==rows5==rows6==rows7==rows8==rows9==rows10==rows11==rows12==rows13==rows14==rows15)):
                for i in range(0,rows0):
                    print i
                    for j in range(0,cols0):

                        pixelValues = [band0[i,j], band1[i,j], band2[i,j], band3[i,j],
                                       band4[i,j], band5[i,j], band6[i,j], band7[i,j],
                                       band8[i,j], band9[i,j], band10[i,j], band11[i,j],
                                       band12[i,j], band13[i,j], band14[i,j], band15[i,j]]

                        if (any(element == 32767 for element in pixelValues)):
                            while 32767 in pixelValues: pixelValues.remove(32767) # removing nodata 32767 in pixelValues list
                        validValues = funCol.remove_outlier(pixelValues) # removing outliers in pixevalue list
                        validValues = np.asarray(validValues) # convert an array_like list to an array
                        yearCount = validValues.size
                        if (yearCount > 12):
                            xValues = np.asarray(range(1, yearCount + 1, 1)) # generating x variable (1,2...)
                            slope, intercept, r_value, p_value, std_err = stats.linregress(xValues, validValues)
                            if (p_value < 0.001):
                                reP_value = 1
                            elif (p_value < 0.005 and p_value >= 0.001):
                                reP_value = 5
                            elif ((p_value < 0.05 and p_value >= 0.005)):
                                reP_value = 50
                            else:
                                reP_value = 0
                            reSlope = round(slope, 2)*100
                            meanValue = round(np.mean(validValues), 0)
                            medianValue = round(np.median(validValues), 0)
                            if(np.std(validValues) < 327.67):
                                sdValue = round(np.std(validValues), 2) * 100
                            else:
                                sdValue = -32768
                                print "unvalid standard deviation!!!"
                            # print reSlope, reP_value, meanValue, medianValue, sdValue
                        else:
                            reP_value = 32767
                            reSlope = 32767
                            meanValue = 32767
                            medianValue = 32767
                            sdValue = 32767

                        band0[i,j] = reP_value
                        band1[i,j] = reSlope
                        band2[i, j] = meanValue
                        band3[i, j] = medianValue
                        band4[i, j] = sdValue

                funCol.output_file(pValueOutputName, band0, geoTransform0, proj0, cols0, rows0)
                funCol.output_file(trendOutputName, band1, geoTransform1, proj1, cols1, rows1)
                funCol.output_file(meanOutputName, band2, geoTransform2, proj2, cols2, rows2)
                funCol.output_file(medOutputName, band3, geoTransform3, proj3, cols3, rows3)
                funCol.output_file(sdOutputName, band4, geoTransform4, proj4, cols4, rows4)

            else:
                print ("Rows/columns are not equal")

        else:
            print ("Tile files do not cover the 16 years")


















"""
greenUp_DOY_InputList = glob.glob(greenUp_DOY_Input+"/*.tif")
QA_All_InputList = glob.glob(QA_All_Input+"*QA_AllB*.tif")

#print greenUp_DOY_InputList
#print QA_All_InputList


print greenUp_DOY_InputList[0]

for line in open(tileNameFile[0]):
    fileName = line.split()
    newFileName = ''.join(fileName)
    print newFileName
    new_list = [x for x in greenUp_DOY_InputList if re.search(newFileName, x)]
    for item in new_list:
        print item
"""











