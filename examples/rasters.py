from engine import *
from core import *

input_reader = Input_Reader
rlayer = input_reader.raster("C:/Temp/DTM_1km_6055_657.tif")

writer = Output_Writer
writer.raster(rlayer, "C:/Temp/DTM_output.tif")
