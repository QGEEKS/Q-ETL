This guide will show you how to set up and configure QGIS ETL to run jobs.
At the end, the system will be configured to run a simple job, performing an ETL task - loading, manipulating, and writing data.

# Setup

## Step 1 - Unzip 

Fetch latest relase [here](https://github.com/QGEEKS/Q-ETL/releases). This will download a zip file containing the application. Unzip this archive. 

This example will unzip the application in **C:/Apps**

When it is unzipped, you will have a folder like this: 

TODO: ADD FOLDER STRUCTURE EXAMPLE

## Step 2 - settings.json

The first step we need to do is to go through the process of creating the settings.json file in the root.
Make a copy of the file _settings\_template.json_, and rename it to _settings.json_. 

TODO: ADD EXPLANATION OF SETTINGS.JSON

## Step 3 - The python project file.

Navigate to the python folder and locate the _boilerplate.py_ file. Make a copy of this file and rename it to _MyProject.py_.

Open and examine the content of the file - there is not much in it yet:

```python
from core import *
from engine import *

## Code goes here
```

Let's keep the file open, we will use it in a short while, we just have one more file to modify before we can start to code the ETL job.

## Step 4 - The project cmd file.

Go to the root folder of the application, and locate the file _boilerplate.cmd_. Make a copy of this file, and rename it to _MyProject.cmd_.

Open this new .cmd file:

```cmd
<PATH-TO>\python-qgis.bat <FULL-PATH-TO-PYTHON-SCRIPT>
```

You need to insert the full path to the _python-qgis.bat_ and the full path to _MyProject.py_ file we created in the previous step. Depending on how you have made your QGIS installation, the path to python-qgis.bat is different. In a OSGEO4W installation, it is in the OSGEO4W\bin folder. In a standalone QGIS installation, it is in QGIS\bin. The path to the MyProject.py depends on where you have placed your project.

An example _cmd_ file could look like this:
```cmd
C:\App\OSGeo4W\bin\python-qgis.bat C:\App\Q-ETL\python\MyProject.py
```

Now, the project is configured to run the project file MyProject.py - and we will now turn our focus on developing our ETL model

# Development

For this tutorial, we will load data from a WFS service, reproject it, and store it on disk in a Geopackage.
The WFS service that we are going to use, contains bus routes and stops - and we are interested in getting the bus stops out.
The service comes in EPSG:25832.

The service:
```
https://geofyn.admin.gc2.io/wfs/geofyn/fynbus/25832?
```

The typename we are looking for is _Fynbus:stops_

For it to work in our code, we need to turn it into a QGIS URI string. the simplest way to do that is to let QGIS load the layer for you and extract the information.
When the layer is loaded, go to the properties of the layer, and select 'Information'- here the URI string can be copied:

TODO: ADD SCREENSHOT FROM QGIS

The string we are going to use as URI is:

```
"srsname='EPSG:25832' typename='fynbus:stops' url='https://geofyn.admin.gc2.io/wfs/geofyn/fynbus/25832'"
``` 

Now, it is time to go to our project and start to code the operations. 


We can try and run the code as it is, verify that all configurations are correct, and see how that program executes.
Go to the root folder of your project, and run the MyProject.cmd file. This will open a terminal window, which reports the execution progress.
When it finishes, go to the folder that was specified as LogPath in the config, and locate the new log file from this run. It has the project name and timestamp in the filename.

This is the basic format of the log file generated on each run. It validates the configuration, examines the environment and operating system, and finally, it starts to execute the script - which in this case is empty.
Now we have confirmed that the boilerplates and configuration of our project are valid, and we can build the code to manage the data.

The process has three steps: Load, reproject and write.

1. Load data
The code is structured in classes - the three main ones are going to be used her. First we create a reader, by invoking the Input_Reader class:
Then, we construct our input layer, by calling the 'wfs' method on our reader. By calling this method, we are going to give it just one parameter - the URI that we constructed in QGIS. we assign the output layer to a variable, in this case we call it wfslayer, for easy readability of this example. 
```
reader = Input_Reader
wfslayer = reader.wfs("srsname='EPSG:25832' typename='fynbus:stops' url='https://geofyn.admin.gc2.io/wfs/geofyn/fynbus/25832'")
```

2. Next, we must do the reprojection of the data from EPSG:25832 to EPSG:4326. for this, we will create a worker, which will be able to perform operations on layers. This is based on the Worker class. QGIS knows the ESPSG code of the layer, so all we need to specify is the target code (we omit the 'EPSG:', so it is only an input integer here...)
```
worker = Worker
reprojectedlayer = worker.Vector.reproject(wfslayer, 4326)
```

3. Finally, we will write our reprojected layer to a Geopackage file. For this, we will use our Output_writer class.
On the writer, we will call the 'geopackage' method, which takes four arguments: Layer to write, layername in the geopackage, the geopackage file to write to, and an option to overwrite the Geopackage.
```
writer = Output_Writer
writer.geopackage(reprojectedlayer,'Busstops','c:/temp/fynbus.gpkg',True)
```

Now, the code looks like this:

TODO: INSERT EXAMPLE

Now, let's call our MyProject.cmd file, and wait for it to finish. It won't take long, the QGIS engine is super fast.
When the job finishes, let go and inspect the log file that is created. The start parts are the same as all other runs, but the script part at the bottom is now different:

As the log states, it reads a total of 4706 features from the source with the wfs reader. it channels these features through the reprojector worker - also returning the same 4706 features (which indicates no geometry problems). Finally, it writes the features to the Geopackage, and the job ends with success ❤️ 

This concludes this quickstart tutorial. The next step is to browse the API documentation to find out which methods are available in _Input\_reader_, _Worker_, and _Output\_Writer_ classes. 

On behalf of the QGIS ETL team, Enjoy 😃 