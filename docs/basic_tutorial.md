# Introduction
This tutorial will show you how to create your first job, using QGIS to make most of the configuration of the parameters. 
We expect you to have completed the [Getting started](https://github.com/MFuglsang/Q-ETL/wiki/Getting-started) guide so that you have Q-ETL configured and running.

You are working in a Danish municipality. You want to have a map of electric-car charging stations in your system, but you don't have the data in your local database. These come from a WFS service from the geodata-collection GeoFA, where different actors can maintain Geodata.
Therefor you set up a Q-ETL job, to gather the data, do processing, and save them to your database. This job will run nightly, ensuring that data is up to date every morning.

## Input service
The service that we use as input, is from GeoFA, we are looking for charging stations for Electric cars.
The service is:

`https://geofa.geodanmark.dk/ows/fkg/fkg`

We load this as a WFS in QGIS, and examine the layers.
We are looking for the layer 'Ladefaciliteter'

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/geofa.png" width="50%" height="50%"> 
<br/>

We then load the data to QGIS:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/data.png" width="50%" height="50%"> 

We get data for the entire country, but we only want one municipality. That's ok, we will filter that out later...

Now we know everything we need to create our job - it's time to build our Q-ETL job.

# Creating the job
Navigate to the Q-ETL folder. In the root, you will have boilerplate.cmd. We make a copy this file, and call it mastra.cmd (Name by the data source, however it can be called whatever you want). Fill in the paths required.

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/cmd.png" width="100%" height="100%">

Next, we go to the python folder. Here we will find the boilerplate.py. In the same way, we make a copy of it, named masta.py

```python
from core import *
from engine import *

## Code goes here...

```

This is the file we are going to start working in right now, the project is ready to go. If you run mastra.cmd, the job will execute, but nothing will happen, since we have no processingin mastra.py
 
## Loading the data in Q-ETL

In other ETL tools, loading WFS data can be complicated. That is not the case in Q-ETL, where QGIS does all the work for us. Since we have loaded the data in QGIS in the start of this guide, we know that QGIS can handle it well, and is able to read the data.

We go to QGIS, and look at the properties of our layer:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/wfs_properties.png" width="100%" height="100%">

Here we can see the Source information of our WFS layer under 'Information' - we copy this line out of QGIS.
This is all we need. However, there is a few elements we don't need, so we trim them away, going from :

`pagingEnabled='default' preferCoordinatesForWfsT11='false' restrictToRequestBBOX='1' srsname='EPSG:25832' typename='fkg:fkg.t_5607_ladefacilitet' url='https://geofa.geodanmark.dk/ows/fkg/fkg'`

To:

`srsname='EPSG:25832' typename='fkg:fkg.t_5607_ladefacilitet' url='https://geofa.geodanmark.dk/ows/fkg/fkg'`

Our first setup step will be to put this in a WFS reader.

We first load the three main classes that we need - reader, worker, and writer (See the documentation at XXX for descriptions)
The class instances can be named whatever you like, but here, we will go with simple names.

```python
from core import *
from engine import *

reader = Input_Reader
worker = Worker
writer = Output_Writer
```

Now, we can access our class instances. If we type 'reader' and add a dot, we are shown all the methods in the reader class.
We need the WFS reader. You get what inputs the method needs, and a description directly in your IDE.

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/wfs_reader.png" width="100%" height="100%">

We create a python variable, let's call it wfs_layer. We set the variable to the wfs-reader output:

```python
wfslayer = reader.wfs("srsname='EPSG:25832' typename='fkg:fkg.t_5800_fac_pkt' url= 'httpS://geofa.geodanmark.dk/ows/fkg/fkg'")
```
Now, the reader is configured, and we can test it out. We go to a terminal, and run the geofa.cmd file:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/terminal.png" width="100%" height="100%">

When we hit enter, the job runs. We get detailed logs in the window:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/cmd_log.png" width="100%" height="100%">

As we can see, the job runs. it reads our WFS service, and then stops - there is nothing more to do in the job. But now, we have configured the WFS access to data, and can start processing it 

## Processing the data
Now we have successfully loaded the data, now we can transform them. In this case, we need to filter the data, so that we only get our municipality.
This is done by using workers.

In this case, we need to filter by an expression, which is a tool from the QGIS processing toolbar. 
Lets make it work there first, the same way we did with our WFS.
Open the processing toolbox, and search for 'expression' - then we find our tool:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/extract_dialog.png" width="50%" height="50%">

We open the tool dialog, and fill it out. We need municipality 330, so we build an expression with that value:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/extract_dialog2.png" width="75%" height="75%">

To make sure our expression is correct, we can run the tool in QGIS, and examine the result. If everything looks ok, we can use the values from the QGIS tool in Q-ETL. In the bottom corner of the tool, is an 'Advanced' button. Click that, and we find the 'Copy as python command':

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/save_python.png" width="50%" height="50%">

If we click that, the python code for running this tool with the values from the GUI is exported.
We paste that into a text editor to see what we get:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/python_code.png" width="100%" height="100%">

In the expression parameter, we get the exact python-formatted expression that we need:

`'EXPRESSION':' "beliggenhedskommune" = 330'`

That we can use to configure our worker in Q-ETL.
We use a method from the workers class - in this case the ExtractByExpression method (Notice the same naming as in QGIS)

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/extract_worker.png" width="100%" height="100%">

We then take our expression, and configure the tool. The input-layer is the output from the WFS reader.We add the output layer to a new variable:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/extract_worker_configured.png" width="100%" height="100%">

Now, we can run the geofa.cmd again, and see what happens in the logfile:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/extract_log.png" width="100%" height="100%">

We can now see, that the extract by expression tool is running, and producing output.
Now, we will just add a timestamp to the data, so that we know when we have acquired them.
This is done with the addTimestamp worker.
```python
ts_layer= worker.Vector.addTimestamp(filteredLayer, "qetl_ts")
```


<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/timestamp_log.png" width="100%" height="100%">

That means that we have processed the data, and now we can write them to our database.


## Writing the data
In this tutorial, we are going to write the data to a Postgres/PostGIS database.
In order to not have database-credentials and users in directly in the jobs, these are maintained in the configuration.json file. 

### The target database
In the settings.json, we have the database connection:

```json
"MyPostGIS" : {
    "host" : "localhost",
    "port" : "5432",
    "databasename":"gis",
    "user" : "xxx",
    "password": "xxx"
},
```

The name of the configuration is what we are going to use to write to the database.
Now, in order to write to the database, we call the instance of our 'Output_Writer' class.
Here we select the postgis writer, and fill in the parameters:

```python
writer.postgis(ts_layer, "MyPostGIS", "gis", "qetl", "ladestandere", True)
```

When that is done, our script is ready. The full code is now:

```python
from core import *
from engine import *

reader = Input_Reader
worker = Worker
writer = Output_Writer

wfslayer = reader.wfs("srsname='EPSG:25832' typename='fkg:fkg.t_5800_fac_pkt' url= 'httpS://geofa.geodanmark.dk/ows/fkg/fkg'")

filteredLayer = worker.Vector.extractByExpression(wfslayer, '"beliggenhedskommune" =330')

ts_layer= worker.Vector.addTimestamp(filteredLayer, "qetl_ts")

writer.postgis(ts_layer, "MyPostGIS", "gis", "qetl", "ladestandere", True)
```

We can now again run the geofa cmd, and examine the output:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/writer_log.png" width="100%" height="100%">

# Examine the output.

## The data
If we open the data in our database, we can examine the data. With a slight modification of the select script, we can see the data and out timestamp column:

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/database_table.png" width="100%" height="100%">

That looks good, how about in QGIS ?

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/result_data.png" width="75%" height="75%">

## The logs

In the final step, let's just examine the log file created.

<img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/tutorial/final_log.png" width="100%" height="100%">

We can see, that all our operations went well, the data was loaded, filtered and written to the database... Perfect!

# What's next

The job is ready, at can be scheduled using windows task scheduler. Select a time where you want the job to run, and point the scheduler to geofa.cmd. 
Then data will automatically flow into your database at night, while you have sweet dreams about all the ETL money you are saving by using Q-ETL :-)