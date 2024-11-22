from core import *
from engine import *


reader = Input_Reader
worker = Worker
output = Output_Writer

worker.file_mover( 'c:/Temp/bygninge3.fgb',  'c:/Temp/bygtemp.fgb')
fileList = worker.file_lister('c:/Temp/', 'fgb')
worker.file_deleter('c:/Temp/bygtemp.fgb')
fileList = worker.file_lister('c:/Temp/', 'fgb')