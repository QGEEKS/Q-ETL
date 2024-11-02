from core import *
from engine import *

reader = Input_Reader
worker = Worker
writer = Output_Writer

wfs_layer = reader.wfs("srsname='EPSG:25832' typename='fkg:fkg.t_5607_ladefacilitet' url='https://geofa.geodanmark.dk/ows/fkg/fkg")


reprojected_layer = worker.reproject(wfs_layer, 25832)

