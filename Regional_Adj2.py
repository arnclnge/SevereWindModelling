"""
Adjusting TCRM output using observed data 

execfile(r'D:/RAPID files/sample python codes/Regional_Adj.py')

"""

import sys
import arcpy
import os
from datetime import datetime
import time
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")

#------------------------------SET INPUTS------------------------------------------#
arcpy.env.workspace = "D:\\workspace_SW_Cebu\\ADJUSTMENTS\\LuzonFreq15Dom2\\adj.gdb\\"
arcpy.env.scratchWorkspace = "D:\\workspace_SW_Cebu\\ADJUSTMENTS\\LuzonFreq15Dom2\\scratch.gdb"

arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 51N")
out_coords = arcpy.SpatialReference("WGS 1984 UTM Zone 51N")

main_dir = "D:\\workspace_SW_Cebu\\ADJUSTMENTS\\LuzonFreq15Dom2\\"
TCRM_dir = "D:\\workspace_SW_Cebu\\TCRM_LUZON\\Luzon_Freq15Dom2\\luzon_freq15dom2.gdb"
v4_dir = "D:\\workspace_SW_Cebu\\ADJUSTMENTS\\LuzonFreq15Dom2\\adj.gdb\\"
v4_dir_ = "D:\\workspace_SW_Cebu\\ADJUSTMENTS\\LuzonFreq15Dom2\\adj.gdb"
error_csv = main_dir+"RP_error.csv"

rp_list = [2,5,10,20,50,100,200,500,1000]
err_rpList = ['ERR_2','ERR_5','ERR_10','ERR_20','ERR_50','ERR_100','ERR_200','ERR_500','ERR_1000']

prj = "D:/Data/WGS 1984.prj"
prj2 = "D:/Data/WGS 1984 UTM Zone 51N.prj"

'''
#----------------------------------------------------------------------------------#

#Initialize
arcpy.env.overwriteOutput = True
print(time.strftime('%H:%M:%S')+" Initialize...")

#Create shpfile from dbf

# Local variables:
error_dbf = "R_obs_2018_v2.dbf"
# Process: Table to Table
arcpy.TableToTable_conversion(error_csv, main_dir, error_dbf, "", 
							"STATION \"STATION\" true true false 255 Text 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,STATION,-1,-1; \
							STNUM \"STNUM\" true true false 4 Long 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,STNUM,-1,-1; \
							LAT \"LAT\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,LAT,-1,-1; \
							LON \"LON\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,LON,-1,-1; \
							RP_2 \"RP_2\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,RP_2,-1,-1; \
							RP_10 \"RP_10\" true true false 4 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,RP_10,-1,-1; \
							RP_20 \"RP_20\" true true false 4 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,RP_20,-1,-1; \
							RP_50 \"RP_50\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,RP_50,-1,-1; \
							RP_100 \"RP_100\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,RP_100,-1,-1; \
							RP_200 \"RP_200\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,RP_200,-1,-1; \
							RP_500 \"RP_500\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,RP_500,-1,-1; \
							RP_700 \"RP_700\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,RP_700,-1,-1; \
							RP_1000 \"RP_1000\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,RP_1000,-1,-1; \
							TCRM_2 \"TCRM_2\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,TCRM_2,-1,-1; \
							TCRM_10 \"TCRM_10\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,TCRM_10,-1,-1; \
							TCRM_20 \"TCRM_20\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,TCRM_20,-1,-1; \
							TCRM_50 \"TCRM_50\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,TCRM_50,-1,-1; \
							TCRM_100 \"TCRM_100\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,TCRM_100,-1,-1; \
							TCRM_200 \"TCRM_200\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,TCRM_200,-1,-1; \
							TCRM_500 \"TCRM_500\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,TCRM_500,-1,-1; \
							TCRM_700 \"TCRM_700\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,TCRM_700,-1,-1; \
							TCRM_1000 \"TCRM_1000\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,TCRM_1000,-1,-1; \
							Err_2 \"Err_2\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Err_2,-1,-1; \
							Err_10 \"Err_10\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Err_10,-1,-1; \
							Err_20 \"Err_20\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Err_20,-1,-1; \
							Err_50 \"Err_50\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Err_50,-1,-1; \
							Err_100 \"Err_100\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Err_100,-1,-1; \
							Err_200 \"Err_200\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Err_200,-1,-1; \
							Err_500 \"Err_500\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Err_500,-1,-1; \
							Err_700 \"Err_700\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Err_700,-1,-1; \
							Err_1000 \"Err_1000\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Err_1000,-1,-1; \
							Diff_2 \"Diff_2\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Diff_2,-1,-1; \
							Diff_10 \"Diff_10\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Diff_10,-1,-1; \
							Diff_20 \"Diff_20\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Diff_20,-1,-1; \
							Diff_50 \"Diff_50\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Diff_50,-1,-1; \
							Diff_100 \"Diff_100\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Diff_100,-1,-1; \
							Diff_200 \"Diff_200\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Diff_200,-1,-1; \
							Diff_500 \"Diff_500\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Diff_500,-1,-1; \
							Diff_700 \"Diff_700\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Diff_700,-1,-1; \
							Diff_1000 \"Diff_1000\" true true false 8 Double 0 0 ,First,#,D:\\workspace_SW_Cebu\\ADJUSTMENTS\\v4\\RP_diff_err.csv,Diff_1000,-1,-1", "")
								
arcpy.MakeXYEventLayer_management(main_dir+error_dbf, "LON", "LAT", "error_lyr", prj)
arcpy.SaveToLayerFile_management("error_lyr", main_dir+"error.lyr")
#arcpy.FeatureClassToShapefile_conversion("error_lyr", main_dir)
#error_shp = main_dir+"error_lyr.shp"
#print("Successfully created error shpfile")


#Project lyr
arcpy.Project_management(main_dir+"error.lyr", main_dir+"error_prj", prj2)

print("Projection successful...")
'''
#------------------------------------------------Krig Error-----------------------------------------#
error_prj = main_dir+"RP_errprj.shp"

# Process: Kriging
#extent "xmin, ymin, xmax, ymax"  or "left, bottom, right, top"
arcpy.env.extent = "-174730.791357 1213922.296 903312.639700 2341973.073946"    #LUZON extent 
for rp in err_rpList:
	arcpy.gp.Kriging_sa(error_prj, rp, v4_dir+rp, "Spherical", "5000", "VARIABLE 12", "")
	print("Kriging error for rp "+rp)

#---------------------------------------Adjust using Raster Calculator------------------------------------------#
for dirpath, dirnames, filenames in arcpy.da.Walk(TCRM_dir, datatype='RasterDataset'):
	for tcrm_rp in [f for f in filenames if f.endswith("_clp")]:
		print(tcrm_rp)
		rp = tcrm_rp.replace("wspd_","").replace("_clp","")
		if int(rp) in rp_list:
			print(rp)
			arcpy.env.workspace = TCRM_dir
			arcpy.CopyRaster_management(tcrm_rp,v4_dir+tcrm_rp)
			for dirpath2,dirnames2,filenames2 in arcpy.da.Walk(v4_dir_, datatype='RasterDataset'):
				for err_rp in [f for f in filenames2 if f.startswith("ERR") and f.endswith(rp)]:
					arcpy.env.workspace = v4_dir
					print(err_rp)
					err_ras = Raster(err_rp)
					tcrm_ras = Raster (tcrm_rp)
					
					adj = (tcrm_ras + ((tcrm_ras / (1-err_ras))*err_ras))*3.6
					adj.save("adj_"+rp)
					print("Adjusted for rp"+rp)





