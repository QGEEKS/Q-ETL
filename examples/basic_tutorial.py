from core import *
from engine import *

reader = Input_Reader
worker = Worker
writer = Output_Writer

wfslayer = reader.wfs("srsname='EPSG:25832' typename='fkg:fkg.t_5800_fac_pkt' url= 'httpS://geofa.geodanmark.dk/ows/fkg/fkg'")

filteredLayer = worker.Vector.extractByExpression(wfslayer, '"beliggenhedskommune" =330')

ts_layer= worker.Vector.addTimestamp(filteredLayer, "qetl_ts")

writer.postgis(ts_layer, "MyPostGIS", "gis", "qetl", "ladestandere", True)