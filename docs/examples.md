# Examples

This page contains practical examples demonstrating various use cases and workflows with Q-ETL. Examples are organized by complexity, starting with the simplest workflows and progressing to more advanced scenarios.

## Table of Contents

**Beginner Level:**

1. [Simple Reprojection](#simple-reprojection) - Basic coordinate system transformation
2. [Basic Input and Output](#basic-input-and-output) - Fundamental read, process, write workflow
3. [File Management Operations](#file-management-operations) - Managing files without GIS processing

**Intermediate Level:**

4. [Attribute Selection and Auto-Incremental Fields](#attribute-selection-and-auto-incremental-fields) - Filtering and field manipulation
5. [Filter Data and Save to PostGIS](#filter-data-and-save-to-postgis) - Database operations
6. [Datafordeleren WFS with SQL Filter](#datafordeleren-wfs-with-sql-filter) - Authentication and SQL filtering

**Advanced Level:**

7. [WFS with Clip Analysis](#wfs-with-clip-analysis) - Spatial analysis operations
8. [Load, Fix Geometry, and Extract Area](#load-fix-geometry-and-extract-area) - Geometry validation workflows
9. [Generic Processing with QGIS Algorithms](#generic-processing-with-qgis-algorithms) - Direct QGIS processing access

**Expert Level:**

10. [Batch Processing from Plandata WFS to PostGIS](#batch-processing-from-plandata-wfs-to-postgis) - Loop processing and database management
11. [Download and Process ZIP with GeoJSON Files](#download-and-process-zip-with-geojson-files) - Complete automated workflow

---

## Simple Reprojection

A straightforward example of coordinate system transformation:

```python
from engine import *
from core import *

# Reading from WFS into a QGIS layer
input_reader = Input_Reader
wfslayer = input_reader.wfs('https://geofyn.admin.gc2.io/wfs/geofyn/fynbus/25832?SERVICE=WFS&REQUEST=GetFeature&VERSION=1.1.0&TYPENAME=fynbus:routes_25832_v&SRSNAME=urn:ogc:def:crs:EPSG::25832')

# Reprojecting the WFS layer to EPSG:4326 from EPSG:25832
worker = Worker
reprojectedLayer = worker.Vector.reproject(wfslayer, 'EPSG:4326')

# Writing the QGIS layer to a GeoJSON file
output_writer = Output_Writer
output_writer.file(reprojectedLayer, "C:/temp/reproject.geojson", "GeoJson")
```

**Key concepts:**

- Coordinate system transformation from UTM (EPSG:25832) to WGS84 (EPSG:4326)
- EPSG code can be provided as integer or string format
- Common pattern for preparing data for web mapping applications

## Basic Input and Output

A simple example demonstrating the fundamental workflow of reading, processing, and writing data:

```python
from engine import *
from core import *

# Reading from WFS into a QGIS layer
input_reader = Input_Reader
wfslayer = input_reader.wfs('https://geofyn.admin.gc2.io/wfs/geofyn/fynbus/25832?SERVICE=WFS&REQUEST=GetFeature&VERSION=1.1.0&TYPENAME=fynbus:routes_25832_v&SRSNAME=urn:ogc:def:crs:EPSG::25832')

worker = Worker
reprojectedlayer = worker.Vector.reproject(wfslayer, 4326)

# Writing the QGIS layer to a GeoJSON file
output_writer = Output_Writer
output_writer.file(wfslayer, 'c:/temp/wfs.geojson', 'GeoJson')
```

**Key concepts:**

- `reader.wfs()` - Loads data from a WFS endpoint
- `worker.Vector.reproject()` - Reprojects to a different CRS
- `output_writer.file()` - Writes layer to file format (GeoJSON, Shapefile, etc.)
- Direct WFS URL with GetFeature request

## File Management Operations

This example shows basic file system operations for managing data files:

```python
from core import *
from engine import *

reader = Input_Reader
worker = Worker
output = Output_Writer

# Move a file
worker.File.mover('c:/Temp/bygninge3.fgb', 'c:/Temp/bygtemp.fgb')

# List all FlatGeobuf files in directory
fileList = worker.File.lister('c:/Temp/', 'fgb')

# Delete a file
worker.File.deleter('c:/Temp/bygtemp.fgb')

# List files again to verify deletion
fileList = worker.File.lister('c:/Temp/', 'fgb')
```

**Key concepts:**

- `worker.File.mover()` - Moves or renames files
- `worker.File.lister()` - Lists files in a directory by extension
- `worker.File.deleter()` - Deletes files
- Useful for managing temporary files and organizing outputs
- File operations can be integrated into ETL workflows for data management

## Attribute Selection and Auto-Incremental Fields

This example shows how to select features and add ID fields:

```python
from engine import *
from core import *

# Reading from WFS into a QGIS layer
input_reader = Input_Reader
wfslayer = input_reader.wfs("srsname='EPSG:4326' typename='ms:continents' url='https://demo.mapserver.org/cgi-bin/wfs' version='2.0.0'")

# Selecting features with attribute NA2DESC = 'Denmark'
worker = Worker
denmarkLayer = worker.Vector.extractByExpression(wfslayer, '"NA2DESC" = \'Denmark\'')

# Add incremental ID field
fidLayer = worker.Vector.addAutoIncrementalField(denmarkLayer, 'FID', 0)

# Export to GeoJSON
output_writer = Output_Writer
output_writer.file(fidLayer, "C:/temp/denmark.geojson", "GeoJson")
```

**Key concepts:**

- `worker.Vector.extractByExpression()` - Filters features using expressions
- `worker.Vector.addAutoIncrementalField()` - Adds sequential ID field starting at specified value
- String escaping in expressions (using `\'` for single quotes within the expression)
- Useful for adding unique identifiers to features

## Filter Data and Save to PostGIS

This example demonstrates filtering and saving to a database:

```python
from core import *
from engine import *

reader = Input_Reader
worker = Worker
writer = Output_Writer

# Load facility points from WFS
wfslayer = reader.wfs("srsname='EPSG:25832' typename='fkg:fkg.t_5800_fac_pkt' url='https://geofa.geodanmark.dk/ows/fkg/fkg'")

# Filter features by municipality code
filteredLayer = worker.Vector.extractByExpression(wfslayer, '"beliggenhedskommune" = 330')

# Add timestamp field
ts_layer = worker.Vector.addTimestamp(filteredLayer, "qetl_ts")

# Save to PostGIS
writer.postgis(ts_layer, "MyPostGIS", "gis", "qetl", "ladestandere", True)
```

**Key concepts:**

- `worker.Vector.extractByExpression()` - Filters features using SQL-like expressions
- `worker.Vector.addTimestamp()` - Adds a timestamp field to track when data was processed
- `writer.postgis()` - Saves layer to PostGIS database with schema and table names
- Attribute filtering syntax with double quotes for field names

## Datafordeleren WFS with SQL Filter

This example shows how to query with authentication and SQL filtering:

```python
from core import *
from engine import *

reader = Input_Reader
worker = Worker
output = Output_Writer

# Load cadastral parcels from Datafordeleren with SQL filter
layer = reader.wfs("""srsname='EPSG:25832' 
                   typename='mat:Jordstykke_Gaeldende' 
                   url='https://wfs.datafordeler.dk/MATRIKLEN2/MatGaeldendeOgForeloebigWFS/1.0.0/WFS?username=xxx&password=yyy' 
                   version='auto' 
                   sql=SELECT * FROM Jordstykke_Gaeldende WHERE Jordstykke_Gaeldende.ejerlavskode = 21751""")

# Reproject to Web Mercator (EPSG:3857)
reprojected = worker.Vector.reproject(layer, 3857)

# Save to GeoPackage
output.geopackage(reprojected, 'ejerlav', 'c:/temp/output.gpkg', True)
```

**Key concepts:**

- WFS with authentication parameters (username/password in URL)
- SQL filtering directly in the WFS request to retrieve specific features
- `worker.Vector.reproject()` - Changes the coordinate reference system
- Multi-line string formatting for better readability

## WFS with Clip Analysis

This example demonstrates spatial analysis with clipping operations:

```python
from core import *
from engine import *

reader = Input_Reader
worker = Worker
output = Output_Writer
constructor = Constructor

# Load protected areas from WFS service
inputlayer = reader.wfs("srsname='EPSG:25832' typename='dai:fredede_omr' url='https://arealeditering-dist-geo.miljoeportal.dk/geoserver/wfs' version='auto'")

# Create a layer from WKT defining the area of interest
area = constructor.layerFromWKT('Polygon', ['POLYGON((706099.6158084492 6185578.989176224,720025.2350720493 6185578.989176224,720025.2350720493 6197017.890714182,706099.6158084492 6197017.890714182,706099.6158084492 6185578.989176224))'], 25832)

# Perform clip analysis with input layer and area
selected_area = worker.Vector.clip(inputlayer, area)

# Save result to GeoPackage
output.geopackage(selected_area, 'Fredede_omraader', 'c:/temp/omraade.gpkg', True)
```

**Key concepts:**

- `reader.wfs()` - Loads data from a Web Feature Service
- `constructor.layerFromWKT()` - Creates a layer from Well-Known Text geometry
- `worker.Vector.clip()` - Clips features to a specified area
- `output.geopackage()` - Saves the result to a GeoPackage file

## Load, Fix Geometry, and Extract Area

A more advanced workflow demonstrating geometry validation and spatial operations:

```python
from engine import *
from core import *

# Input WFS
input_reader = Input_Reader
wfslayer = input_reader.wfs('https://geofyn.admin.gc2.io/wfs/geofyn/fynbus/25832?SERVICE=WFS&REQUEST=GetFeature&VERSION=1.1.0&TYPENAME=fynbus:routes_25832_v&SRSNAME=urn:ogc:def:crs:EPSG::25832')

# Work-geometry from WKT
constructor = Constructor
box = constructor.layerFromWKT('Polygon', ['POLYGON((582913.5369507923 6132445.965210357,593841.5534312518 6132445.965210357,593841.5534312518 6145264.641981553,582913.5369507923 6145264.641981553,582913.5369507923 6132445.965210357))'], 25832)

# Input Geometry has errors, fixing them
worker = Worker
wfs_geomfix = worker.Vector.fixGeometry(wfslayer)

# Clipping the WFS with the work-geometry
extractLayer = worker.Vector.clip(wfs_geomfix, box)

# Writing the QGIS layer to a GeoJSON file
output_writer = Output_Writer
output_writer.file(extractLayer, "C:/temp/extractLayer.geojson", "GeoJson")
```

**Key concepts:**

- `worker.Vector.fixGeometry()` - Repairs invalid geometries before processing
- `worker.Vector.clip()` - Clips features to a polygon boundary
- `constructor.layerFromWKT()` - Creates geometry from Well-Known Text
- Important to fix geometries before spatial operations to avoid errors
- Useful for quality assurance in data workflows

## Generic Processing with QGIS Algorithms

This example demonstrates accessing the full QGIS processing toolbox:

```python
from core import *
from engine import *

reader = Input_Reader
worker = Worker
output = Output_Writer

# Input WFS
input_reader = Input_Reader
wfslayer = input_reader.wfs('https://geofyn.admin.gc2.io/wfs/geofyn/fynbus/25832?SERVICE=WFS&REQUEST=GetFeature&VERSION=1.1.0&TYPENAME=fynbus:routes_25832_v&SRSNAME=urn:ogc:def:crs:EPSG::25832')

# Define parameters for native:buffer algorithm
params = {
    'INPUT': wfslayer,
    'DISTANCE': 10,
    'SEGMENTS': 5,
    'END_CAP_STYLE': 0,
    'JOIN_STYLE': 0,
    'MITER_LIMIT': 2,
    'DISSOLVE': False,
    'SEPARATE_DISJOINT': False,
    'OUTPUT': 'TEMPORARY_OUTPUT'
}

# Run the buffer algorithm
buffer = worker.Generic.ProcessingRunner("native:buffer", params)
```

**Key concepts:**

- `worker.Generic.ProcessingRunner()` - Executes any QGIS processing algorithm
- Algorithm parameters are passed as a dictionary
- Access to the full QGIS processing toolbox (500+ algorithms)
- Algorithm names follow the format "provider:algorithm" (e.g., "native:buffer", "gdal:rasterize")
- Use 'TEMPORARY_OUTPUT' for intermediate layers
- Useful for operations not directly available in Q-ETL's simplified interface

## Batch Processing from Plandata WFS to PostGIS

This example demonstrates batch processing with database management:

```python
from core import *
from engine import *

reader = Input_Reader
worker = Worker
output = Output_Writer

# List of table names to process
input_tabeller = ['theme_pdk_zonekort_v', 
                  'theme_pdk_lokalplan_vedtaget_v', 
                  'theme-lpd-sommerhusomr', 
                  'theme_pdk_kommuneplanramme_vedtaget_v', 
                  'theme_pdk_skovrejsningsomraade_forslag_v']

# Database preparation - drop and recreate schema
worker.Vector.execute_sql('MyPostGIS', 'Postgres', """DROP SCHEMA IF exists plandata CASCADE""", 'gis')
worker.Vector.execute_sql('MyPostGIS', 'Postgres', """CREATE SCHEMA plandata""", 'gis')

# Process each layer one at a time
for table in input_tabeller:
    layer = reader.wfs(f"srsname='EPSG:25832' typename='pdk:{table}' url='https://geoserver.plandata.dk/geoserver/wfs?servicename=wfs' version='auto'")
    output.postgis(layer, 'MyPostGIS', 'gis', 'plandata', table, True)
```

**Key concepts:**

- `worker.Vector.execute_sql()` - Executes SQL commands on the database
- Loop processing for handling multiple datasets efficiently
- `output.postgis()` - Writes vector data to a PostGIS database
- Database schema management (DROP/CREATE)
- Connection references using configuration names ('MyPostGIS')

## Download and Process ZIP with GeoJSON Files

This most advanced example demonstrates a complete automated workflow:

```python
# Q-ETL imports
from core import *
from engine import *

# Python standard library imports
from pathlib import Path
import zipfile

# Define reader, worker and output
reader = Input_Reader
worker = Worker
output = Output_Writer

# Define paths and URL
zip_file_url = 'URL TO ZIP FILE WITH GEOJSON FILES'
local_file_path = Path('c:/temp/geojson_data.zip')
extract_path = Path('c:/temp/geojson_data')

# Download file
download_successful = worker.download_file(zip_file_url, local_file_path)

# Extract ZIP file
try:
    with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print(f'Extraction completed. Files are extracted to: {extract_path}')
except zipfile.BadZipFile:
    print(f'Error: {local_file_path} is not a zip file or it is corrupted')

# Process data in Q-ETL and save to database
# Find all GeoJSON files from extracted ZIP
geoJson_filer = [file for file in Path(extract_path).rglob('*.geojson')]

# Database preparation
worker.Vector.execute_sql('MyPostGIS', 'Postgres', 'CREATE SCHEMA IF NOT EXISTS geojson_zip', 'gis')

# Load and save each dataset to database
for geojson_filepath in geoJson_filer:
    tablename = Path(geojson_filepath).stem
    geojson_file = reader.geojson(geojson_filepath.as_posix())
    output.postgis(geojson_file, 'MyPostGIS', 'div_test', 'geojson_zip', tablename, True)
```

**Key concepts:**

- `worker.download_file()` - Downloads files from URL
- Python's `pathlib.Path` for cross-platform file path handling
- `zipfile` module integration for archive handling
- `Path.rglob()` - Recursively finds all files matching a pattern
- `Path.stem` - Gets filename without extension for table naming
- `reader.geojson()` - Loads GeoJSON files
- Error handling with try/except blocks
- Batch processing of multiple files in a directory structure

## Additional Resources

For more information, see:

- [Basic Tutorial](basic_tutorial.md) - Step-by-step introduction to Q-ETL
- [Inputs](Inputs.md) - Complete guide to all available data input methods
- [Workers](workers.md) - Comprehensive documentation of data processing operations
- [Outputs](outputs.md) - All available output formats and destinations
- [Constructors](constructors.md) - Creating geometries and layers programmatically
