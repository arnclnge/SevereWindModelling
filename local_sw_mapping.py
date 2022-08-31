"""

TITLE: Mapping local and regional winds 
Date created: June 14, 2019
	
workspace: D:/LOCALWIND/
		
Data needed:
	1. province_psaprov.shp (Place inside folder running_boundaries)
	2. loc500_prov inside Extract.gdb
	3. loc100_prov inside Extract.gdb
	4. symbology layer files
	
Main Outputs: 
	1. local wind maps
	
Open the python application from C:/Python27/ArcGIS10.2/python.exe

Type:
>>>execfile(r'D:/RAPID files/sample python codes/local_sw_mapping.py')

Author: Arienne D. Calonge
E-mail: arnclnge821@gmail.com


"""

import sys
import arcpy
import os
from datetime import datetime
import time
import re

arcpy.CheckOutExtension("Spatial")

#SET INPUTS
arcpy.env.workspace = "D:/LOCALWIND/Extract.gdb"		
mxd = "D:/LOCALWIND/PSA2016_LC2010/Albay_local.mxd"									
running_boundaries = "D:/LOCALWIND/DATA/running_boundaries"		
regional_boundaries = "D:/LOCALWIND/DATA/PSA2016_region_py"
mncp_boundary = "D:/LOCALWIND/DATA/PSA2016_muni"
prov_symbol = "D:/LOCALWIND/DATA/LayerFiles/psaprov_symbol.lyr"
mncp_symbol = "D:/LOCALWIND/DATA/LayerFiles/psamuni_symbol.lyr"
localwind_symbol = "D:/LOCALWIND/DATA/LayerFiles/legend.lyr"
prov_symbol_inset = "D:/LOCALWIND/DATA/LayerFiles/prov_inset.lyr"
region_symbol_inset = "D:/LOCALWIND/DATA/LayerFiles/region_inset.lyr"
output_png = "D:/LOCALWIND/PNG/"

arcpy.env.overwriteOutput = True
print(time.strftime('%H:%M:%S')+" Initialize...")

#---------SELECTING MAP DOC------------#
print("Opening mxd file...")
mxd = arcpy.mapping.MapDocument(mxd)		#location of mxd
df = arcpy.mapping.ListDataFrames(mxd)[0]

for shp in [f for f in os.listdir(running_boundaries) if f.endswith('.shp')]:
	prov = shp.replace('_psaprov.shp','')
	print("Processing "+prov)
	#---------ADD PROVINCIAL BOUNDARY SHPFILE---------# 
	prov_boundary = arcpy.mapping.Layer(running_boundaries+"/"+shp)
	arcpy.mapping.AddLayer(df, prov_boundary,"TOP")
	print("Provincial boundary added")
	prov_boundary_lyr = arcpy.mapping.ListLayers(mxd)[0]
	arcpy.ApplySymbologyFromLayer_management(prov_boundary_lyr, prov_symbol)
	print("Zooming to layer")
	df.extent = prov_boundary_lyr.getSelectedExtent()
	#---------ADD MUNICIPAL BOUNDARY SHPFILE---------# 
	mncp_boundary = arcpy.mapping.Layer(mncp_boundary+"/"+prov+"_psamuni.shp")
	arcpy.mapping.AddLayer(df, mncp_boundary,"TOP")
	print("Municipal boundary added")
	mncp_boundary_lyr = arcpy.mapping.ListLayers(mxd)[0]
	arcpy.ApplySymbologyFromLayer_management(mncp_boundary_lyr, mncp_symbol)
	#---------ADD MUNICIPAL BOUNDARY LABELS---------# 
	print("Adding municipal labels...")
	if mncp_boundary_lyr.supports ("LABELCLASSES"):
		lcs = mncp_boundary_lyr.labelClasses
		lc = lcs[0]
		lc.expression = '[Mun_Name]'
		mncp_boundary_lyr.showLabels = True
	#--------------------UPDATING LAYERS------------------#
	muniboundarylyr = arcpy.mapping.ListLayers(mxd)[0]
	provboundarylyr = arcpy.mapping.ListLayers(mxd)[1]
	#------------CHANGING TEXT ELEMENTS-------------------#
	prov_field = "Pro_Name"	
	region_field = "Reg_Name"
	with arcpy.da.SearchCursor(provboundarylyr,(prov_field,region_field)) as cursor: 
		for row in cursor:
			prov_name = str(row[0])
			reg_name = str(row[1])
			for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*prov"):
				elm.text = "PROVINCE OF " +prov_name
			for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*region"):
				elm.text = reg_name
	print("Title elements changed...")
	#---------INSET MAP DATA FRAMES--------------#
	print("Working data frame: inset map...")
	df_inset = arcpy.mapping.ListDataFrames(mxd)[1]
	#add provincial shpfile
	arcpy.mapping.AddLayer(df_inset, prov_boundary,"TOP")
	print("Provincial shpfile added...")
	#add regional shpfile
	region2_field = "Reg_Name"
	with arcpy.da.SearchCursor(prov_boundary,(region2_field)) as cursor2: 
		for row in cursor2:
			reg_name2 = str(row[0])
			reg_code1 = re.search('\(([^)]+)', reg_name2).group(1)
			reg_code2 = reg_code1.lower()
			inset_rgn_lyr = arcpy.mapping.Layer(regional_boundaries+"/{0}_psaprov.shp".format(reg_code2))
			arcpy.mapping.AddLayer(df_inset,inset_rgn_lyr,"TOP")
	print("Regional shpfile added...")
	#list layers
	rgnboundarylyr_ = arcpy.mapping.ListLayers(mxd, "",df_inset)[0]
	provboundarylyr_ = arcpy.mapping.ListLayers(mxd, "", df_inset)[1]
	#move regional boundary layer
	arcpy.mapping.MoveLayer(df_inset,provboundarylyr_, rgnboundarylyr_,"AFTER")
	print("Regional layer moved after provincial boundary layer...")
	#list layers
	provboundarylyr2 = arcpy.mapping.ListLayers(mxd, "",df_inset)[0]
	rgnboundarylyr2 = arcpy.mapping.ListLayers(mxd, "",df_inset)[1]
	#zoom to layer to regional shpfile
	df_inset.extent = rgnboundarylyr2.getSelectedExtent()
	print("Zoomed to regional boundary layer...")
	#change symbology
	arcpy.ApplySymbologyFromLayer_management(provboundarylyr2, prov_symbol_inset)
	arcpy.ApplySymbologyFromLayer_management(rgnboundarylyr2, region_symbol_inset)
	arcpy.RefreshActiveView()
	print("Layer symbologies changed...")

	#---------ADD LOCAL WIND RASTERS-------------# 
	print("Adding RP500 local wind raster")
	rp500lyr = arcpy.mapping.Layer("loc500_"+prov)
	arcpy.mapping.AddLayer(df, rp500lyr,"TOP")
	print("Reordering RP500 layer...")
	rp500lyr_ = arcpy.mapping.ListLayers(mxd, "", df)[0]
	arcpy.ApplySymbologyFromLayer_management(rp500lyr_, localwind_symbol)
	arcpy.mapping.MoveLayer(df,provboundarylyr, rp500lyr_,"AFTER")
	arcpy.mapping.ExportToPNG(mxd, output_png+"{0}_".format(prov)+"loc500.png", resolution=300)
	print("loc500_"+prov+" exported...")
	rp500lyr_.visible = False
	
	print("Adding RP100 local wind raster")
	rp100lyr = arcpy.mapping.Layer("loc100_"+prov)
	arcpy.mapping.AddLayer(df, rp100lyr,"TOP")
	print("Reordering RP100 layer...")
	rp100lyr_ = arcpy.mapping.ListLayers(mxd)[0]
	arcpy.ApplySymbologyFromLayer_management(rp100lyr_, localwind_symbol)
	arcpy.mapping.MoveLayer(df,provboundarylyr, rp100lyr_,"AFTER")
	for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*title"):
				elm.text = elm.text.replace('500', '100')
				elm.text = elm.text.replace('0.2%', '1%')
	arcpy.mapping.ExportToPNG(mxd, output_png+"{0}_".format(prov)+"loc100.png", resolution=300)
	print("loc100_"+prov+" exported...")
	#-------------REMOVING LAYER FILES---------------#
	print("Removing layer files...")
	arcpy.mapping.RemoveLayer(df,muniboundarylyr)
	arcpy.mapping.RemoveLayer(df,provboundarylyr)
	arcpy.mapping.RemoveLayer(df,rp500lyr)
	arcpy.mapping.RemoveLayer(df_inset,inset_rgn_lyr)
	arcpy.mapping.RemoveLayer(df_inset, provboundarylyr2)
		
			
del mxd
print(time.strftime('%H:%M:%S')+" wooohooo FINISHED!!")	
	
	
	
	
	
	
	
	
	
	
	
	
