"""

TITLE: AUTOMATION OF SEVERE WIND MS AND MZ VALUES, DEM.ASC (octave)
	
		
Data needed:
	1. DTM & DSM
	2. .gdb folder for the multiplier and set it as the workspace
	3. provincial boundary shpfile
	4. land cover shpfile
	
Main Outputs: 
	1. Ms_orig raster
	2. Mz_orig raster
    3. topo/input/dem.asc (for octave)
    4. dtm_asc.txt , dtm_asc.prj
    5. empty terrain folder
    6. empty shielding folder
    7. topo folder with input, mfiles, and output folders
	
Open the python application from C:/Python27/ArcGIS10.2/python.exe

Type:
>>>execfile(r'C:/DATA/ARIENNE/ms_mz.py')

Arienne D. Calonge
arnclnge821@gmail.com


"""


import os
import sys
import arcpy
from arcpy.sa import *
from datetime import datetime
import time
import shutil

arcpy.CheckOutExtension("Spatial")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 51N")
#exec(open('C:/DATA/ARIENNE/ms_mz_inputs.py').read())

##############################################################################################
#------------------------------------------SET INPUTS----------------------------------------#

output_dir          = "C:/DATA/2019_PHIL_MULTIPLIERS/LUZON/palawan_c2_psa2016_py"                             #set to main folder
province_key        = 'palawan_c2'	

boundary_dir_copy   = "C:/DATA/2019_PHIL_MULTIPLIERS/Data/PSA2016_province_py/"                #set to directory of shpfile bou
dtm_dir             = "C:/DATA/Data/Philippine_DTM/phwgs84_dtm"
dsm_dir             = "C:/DATA/Data/Philippine_DSM/phwgs84_dsm"
bulc_dir            = "C:/DATA/2019_PHIL_MULTIPLIERS/Data/2015 Land Cover Data/lc2015_pal_builtup.shp"  #set land cover built-up data
veglc_dir           = "C:/DATA/2019_PHIL_MULTIPLIERS/Data/2015 Land Cover Data/lc2015_pal_veg.shp"      #set land cover vegetation data
water_dir           = "C:/DATA/2019_PHIL_MULTIPLIERS/Data/2015 Land Cover Data/lc2015_pal_water.shp"    #set land cover water data
mfiles_dir          = "C:/DATA/Data/m-files"
gawk_dir            = "C:/gawk-3.1.6-1-bin/bin"

##############################################################################################


#--------------------------------------------------------------------------------------------#

#Initialize
arcpy.env.overwriteOutput = True
print(time.strftime('%H:%M:%S')+" "+province_key+": Initialize...")

#create main folder
os.makedirs(output_dir)

#create a file geodatabase
arcpy.CreateFileGDB_management(output_dir, province_key+"_mult.gdb")
arcpy.env.workspace = "{}/{}_mult.gdb".format(output_dir,province_key)
print("Geodatabase created...")

#copy shpfile boundary
source = os.listdir(boundary_dir_copy)
for f in source:
    if f.startswith(province_key):
        print("Copying "+f)
        shutil.copy(boundary_dir_copy+f,output_dir)

boundary_dir = output_dir+'/{}_psaprov.shp'.format(province_key)

#-------------------------------------------------------------------------------------------------------#

#extract by mask: DSM & DTM
DTM_extract = ExtractByMask(dtm_dir, boundary_dir)
DTM_extract.save("dtm")
print("DTM extracted...")
DSM_extract = ExtractByMask(dsm_dir, boundary_dir)
DSM_extract.save("dsm")
print("DSM extracted...")

#calculate land cover heights
LCHT_raster = Raster("dsm") - Raster("dtm")
LCHT_raster.save("lcht")
print("Land cover heights calculated...")

#-------------------------------------------BUILT-UP----------------------------------------------------#
#extract by mask IFSAR LCHT with NAMRIA's landcover2010 built-up
buht_extract = ExtractByMask("lcht", bulc_dir)
buht_extract.save("buht")
print("Built-up LCHT extracted...")

#Get minimum & maximum elevation of buht
buhtMin = arcpy.GetRasterProperties_management("buht","MINIMUM")
buhtMin_elev= buhtMin.getOutput(0)
print("Minimum elev of BU ="+buhtMin_elev)
buhtMax = arcpy.GetRasterProperties_management("buht", "MAXIMUM")
buhtMax_elev = buhtMax.getOutput(0)
print("Maximum elev of BU ="+buhtMax_elev)

#reclassify buht according to GeoScience Australia's Terrain Classification table
buht_reclass = Reclassify("buht", "Value", RemapRange([[buhtMin_elev,1,10], [1,5,6],[5,10,5],[10,20,4],[20,buhtMax_elev,1]]), "NODATA")
buht_reclass.save("bulc")
print("BULC values reclassified...")


#---------------------------------------VEGETATION---------------------------------------------------------#
#extract by mask IFSAR LCHT with NAMRIA's landcover2010 vegetation
veght_extract = ExtractByMask("lcht", veglc_dir)
veght_extract.save("veght")
print("Vegetation LCHT extracted...")

#Get minimum & maximum elevation of veght
veghtMin = arcpy.GetRasterProperties_management("veght","MINIMUM")
veghtMin_elev= veghtMin.getOutput(0)
print("Minimum elev of Veg ="+veghtMin_elev)
veghtMax = arcpy.GetRasterProperties_management("veght", "MAXIMUM")
veghtMax_elev = veghtMax.getOutput(0)
print("Maximum elev of Veg ="+veghtMax_elev)

#reclassify veght according to GeoScience Australia's Terrain Classification table
veght_reclass = Reclassify("veght", "Value", RemapRange([[veghtMin_elev,0.5,11], [0.5,1,10],[1,3,9],[3,10,8],[10,veghtMax_elev,3]]), "NODATA")
veght_reclass.save("veglc")
print("VEGLC values reclassified...")


#-------------------------------------WATER-------------------------------------------------------------------#
#clip water land cover
arcpy.Clip_analysis(water_dir, boundary_dir, "water")
print("Water bodies clipped...")

#add new field to water shpfiles
arcpy.AddField_management("water", "code", "FLOAT",12,8)
arcpy.CalculateField_management("water", 'code',"11","PYTHON_9.3")

#convert water shp to raster
arcpy.PolygonToRaster_conversion("water","code","watermask","CELL_CENTER","code",20)
print("Water bodies shpfile converted to raster")


#--------------------------------LAND COVER RASTER---------------------------------------------------#
ConstRaster = CreateConstantRaster(11, "INTEGER",20,boundary_dir)
ConstRaster.save("landcover")
arcpy.Mosaic_management("veglc;bulc;watermask","landcover","LAST","FIRST","","","","","NONE")
print("Created land cover raster...")

#----------------------------------TERRAIN: Mz VALUES------------------------------------------------#
landcover_reclass = Reclassify("landcover", "Value", RemapValue([[1,66], [3,70],[4,71],[5,74],[6,77],[8,82],[9,84],[10,89],[11,96]]))
landcover_reclass.save("Mz_int")
Mz_raster = Float(Raster("Mz_int"))*0.01
Mz_raster.save(output_dir+"/Mz_orig")
print("Mz_orig created...")

#----------------------------------SHIELDING: Ms VALUES------------------------------------------------#
landcover_reclass2 = Reclassify("landcover", "Value", RemapValue([[1,70], [3,100],[4,70],[5,80],[6,85],[8,100],[9,100],[10,100],[11,100]]))
landcover_reclass2.save("Ms_int")
Ms_raster = Float(Raster("Ms_int"))*0.01
Ms_raster.save(output_dir+"/Ms_orig")
print("Ms_orig created...")

#---------------------------------CONVERTING DTM RASTER TO ASCII FOR TOPO------------------------------------------------------#
arcpy.RasterToASCII_conversion("dtm",output_dir+"/dtm_asc.txt")
print("DTM raster converted to ASCII...")

#---------------------------------CREATING DIRECTORIES--------------------------------------#

terrain_path = output_dir+"/terrain"
shielding_path = output_dir+"/shielding"
topo_path = output_dir+"/topo"
topo_input_path = output_dir+"/topo/input"
topo_output_path = output_dir+"/topo/output"
#create shielding, terrain & topo folders
os.makedirs(terrain_path)
os.makedirs(shielding_path)
os.makedirs(topo_path)
os.makedirs(topo_input_path)
os.makedirs(topo_output_path)
print("shielding, topo, and terrain directories created")

#--------------------------PREPARING FILES FOR RUNNING OF TOPO OCTAVE----------------------#

#copy m-files
shutil.copytree(mfiles_dir,topo_path+"/m-files")
print("m-files copied")

#copy dtm_asc.txt to bin folder of gawk-3.1.6-1-bin
dtm_asc_txt = output_dir+"/dtm_asc.txt"
shutil.copyfile(dtm_asc_txt,gawk_dir+"/"+province_key+"dtm_asc.txt")
print("dtm_asc.txt copied to bin folder of gawk-3.1.6-1-bin")


#convert dtm_asc.txt to dtm_asc.asc
    #   cmd = gawk_dir+"/gawk.exe -f "+gawk_dir+"/convert.awk "+gawk_dir+"/"+province_key+"dtm_asc.txt > "+gawk_dir+"/"+province_key+"dtm_asc.asc"
    #   os.system(cmd)

os.chdir(gawk_dir)
cmd = "gawk.exe -f convert.awk "+province_key+"dtm_asc.txt > "+province_key+"dtm_asc.asc"
os.system(cmd)
print("dtm_asc.txt converted to dtm_asc.asc")


#copy dtm_asc.asc to topo/input as dem.asc
dtm_asc_asc = gawk_dir+"/"+province_key+"dtm_asc.asc"
shutil.copyfile(dtm_asc_asc,topo_input_path+"/dem.asc")
print("dtm_asc.asc copied to topo/input as dem.asc")


print(time.strftime('%H:%M:%S')+" DONE! Next step is to run convolveTerrain2.py and octave")























