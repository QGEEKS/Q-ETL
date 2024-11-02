from core import *
from engine import *

reader = Input_Reader
worker = Worker
writer = Output_Writer

wfs_layer = reader.wfs("srsname='EPSG:25832' typename='fkg:fkg.t_5607_ladefacilitet' url='https://geofa.geodanmark.dk/ows/fkg/fkg")

filtered_layer = worker.extractByExpression(wfs_layer, ' "beliggenhedskommune" = 330')

ts_layer = worker.timeStamper(filtered_layer, 'QETL-ts')

writer.postgis(ts_layer, 'MyPostGIS', 'gis', 'qetl', 'ladestandere', True)