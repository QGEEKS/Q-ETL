from core import *
from engine import *


reader = Input_Reader
worker = Worker
output = Output_Writer

worker.File.mover( 'c:/Temp/bygninge3.fgb',  'c:/Temp/bygtemp.fgb')
fileList = worker.File.lister('c:/Temp/', 'fgb')
worker.File.deleter('c:/Temp/bygtemp.fgb')
fileList = worker.File.lister('c:/Temp/', 'fgb')