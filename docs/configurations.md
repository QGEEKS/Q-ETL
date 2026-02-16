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

