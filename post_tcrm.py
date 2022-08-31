"""

TITLE: PROCESSING HAZARD OUTPUT FROM TCRM 

This script processes hazard.nc file from TCRM, extracts according to the country boundary, and converts values from mps to kph.

Data needed:
	1. hazard nc file


Open the python application from C:/Python27/ArcGIS10.2/python.exe

Type:
>>>execfile(r'D:/RAPID files/python codes/post_tcrm.py')

Arienne D. Calonge
arnclnge821@gmail.com


"""

# -*- coding: utf-8 -*-

import sys
import arcpy
from arcpy.sa import *
import os
from datetime import datetime
import time
import re
import shutil

arcpy.CheckOutExtension("Spatial")

#----------SET INPUTS
arcpy.env.workspace = "D:/workspace_SW_Cebu/TCRM_3/TCMerge_2018/TCMerge_2018.gdb/"
arcpy.env.scratchWorkspace = "D:/workspace_SW_Cebu/TCRM_MINDANAO/LATITUDINAL/scratch.gdb/"

out = "D:/workspace_SW_Cebu/TCRM_3/TCMerge_2018/TCMerge_2018.gdb/"
ph_boundary = "D:/Data/Philbasemaps2010_NSO_OCHA/PH_boundary.shp"	
#ph_boundary = "D:/Data/Philbasemaps2010_NSO_OCHA/mindanao_prov.shp"											#BOUNDARY SHP
netcdf = "D:/workspace_SW_Cebu/TCRM_3/TCMerge_2018/hazard.nc"
pt_extract = "D:/workspace_SW_Cebu/TCRM_MINDANAO/LATITUDINAL/stns_gust.shp"


#Initialize
raster_dir = "D:/workspace_SW_Cebu/TCRM_MINDANAO/LATITUDINAL/raster_rp5km"
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 51N")
print(time.strftime('%H:%M:%S')+" Initialize...")
# arcpy.Compress_management(out)      

#make netcdf layer
yr_list = [2,3,4,5,10,15,20,30,40,50,75,100,200,500,700,1000]
#yr_list = [2,3,4,5,10,15,20,25,30,35,40,45,50,75,100,150,200,250,300,350,400,450,500,700,1000,1700,2000,2500,5000,10000]

for y in yr_list:
	y = str(y)
	arcpy.MakeNetCDFRasterLayer_md(netcdf,'wspd','lon','lat','wspd_'+y,'#',"years "+y,"BY_VALUE")
	arcpy.SaveToLayerFile_management('wspd_'+y,'wspd_'+y+'.lyr')
	print('wspd_'+y+' raster layer created...')
	

for rp in [f for f in os.listdir(out) if f.endswith('.lyr')]:
	flname = rp.replace('.lyr', '')
	print(flname)
	
	#copy layer files to raster_dir
	shutil.copyfile(out+rp,raster_dir+rp)
	print("Layer file copied to raster folder...")
            	
	#Clip Raster
	arcpy.Clip_management(raster_dir+rp,'-174730.791357 507005.531721 900170.986393 2341973.073946',flname+"_clp",'#','#','#','MAINTAIN_EXTENT')
	print(flname+" clipped...")
	
	#project raster
	outCS = arcpy.SpatialReference('WGS 1984 UTM Zone 51N')
	
	arcpy.ProjectRaster_management(flname+"_clp",flname+'_prj',outCS,'BILINEAR','5000')
	print(flname+" projected...")
	
	yr = re.search('wspd_(.+?).lyr',rp)
	if yr:
		yr_rp = yr.group(1)
		print(yr_rp)
	
	#extract by mask
	#arcpy.env.cellSize = 20♣
	rp_extract = ExtractByMask(flname+'_prj', ph_boundary)
	rp_extract.save("wspd_"+yr_rp+"ph")
	print("wspd_"+yr_rp+"ph"+" extracted...")

	#convert mps to kph
	rp_mps = Raster("wspd_"+yr_rp+"ph")*3.6
	rp_mps.save("wspd_"+yr_rp+"kph")
	print("wspd_"+yr_rp+"kph"+" saved to gdb...")
	
#extract multi values to points
ExtractMultiValuesToPoints(pt_extract, [["wspd_2_clp","TCRM_2"],["wspd_3_clp","TCRM_3"],["wspd_4_clp","TCRM_4"],["wspd_5_clp","TCRM_5"],["wspd_10_clp","TCRM_10"],["wspd_15_clp","TCRM_15"],["wspd_20_clp","TCRM_20"],["wspd_30_clp","TCRM_30"],["wspd_40_clp","TCRM_40"],["wspd_50_clp","TCRM_50"],["wspd_75_clp","TCRM_75"],["wspd_100_clp","TCRM_100"],["wspd_200_clp","TCRM_200"],["wspd_500_clp","TCRM_500"],["wspd_700_clp","TCRM_700"],["wspd_1000_clp","TCRM_1000"]],"NONE")
#ExtractMultiValuesToPoints(pt_extract, [["wspd_2_clp","TCRM_2"],["wspd_3_clp","TCRM_3"],["wspd_4_clp","TCRM_4"],["wspd_5_clp","TCRM_5"],["wspd_10_clp","TCRM_10"],["wspd_15_clp","TCRM_15"],["wspd_20_clp","TCRM_20"],["wspd_25_clp","TCRM_25"],["wspd_30_clp","TCRM_30"],["wspd_35_clp","TCRM_35"],["wspd_40_clp","TCRM_40"],["wspd_45_clp","TCRM_45"],["wspd_50_clp","TCRM_50"],["wspd_75_clp","TCRM_75"],["wspd_100_clp","TCRM_100"],["wspd_150_clp","TCRM_150"],["wspd_200_clp","TCRM_200"],["wspd_250_clp","TCRM_250"],["wspd_300_clp","TCRM_300"],["wspd_350_clp","TCRM_350"],["wspd_400_clp","TCRM_400"],["wspd_450_clp","TCRM_450"],["wspd_500_clp","TCRM_500"],["wspd_700_clp","TCRM_700"],["wspd_1000_clp","TCRM_1000"],["wspd_1700_clp","TCRM_1700"],["wspd_2000_clp","TCRM_2000"],["wspd_2500_clp","TCRM_2500"],["wspd_5000_clp","TCRM_5000"],["wspd_10000_clp","TCRM_10000"]],"NONE")
print("TCRM raster values in mps extracted to PAGASA station points...")
	


print(time.strftime('%H:%M:%S')+" All tiff files processed. Next step: adjust rasters using observed data")