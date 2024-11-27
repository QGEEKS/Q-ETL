from core import *
from engine import *

reader = Input_Reader
worker = Worker
output = Output_Writer
const = Constructor

point = const.layerFromWKT('Point', ['POINT(713066.7674185499 6179943.648046177)'], 25832)
parameters = {
                'bufferdist': 100,
                'input':point,
                'Output': 'memory:buffer'
            }
result = processing.run("script:BufferModel", parameters )
output.geopackage(result['Output'], 'buffermodel', 'c:/Temp/modeloutput.gpkg', True)