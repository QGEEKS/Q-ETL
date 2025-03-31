from core import *
from engine import *


reader = Input_Reader
worker = Worker
output = Output_Writer

##Input WFS
input_reader = Input_Reader
wfslayer = input_reader.wfs('https://geofyn.admin.gc2.io/wfs/geofyn/fynbus/25832?SERVICE=WFS&REQUEST=GetFeature&VERSION=1.1.0&TYPENAME=fynbus:routes_25832_v&SRSNAME=urn:ogc:def:crs:EPSG::25832')

params = {
    'INPUT':"WFS:// pagingEnabled='true' preferCoordinatesForWfsT11='false' srsname='EPSG:25832' typename='fynbus:stops_v' url='https://geofyn.admin.gc2.io/wfs/geofyn/fynbus/25832' version='auto'",
    'DISTANCE':10,
    'SEGMENTS':5,
    'END_CAP_STYLE':0,
    'JOIN_STYLE':0,
    'MITER_LIMIT':2,
    'DISSOLVE':False,
    'SEPARATE_DISJOINT':False,
    'OUTPUT':'TEMPORARY_OUTPUT'
    }

buffer = worker.Generic.ProcessingRunner("native:buffer", params)