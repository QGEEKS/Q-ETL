
# Q-ETL 

A Python framework to create ETL processes powered by the QGIS engine.

## Basic example

This is an example of how to load an input file, reproject the data to WGS84 (EPSG:4326) and write the output to a GeoJSON file.  

```python
reader = Input_Reader
layer = reader.geojson("testdata/kommuner.geojson")

worker = Worker
reprojectedLayer = worker.reproject(layer, "EPSG:4326")

writer = Output_writer
writer.file(reprojectedLayer, "C:/temp/kommuner_4326.geojson", "GeoJson")
```

## Quickstart
Checkout the _Basic tutorial_ guide on qgeeks.github.io [here](https://qgeeks.github.io/Q-ETL/basic_tutorial/).

## Download
Download the latest release [here](https://github.com/QGEEKS/Q-ETL/releases).


## About the project
The Q-ETL project builds uppon the work of the QGIS project (https://www.qgis.org/). 
The project is not developed, endorsed by, or otherwise realted to the QGIS project. 


