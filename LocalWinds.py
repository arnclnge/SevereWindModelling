"""

TITLE: Extracting regional and producing local winds per province
	
workspace: D:\LOCALWIND\
		
Data needed:
	1. regional winds for ph (copy to Extract.gdb)
	2. provincial boundary (copy to DATA/running_boundaries & DATA/PSA2016_province)
	3. combined multiplier (copy to Extract.gdb)
	
Main Outputs: 
	1. prov_reg (in the geodatabase)
	2. prov_loc (in the geodatabase)
	3. prov_muni (in prov_muni_output)
	4. mean wdspd per barangay dbf files (tables_dir)
	
Open the python application from C:/Python27/ArcGIS10.2/python.exe

Type:
>>>execfile(r'D:/RAPID files/sample python codes/LocalWinds.py')

Arienne D. Calonge
arnclnge821@gmail.com


"""

import os
import sys
import arcpy
from arcpy.sa import *
from datetime import datetime
import time

arcpy.CheckOutExtension("Spatial")

####--------------------------------------------------SET INPUTS---------------------------------------------------####
out_dir = "D:/LOCALWIND/Feb2020.gdb/"
out_dir_ = "D:/LOCALWIND/Feb2020.gdb"	
adj_dir = "D:/workspace_SW_Cebu/ADJUSTMENTS/v4/v4.gdb"						#CHANGE!
provboundary_dir = "D:/LOCALWIND/DATA/running_boundaries/"	
mult_dir = "D:/LOCALWIND/DATA/MULTIPLIERS/"		
tables_dir = "D:/LOCALWIND/DATA/TABLES/"									#CHANGE!
muni_dir = "D:/LOCALWIND/DATA/PSA2016_brgy_py/"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 51N")																			#change
arcpy.env.overwriteOutput = True
arcpy.env.cellSize = 20
print(time.strftime('%H:%M:%S')+" Initialize...")

rp_list = [2,10,20,50,100,200,500,700,1000]

#######################################################################################################################

#COPY ADJUSTED RASTER
#for dirpath, dirnames, filenames in arcpy.da.Walk(adj_dir, datatype='RasterDataset'):
#	for adj in [f for f in filenames if f.startswith("adj_")]:
#		rp = adj.replace("adj_","")
#		if int(rp) in rp_list:
#			print(rp)
#			arcpy.env.workspace = adj_dir
#			arcpy.CopyRaster_management(adj, out_dir+adj)

#copy multipliers
for shp in [f for f in os.listdir(provboundary_dir) if f.endswith('.shp')]:	#location of shpfiles
	prov = shp.replace('_psaprov.shp','')			
	for dirpath, dirnames, filenames in arcpy.da.Walk(mult_dir+prov, datatype='RasterDataset'):
		for combmult in filenames:
			arcpy.env.workspace = mult_dir+prov
			arcpy.CopyRaster_management(combmult, out_dir+prov+'_'+combmult)

arcpy.env.workspace = out_dir_
arcpy.env.cellSize = 20
for shp in [f for f in os.listdir(provboundary_dir) if f.endswith('.shp')]:	#location of shpfiles
	prov = shp.replace('_psaprov.shp','')
	print('Extracting for '+prov)
	for dirpath, dirnames, filenames in arcpy.da.Walk(out_dir_, datatype='RasterDataset'):
		for adj in [f for f in filenames if f.startswith("adj_")]:
			rp = adj.replace("adj_","")
			arcpy.env.cellSize = 20
			#EXTRACT
			arcpy.gp.ExtractByMask_sa(adj,provboundary_dir+shp, prov+'_adj{}'.format(rp))
			print("adj_{} extracted for ".format(rp)+prov)
			
			#calculate local wind
			Loc_raster = Raster(prov+'_adj{}'.format(rp))*Raster(prov+"_"+combmult)
			Loc_raster.save(prov+"_loc{}".format(rp))
			print("Loc_{} calculated for ".format(rp)+prov)
		
			#ZONAL STATISTICS PER BARANGAY
			muni_shp = muni_dir+prov+'_psabrgy.shp'						
			flname = tables_dir+prov+'_loczon{}.dbf'.format(rp)
			wdspd_table = ZonalStatisticsAsTable(muni_shp, 'Bgy_Code',prov+"_loc{}".format(rp),flname,'','ALL')

print(time.strftime('%H:%M:%S')+" wooohooo WE OUT!!")