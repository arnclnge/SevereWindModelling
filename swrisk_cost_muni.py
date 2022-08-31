"""

TITLE: AUTOMATION OF SEVERE WIND RISK MAPPING FOR ALL MUNICIPALITIES
		(COST)
		
Data needed:
	1. symbology layer file with temp_field (with values of any return period of population) 
		-filename: "symbol_pop.lyr"
	2. risk shpfile 
		-filename: "[municipality]_risk_shp.shp"
	3. mxd file with layout
	4. water bodies and roads per municipality shpfile
	
Outputs: ("D:/workspace_RAPID/py_files/[municipality]")
	1. [municipality]_lyr.lyr
	2. PNG files of population risk maps for all municipalities (resolution: 300 dpi)
	
Open the python application from C:\Python27\ArcGIS10.2\python.exe
Type:
>>>execfile(r'D:/RAPID files/sample python codes/swrisk_pop_muni.py')

Arienne D. Calonge
arnclnge821@gmail.com


"""
# -*- coding: utf-8 -*-

import sys
import arcpy
import os
from datetime import datetime
import time

arcpy.CheckOutExtension("Spatial")

arcpy.env.workspace = "D:/workspace_RAPID/py_files"				#change
main_dir = "D:/workspace_RAPID/py_files/"						#change

arcpy.env.overwriteOutput = True
print(time.strftime('%H:%M:%S')+" Initialize...")

#---------SELECTING MAP DOC------------#
print("Opening mxd file...")
mxd = arcpy.mapping.MapDocument(main_dir+"abuyog/Abuyog_cost.mxd")		#location of mxd
df = arcpy.mapping.ListDataFrames(mxd)[0]

#---------ADD RISK SHPFILE-------------# 		

for shp in [f for f in os.listdir(main_dir+"excel/shpfiles") if f.endswith('.shp')]:	#location of shpfiles
	mncp = shp.replace('_risk_shp.shp','')
	print("Processing "+mncp)
	print("Converting "+shp+ " to layer...")
	arcpy.MakeFeatureLayer_management(main_dir+"excel/shpfiles/"+mncp+"_risk_shp.shp", mncp+"_")	#location of shpfiles
	mncp_risk = mncp+"_"
	arcpy.SaveToLayerFile_management(mncp+"_", main_dir+mncp+"/"+mncp+"_lyr.lyr")					#location of output lyr file
	mncp_lyr = arcpy.mapping.Layer(main_dir+mncp+"/"+mncp+"_lyr.lyr")								#location of output lyr file
	arcpy.mapping.AddLayer(df, mncp_lyr, "TOP") 													
	mncp_lyr_fnl = arcpy.mapping.ListLayers(mxd)[0]
	print("Zooming to layer")
	df.extent = mncp_lyr_fnl.getSelectedExtent()
	
	#------ADD WATER BODIES AND ROADS SHPFILE-----#

	water_dir = "D:/workspace_RAPID/Data/WaterBodies_SamarLeyte/"+mncp+"_water.shp"		#location of water bodies
	water_symbol = main_dir+"symbols/abuyog_water.lyr"
	road_dir = "D:/workspace_RAPID/Data/phil_road/"+mncp+"_road.shp"					#location of roads
	road_symbol = main_dir+"symbols/abuyog_road.lyr"
	
	print("Adding water bodies...")
	arcpy.MakeFeatureLayer_management(water_dir, mncp+"_water")
	arcpy.SaveToLayerFile_management(mncp+"_water", main_dir+mncp+"/"+mncp+"_water.lyr")
	water_lyr = arcpy.mapping.Layer(main_dir+mncp+"/"+mncp+"_water.lyr")
	arcpy.mapping.AddLayer(df, water_lyr, "TOP")
	water_lyr_fnl = arcpy.mapping.ListLayers(mxd)[0]
	arcpy.ApplySymbologyFromLayer_management(water_lyr_fnl, water_symbol)
	
	print("Adding roads...")
	arcpy.MakeFeatureLayer_management(road_dir, mncp+"_road")
	arcpy.SaveToLayerFile_management(mncp+"_road", main_dir+mncp+"/"+mncp+"_road.lyr")
	road_lyr = arcpy.mapping.Layer(main_dir+mncp+"/"+mncp+"_road.lyr")
	arcpy.mapping.AddLayer(df, road_lyr, "TOP")
	road_lyr_fnl = arcpy.mapping.ListLayers(mxd)[0]
	arcpy.ApplySymbologyFromLayer_management(road_lyr_fnl, road_symbol)
	
	#------------ADDING LABELS---------------#
	print("Adding barangay labels...")
	if mncp_lyr_fnl.supports ("LABELCLASSES"):
		lcs = mncp_lyr_fnl.labelClasses
		lc = lcs[0]
		lc.expression = '[Bgy_Name]'
		mncp_lyr_fnl.showLabels = True
		
	#--------CHANGING ELEMENTS--------#
	print("Changing text elements...")
	for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*municipality"):
		elm.text = "MUNICIPALITY OF "+mncp.upper()
	for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*province"):
		if mncp in ('lawaan', 'balangiga'):
			elm.text = "PROVINCE OF EASTERN SAMAR"
		elif mncp in ('basey', 'marabut'):
			elm.text = "PROVINCE OF SAMAR"
		else:
			elm.text = "PROVINCE OF LEYTE"
			
	print("Adjusting scale bar...")
	scaleBar = arcpy.mapping.ListLayoutElements(mxd, "MAPSURROUND_ELEMENT", "Scale Bar")[0]
	scaleBar.elementPositionX = 13.694
	scaleBar.elementPositionY = 9.1785
			
	print("Changing inset map...")
	df2 = arcpy.mapping.ListDataFrames(mxd)[1]
	inset_lyrs = arcpy.mapping.ListLayers(mxd, "", df2)
	for inset_lyr in inset_lyrs:
		if inset_lyr.name == mncp.capitalize():
			inset_lyr.visible = True
		
	print("Inserting water bodies label...")
	for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*water"):
		if mncp in elm.name:
			if elm.name == "abuyog dulag mayorga tolosa water":
				elm.text = "LEYTE GULF"
			elif elm.name == "balangiga lawaan water":
				elm.text = "LEYTE GULF"
			elif elm.name == "basey water":
				elm.text = "SAN PABLO BAY"
			elif elm.name == "palo tanauan water":
				elm.text = "SAN PABLO BAY"
			elif elm.name == "macarthur water":
				elm.text = "LEYTE GULF"
			elif elm.name == "basey san juanico water":
				elm.text = "SAN JUANICO STRAIT"
			elif elm.name == "marabut water":
				elm.text = "SAN PABLO BAY"
		
	arcpy.RefreshActiveView()
	
	#---------APPLY SYMBOLOGY--------------#
	symbol = arcpy.mapping.Layer(main_dir+"abuyog/symbol_pop.lyr")				#location of symbol lyr file
	
	
	print("Adding temporary field for symbology...")
	arcpy.AddField_management(mncp_lyr, 'temp_field', "FLOAT")
	fields = [field.name for field in arcpy.ListFields(mncp_lyr_fnl) if field.name <> 'temp_field']
	
	print("Looping through each field...")
	for field in fields:
		if "POP200" in field:
			arcpy.CalculateField_management(mncp_lyr_fnl, 'temp_field', "!{0}!".format(field), "PYTHON_9.3")
			arcpy.ApplySymbologyFromLayer_management(mncp_lyr_fnl, symbol)
			for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*title"):
				elm.text = elm.text.replace('20', '200')
				elm.text = elm.text.replace('5%', '0.5%')
			arcpy.RefreshActiveView()
			arcpy.mapping.ExportToPNG(mxd, os.path.join(main_dir+mncp+"/"+mncp+"_{0}.png".format(field)), resolution=300)
			print(mncp+"_POP_200.png exported")
			
		if "POP100" in field:
			arcpy.CalculateField_management(mncp_lyr_fnl, 'temp_field', "!{0}!".format(field), "PYTHON_9.3")
			arcpy.ApplySymbologyFromLayer_management(mncp_lyr_fnl, symbol)
			for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*title"):
				elm.text = elm.text.replace('200', '100')
				elm.text = elm.text.replace('0.5%', '1%')
			arcpy.RefreshActiveView()
			arcpy.mapping.ExportToPNG(mxd, os.path.join(main_dir+mncp+"/"+mncp+"_{0}.png".format(field)), resolution=300)
			print(mncp+"_POP_100.png exported")
			
		if "POP50" in field:
			arcpy.CalculateField_management(mncp_lyr_fnl, 'temp_field', "!{0}!".format(field), "PYTHON_9.3")
			arcpy.ApplySymbologyFromLayer_management(mncp_lyr_fnl, symbol)
			for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*title"):
				elm.text = elm.text.replace('100', '50')
				elm.text = elm.text.replace('1%', '2%')
			arcpy.RefreshActiveView()
			arcpy.mapping.ExportToPNG(mxd, os.path.join(main_dir+mncp+"/"+mncp+"_{0}.png".format(field)), resolution=300)
			print(mncp+"_POP_50.png exported")
			
		if "POP20" in field:
			arcpy.CalculateField_management(mncp_lyr_fnl, 'temp_field', "!{0}!".format(field), "PYTHON_9.3")
			arcpy.ApplySymbologyFromLayer_management(mncp_lyr_fnl, symbol)
			for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*title"):
				elm.text = elm.text.replace('50', '20')
				elm.text = elm.text.replace('2%', '5%')
			arcpy.RefreshActiveView()
			arcpy.mapping.ExportToPNG(mxd, os.path.join(main_dir+mncp+"/"+mncp+"_{0}.png".format(field)), resolution=300)
			print(mncp+"_POP_20.png exported")
			
		if "POP500" in field:
			arcpy.CalculateField_management(mncp_lyr_fnl, 'temp_field', "!{0}!".format(field), "PYTHON_9.3")
			arcpy.ApplySymbologyFromLayer_management(mncp_lyr_fnl, symbol)
			for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*title"):
				elm.text = elm.text.replace('20', '500')
				elm.text = elm.text.replace('5%', '0.2%')
			arcpy.RefreshActiveView()
			arcpy.mapping.ExportToPNG(mxd, os.path.join(main_dir+mncp+"/"+mncp+"_{0}.png".format(field)), resolution=300)
			print(mncp+"_POP_500.png exported")
	
	#-------------REMOVING LAYER FILES---------------#
	for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "*water"):
		if mncp in elm.name:
			elm.text = " "
	for inset_lyr in inset_lyrs:
		if inset_lyr.name == mncp.capitalize():
			inset_lyr.visible = False
	print("Water bodies & inset map cleared...")
	print("Removing layer files...")
	arcpy.Delete_management(main_dir+mncp+"/"+mncp+"_lyr.lyr")
	arcpy.mapping.RemoveLayer(df,mncp_lyr_fnl)
	arcpy.mapping.RemoveLayer(df,water_lyr_fnl)
	arcpy.mapping.RemoveLayer(df,road_lyr_fnl)
	print("Deleting temp_field...")
	arcpy.DeleteField_management(mncp_lyr, 'temp_field')
	print(time.strftime('%H:%M:%S'))


#-------------DELETING VARIABLES-----------------#


del mxd, mncp_risk, mncp_lyr, mncp_lyr_fnl, symbol, fields, inset_lyrs


print(time.strftime('%H:%M:%S')+" wooohooo WE OUT!!")
	
	
