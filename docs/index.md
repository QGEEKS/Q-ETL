# Q-ETL

A Python framework to create ETL processes powered bu the QGIS engine <sup>1</sup>.

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

To run the job, simply call the _.cmd_ file, and the job will execute. The translation log os placed in the log directory as specified in the configuration.

See more in the [Getting started](getting_started) section.

## Download
Download the latest release [here](https://github.com/QGEEKS/Q-ETL/releases).

---------
<sup>1</sup> The Q-ETL project builds upon the work of the QGIS project (https://qgis.org). This project si not developed, endorsed by, or otherwise related to the QGIS project.