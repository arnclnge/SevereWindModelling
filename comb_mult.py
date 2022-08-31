"""

TITLE: AUTOMATION OF COMBINED MULTIPLIER FOR SEVERE WIND 
	
		
Data needed:
	1. DTM 
    2. output of convolveTerrain2.py shielding img files
    3. output of convolveTerrain2.py terrain img files
    4. output of octave topo files
 
	
Main Outputs: 
	1. max_ms
    2. max_mz
    3. max_mh
    4. comb_mult
    5. m4 files
	
Open the python application from C:/Python27/ArcGIS10.2/python.exe

Type:
>>>execfile(r'C:/DATA/ARIENNE/comb_mult.py')

Arienne D. Calonge
arnclnge821@gmail.com


"""

import os
import glob
import sys
import arcpy
from arcpy.sa import *
from datetime import datetime
import time

arcpy.CheckOutExtension("Spatial")

#SET INPUTS!
arcpy.env.workspace = 'C:/DATA/2019_PHIL_MULTIPLIERS/LUZON/palawan_d_psa2016_py/palawan_d_mult.gdb'
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 51N")
province_key = 'palawan_d'	
shield_dir = 'C:/DATA/2019_PHIL_MULTIPLIERS/LUZON/palawan_d_psa2016_py/shielding'
terrain_dir = 'C:/DATA/2019_PHIL_MULTIPLIERS/LUZON/palawan_d_psa2016_py/terrain'
topo_dir = 'C:/DATA/2019_PHIL_MULTIPLIERS/LUZON/palawan_d_psa2016_py/topo/output'
out_files = 'C:/DATA/2019_PHIL_MULTIPLIERS/LUZON/palawan_d_psa2016_py'
#Import windshield model toolbox
arcpy.ImportToolbox('C:/DATA/Data/Windtools _updatedversion_nobutas/Multiplier Tools.tbx','MultiplierTools')

#delete contents of temp folder
temp_dir = glob.glob('C:temp/*')
for f in temp_dir:
    os.remove(f)

print(time.strftime('%H:%M:%S')+" Initialize...")
arcpy.env.overwriteOutput = True

#---------------------------------------------COMPUTATION OF MAX_MS------------------------------------------#

#Set Null the negative values of dtm 
DTM_null = SetNull("dtm","dtm","value < 0")
DTM_null.save("dtm_null")
print("DTM negative values converted to null...")

#Compute for slope 
outSlope = Slope("dtm_null","PERCENT_RISE",1)
outSlope.save("slope")
print("Slope created...")

#Compute for aspect
outAspect = Aspect("dtm")
outAspect.save("aspect")
print("Aspect created...")

#Reclassify aspect
outReclass = Reclassify("aspect","value",RemapRange([[-1,0,9], [0,22.5,1],[22.5,67.5,2],[67.5,112.5,3],[112.5,157.5,4],[157.5,202.5,5],[202.5,247.5,6],[247.5,292.5,7],[292.5,337.5,8],[337.5,360,1]]), "NODATA")
outReclass.save("aspect_rec")
print("Aspect reclassified...")

#Run shield model for 8 directions
arcpy.Shield3_MultiplierTools(slope_legazp1="slope",reclass_aspe1="aspect_rec",shield_orig=shield_dir+"/shield_W.img",ms_orig="ms_w_sh",Where_clause__2_="Value=7",Where_clause__3_="Value<>7")
print("ms_w_sh produced...")
arcpy.Shield3_MultiplierTools(slope_legazp1="slope",reclass_aspe1="aspect_rec",shield_orig=shield_dir+"/shield_SW.img",ms_orig="ms_sw_sh",Where_clause__2_="Value=6",Where_clause__3_="Value<>6")
print("ms_sw_sh produced...")
arcpy.Shield3_MultiplierTools(slope_legazp1="slope",reclass_aspe1="aspect_rec",shield_orig=shield_dir+"/shield_SE.img",ms_orig="ms_se_sh",Where_clause__2_="Value=4",Where_clause__3_="Value<>4")
print("ms_se_sh produced...")
arcpy.Shield3_MultiplierTools(slope_legazp1="slope",reclass_aspe1="aspect_rec",shield_orig=shield_dir+"/shield_S.img",ms_orig="ms_s_sh",Where_clause__2_="Value=5",Where_clause__3_="Value<>5")
print("ms_s_sh produced...")
arcpy.Shield3_MultiplierTools(slope_legazp1="slope",reclass_aspe1="aspect_rec",shield_orig=shield_dir+"/shield_NW.img",ms_orig="ms_nw_sh",Where_clause__2_="Value=8",Where_clause__3_="Value<>8")
print("ms_nw_sh produced...")
arcpy.Shield3_MultiplierTools(slope_legazp1="slope",reclass_aspe1="aspect_rec",shield_orig=shield_dir+"/shield_NE.img",ms_orig="ms_ne_sh",Where_clause__2_="Value=2",Where_clause__3_="Value<>2")
print("ms_ne_sh produced...")
arcpy.Shield3_MultiplierTools(slope_legazp1="slope",reclass_aspe1="aspect_rec",shield_orig=shield_dir+"/shield_N.img",ms_orig="ms_n_sh",Where_clause__2_="Value=1",Where_clause__3_="Value<>1")
print("ms_n_sh produced...")
arcpy.Shield3_MultiplierTools(slope_legazp1="slope",reclass_aspe1="aspect_rec",shield_orig=shield_dir+"/shield_E.img",ms_orig="ms_e_sh",Where_clause__2_="Value=3",Where_clause__3_="Value<>3")
print("ms_e_sh produced...")

#Compute max_ms
max_ms = CellStatistics(["ms_w_sh","ms_e_sh","ms_n_sh","ms_ne_sh","ms_nw_sh","ms_s_sh","ms_se_sh","ms_sw_sh"],"MAXIMUM","NODATA")
max_ms.save(out_files+"/max_ms")
print("Maximum shielding multiplier computed...")

#--------------------------------------------------COMPUTATION OF MAX_MZ------------------------------------------------#

#Compute max_mz
max_mz = CellStatistics([terrain_dir+'/mz_E.img',
                         terrain_dir+'/mz_N.img',
                         terrain_dir+'/mz_NE.img',
                         terrain_dir+'/mz_NW.img',
                         terrain_dir+'/mz_S.img',
                         terrain_dir+'/mz_SE.img',
                         terrain_dir+'/mz_SW.img',
                         terrain_dir+'/mz_W.img'],"MAXIMUM","NODATA")
max_mz.save(out_files+"/max_mz")
print("Maximum terrain multiplier computed...")

#--------------------------------------------------COMPUTATION OF MAX_MH------------------------------------------------#

for ascii in [f for f in os.listdir(topo_dir) if f.endswith('smooth.asc')]:
    dir = ascii.replace('mh_','').replace('_smooth.asc','')
    arcpy.ASCIIToRaster_conversion(topo_dir+'/'+ascii,"mh_"+dir+"_ras","FLOAT")
    print("mh_"+dir+"_smooth.asc"+" converted to raster...")
    
print('ASCII files loaded...')

#Compute max_mh
max_mh = CellStatistics(['mh_e_ras','mh_n_ras','mh_ne_ras','mh_nw_ras','mh_s_ras','mh_se_ras','mh_sw_ras','mh_w_ras'],"MAXIMUM","NODATA")
max_mh.save(out_files+"/max_mh")
print("Maximum topo multiplier computed...")

#-------------------------------------------------COMBINED MULTIPLIER----------------------------------------------------#
#Compute for combined mult
comb_mult = Raster(out_files+"/max_ms")*Raster(out_files+"/max_mz")*Raster(out_files+"/max_mh")
comb_mult.save(out_files+"/combmult")
print("Combined multiplier created...")

#-------------------------------------------------COMPUTATION OF m4 FILES--------------------------------------------#
#create folder for m4 files
m4_path = out_files+"/"+province_key+"_m4files"
os.makedirs(m4_path)
print("m4 files folder created")

#compute for m4 for all directions
m4_max = Raster(out_files+"/max_ms")*Raster(out_files+"/max_mz")*Raster(out_files+"/max_mh")
m4_max.save(m4_path+"/m4_max")
print("m4_max created")

m4_n = Raster(terrain_dir+'/mz_N.img')*Raster('ms_n_sh')*Raster('mh_n_ras')
m4_n.save(m4_path+"/m4_n")
print("m4_n created")

m4_e = Raster(terrain_dir+'/mz_E.img')*Raster('ms_e_sh')*Raster('mh_e_ras')
m4_e.save(m4_path+"/m4_e")
print("m4_e created")

m4_w = Raster(terrain_dir+'/mz_W.img')*Raster('ms_w_sh')*Raster('mh_w_ras')
m4_w.save(m4_path+"/m4_w")
print("m4_w created")

m4_s = Raster(terrain_dir+'/mz_S.img')*Raster('ms_s_sh')*Raster('mh_s_ras')
m4_s.save(m4_path+"/m4_s")
print("m4_s created")

m4_se = Raster(terrain_dir+'/mz_SE.img')*Raster('ms_se_sh')*Raster('mh_se_ras')
m4_se.save(m4_path+"/m4_se")
print("m4_se created")

m4_sw = Raster(terrain_dir+'/mz_SW.img')*Raster('ms_sw_sh')*Raster('mh_sw_ras')
m4_sw.save(m4_path+"/m4_sw")
print("m4_sw created")

m4_nw = Raster(terrain_dir+'/mz_NW.img')*Raster('ms_nw_sh')*Raster('mh_nw_ras')
m4_nw.save(m4_path+"/m4_nw")
print("m4_nw created")

m4_ne = Raster(terrain_dir+'/mz_NE.img')*Raster('ms_ne_sh')*Raster('mh_ne_ras')
m4_ne.save(m4_path+"/m4_ne")
print("m4_ne created")


print(time.strftime('%H:%M:%S')+" ["+province_key+"] "+" WOHOO IT'S DONE!")















