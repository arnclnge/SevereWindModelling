"""

TITLE: PRODUCTION OF SYMBOLOGY LAYERS FOR INPUT TO RISK AUTOMATION


Data needed:
	1. risk shpfile (output of swrisk_shpfile.py)
	2. sample symbology layer file (abuyog_symbol_vuln.lyr)
	3. empty mxd file (symbols_py.mxd)

Open the python application from C:\Python27\ArcGIS10.2\python.exe

OUTPUTS: 
	1. symbol layer files (D:/workspace_RAPID/py_files/symbols/test)

Type:
>>>execfile(r'D:/RAPID files/sample python codes/swrisk_vuln_symbol.py')

Author: Arienne D. Calonge
E-mail: arnclnge821@gmail.com


"""


import sys
import arcpy
import os
from datetime import datetime
import time

arcpy.env.workspace = "D:/workspace_RAPID/py_files"				#change
main_dir = "D:/workspace_RAPID/py_files/"						#change
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

print(time.strftime('%H:%M:%S')+" Initialize...")

mxd = arcpy.mapping.MapDocument(main_dir+"symbols/symbols_py.mxd")		#change
df = arcpy.mapping.ListDataFrames(mxd)[0]

for shp in [f for f in os.listdir(main_dir+"excel/shpfiles") if f.endswith('.shp')]:	#location of shpfiles
	symbol = arcpy.mapping.Layer(main_dir+"symbols/abuyog_symbol_vuln.lyr")				#location of symbol lyr file
	mncp = shp.replace('_risk_shp.shp','')
	
	print("Making Feature Layer...")
	arcpy.MakeFeatureLayer_management(main_dir+"excel/shpfiles/"+mncp+"_risk_shp.shp", mncp+"_2")
	mncp_risk = mncp+"_2"
	arcpy.SaveToLayerFile_management(mncp+"_2", main_dir+"symbols/"+mncp+"_lyr.lyr")			
	mncp_lyr = arcpy.mapping.Layer(main_dir+"symbols/"+mncp+"_lyr.lyr")
	arcpy.mapping.AddLayer(df, mncp_lyr, "TOP") 
	mncp_lyr_fnl = arcpy.mapping.ListLayers(mxd)[0]
	
	print("Adding temporary field...")
	arcpy.AddField_management(mncp_lyr_fnl, 'temp_field', "FLOAT")
	arcpy.CalculateField_management(mncp_lyr_fnl, 'temp_field', "!V_200_FLRA!", "PYTHON_9.3")
	
	print("Applying symbology...")
	arcpy.ApplySymbologyFromLayer_management(mncp_lyr_fnl, symbol)
	
	print("Applying barangay label...")
	if mncp_lyr_fnl.supports ("LABELCLASSES"):
		lcs = mncp_lyr_fnl.labelClasses
		print(lcs)
		lc = lcs[0]
		lc.expression = '[Bgy_Name]'
		mncp_lyr_fnl.showLabels = True
	
	arcpy.SaveToLayerFile_management(mncp_lyr_fnl, main_dir+"symbols/test/"+mncp+"_symbol_vuln.lyr")
	arcpy.Delete_management(main_dir+"symbols/"+mncp+"_lyr.lyr")
	arcpy.DeleteField_management(mncp_lyr, 'temp_field')

del mxd, df, mncp, mncp_lyr, mncp_lyr_fnl, lc, lcs

print(time.strftime('%H:%M:%S')+" Initialize...")
print("Symbol layers successfully created.")
