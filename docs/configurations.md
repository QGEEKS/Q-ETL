# Configurations

## Configuring the settings.json file

The settings json has required elements, and optional elements.

```json
{
    "Qgs_PrefixPath" : "",
    "QGIS_ini_Path" : "",
    "QGIS_bin_folder": "",
    "logdir" : "",
    "TempFolder" : "",
    "DatabaseConnections": {
        "MyPostGIS" : {
            "host" : "",
            "port" : "",
            "databasename":"",
            "user" : "",
            "password": ""
        },
        "MyMSSQL" : {
            "host" : "",
            "port" : "",
            "databasename":"",
            "user" : "",
            "password": ""
        }

    },
    "emailConfiguration" : {
        "emailOnError" : "False",
        "smtp_server" : "",
        "smtp_port" : "",
        "smtp_username" : "",
        "smtp_password" : "",
        "message_from" : "",
        "message_to" : []
    } ,
    "pushoverConfiguration": {
        "pushoverOnError" : "False",
        "pushover_user_key" : "",
        "pushover_app_token" : ""
    }  

}
```
### Qgs_PrefixPath (Required)
The root folder of your QGIS application of our installation
For instance: C:/Program Files/QGIS x.xx.x/apps/qgis

### QGIS_ini_Path (Required)
QGIS_ini_Path is a little more tricky. it is found in the root of your default user-profile in QGIS. To fetch it the easiest way, open QGIS, open the Python prompt and type: print(QSettings().fileName())

### QGIS_bin_folder (Required)
The path to the QGIS bin forlder of you installation.
For instance: C:/Program Files/QGIS x.xx.x/bin

### logdir (Required)
A folder for the generated log files. 

### TempFolder (Required)
A folder for temporary data.

### DatabaseConnections (Optional)
If you need to configure databases, this is donw in this part of settings.json. 
You can create named configurations to multiple databases.

### emailConfiguration (Optional)
Jobs can send email on errors. This is be default dsiabled. If you have an SMTP server, you can configure Q-ETL to uses it, sending email notifications if scheduled jobs fail.

### pushoverConfiguration (Optional)
Jobs can send error messages to Android and Iphone devices using the Pushover service

## Setting .env for Datafordeleren.dk
In order to use datafordeleren, you need to configure your user and password for your tjenestebruger.
Make a copy of the root file '.evv_template, and rename it to '.env'
Edit the file and fill ind the username and password for datafordeleren, and you can use the integrations to datafordeleren.

```
DATAFORDELER_TJENESTEBRUGER=
DATAFORDELER_PASSWORD=
# Hosts, not to be edited
DATAFORDELER_DOWNLOAD_HOST=https://api.datafordeler.dk/FileDownloads/GetFile?

```

## Setting up the log server

To enable remote access to logs, it is possible to configure a logfile server from Q-ETL.
This makes it possible to access job logs from remote locations, to verify that jobs have run and completed without logging onto the server.

### Configuration
The configuration of the logserver is in the server folder\
<img src="https://github.com/QGEEKS/Q-ETL/blob/ressources/images/server/server.png" > \
<br/><br/>
To set up the server, make a compy of the template file, and call it server.cmd\

<img src="https://github.com/QGEEKS/Q-ETL/blob/ressources/images/server/server_template.png" > 
<br/><br/>
It requires two elements: The path to python.exe - located in the QGIS install folder and the full path to the server.py file.\
When this file is created, you are ready to install the server. 
<br/><br/>
Navigate to the server\bin folder:
<br/><br/>
<img src="https://github.com/QGEEKS/Q-ETL/blob/ressources/images/server/server_bin.png" > 
<br/><br/>
Run install_service.cmd to install the windows service:
<br/><br/>
<img src="https://github.com/QGEEKS/Q-ETL/blob/ressources/images/server/install.png" > 
<br/><br/>
The system will prompt for elevation, the install needs administrative privileges to run. If all goes well, the message will tell you that the service is installed. Now you can open Windows services, to locate the new service:
 <br/><br/>
<img src="https://github.com/QGEEKS/Q-ETL/blob/ressources/images/server/service.png" > 
 <br/><br/>
The first time, the service must be started manually. Set startup to automatic, and it will start up with Windows after restart. 
It is preferred to have a service account for running the service. It must have 'log on as service' privileges. 
<br/><br/>
When the server is running, the server can be accessed on localhost:3000. There you will see the contents of the log directory. If you click on a log file, it will be displayed for you.
<br/><br/>
<img src="https://github.com/QGEEKS/Q-ETL/blob/ressources/images/server/url.png" > 
<br/><br/>
<img src="https://github.com/QGEEKS/Q-ETL/blob/ressources/images/server/logfile.png" > 

### Troubleshooting
If you have problems starting the service, the configuration is wrong.
It is a cmd file that runs the service - if you have spaces in your paths, put "" around the elements. 
