
# Q-ETL 

A Python framework to create ETL processes powered by the QGIS engine.

## Documentation
The documentation for Q-ETL is avaialble online [here](https://qgeeks.github.io/Q-ETL/).

## Basic example

This is an example of how to load an input file, reproject the data to WGS84 (EPSG:4326) and write the output to a GeoJSON file.  

```python
reader = Input_Reader
layer = reader.geojson("testdata/kommuner.geojson")

worker = Worker
reprojectedLayer = worker.Vector.reproject(layer, "EPSG:4326")

writer = Output_writer
writer.file(reprojectedLayer, "C:/temp/kommuner_4326.geojson", "GeoJson")
```


## Quickstart
Checkout the _Basic tutorial_ guide on qgeeks.github.io [here](https://qgeeks.github.io/Q-ETL/basic_tutorial/).

## Jupyter Notebooks Support

Q-ETL can be used interactively in Jupyter Notebooks within VS Code. This is great for:
- Interactive development and testing
- Step-by-step debugging of ETL workflows
- Data exploration and visualization
- Creating tutorials and documentation

**Quick Setup:**
```cmd
setup_jupyter.cmd
```

For detailed setup instructions, see:
- 📘 [Full Setup Guide](docs/jupyter_setup.md)
- 🚀 [Quick Reference](JUPYTER_QUICKREF.md)
- 📓 [Example Notebook](demos/development_notebook.ipynb)

## Download
Download the latest release [here](https://github.com/QGEEKS/Q-ETL/releases).



## About the project
The Q-ETL project builds uppon the work of the QGIS project (https://www.qgis.org/). 
The project is not developed, endorsed by, or otherwise realted to the QGIS project. 


