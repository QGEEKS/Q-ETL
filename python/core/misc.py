from core.logger import *
from core.db import *
import sys
import subprocess
import platform,socket,re,uuid,json
import pip._internal as pip
from sys import argv
import os.path as path
import json
from PyQt5.QtCore import QSettings
import smtplib
from email.mime.text import MIMEText
from qgis.core import QgsVectorFileWriter, QgsProject
from random import randrange
import tracemalloc


def install_dependencies():
    logfile = get_logfile()
    try:
        import psutil
    except:
        logger.info(f'Missing dependency found: psutil')
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psutil'])
            import psutil
        except:
            logger.info(f'Unable to install dependencies - run the editor in admin mode on first run')
            script_failed()
        logger.info(f'Dependency: psutil - installed')

    try:
        import geopandas
    except:
        logger.info(f'Missing dependency found: geopandas')
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'geopandas'])
            import geopandas
        except:
            logger.info(f'Unable to install dependencies - run the editor in admin mode on first run')
            script_failed()
        logger.info(f'Dependency: geopandas - installed')

def get_version():
    with open('version.json') as f:
        data = json.load(f)
    return  data['version']


def createJobRun(id):
    config = get_config()
    logfile = get_logfile()
    jobrun_path = config['TempFolder'] + 'job_run.json'
    try:
        os.remove(jobrun_path)
    except OSError:
        pass

    element = {
        'id' : str(id),
        'logfile' : logfile
    }

    with open(jobrun_path, 'w') as f:
        json.dump(element, f)

def remove_jobrun():
    config = get_config()
    jobrun_path = config['TempFolder'] + 'job_run.json'
    try:
        os.remove(jobrun_path)
    except OSError:
        pass

def read_jobrun():
    config = get_config()
    jobrun_path = config['TempFolder'] + 'job_run.json'
    with open(jobrun_path) as f:
        data = json.load(f)
    return data


def layerHasFeatures(layer: str):
    if layer.featureCount() == 0:
        return False
    else:
        return True

def create_tempfile(layer: str, toolname: str):
    logger = get_logger()
    config = get_config()
    try:
        tmp_path = f'{config["TempFolder"]}QETL_{toolname}_{str(randrange(1000))}.fgb'
        logger.info(f'Creating Temporary file {tmp_path}')
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = 'FlatGeobuf'
        QgsVectorFileWriter.writeAsVectorFormatV3(layer, tmp_path, QgsProject.instance().transformContext(), options)
        logger.info('Temporary file created')
        return tmp_path
    except Exception as error:
        logger.error("An error occured creating temporary file")
        logger.error(f'{type(error).__name__}  –  {str(error)}')
        logger.critical("Program terminated")
        script_failed()

def delete_tempfile(tmp_path):
        logger = get_logger()
        try:
            os.remove(tmp_path)
            logger.info(f'Temporary file {tmp_path} deleted')
        except:
            logger.info('Could not delete temporary layer - manual cleanup is required')

def validateEnvironment(settings):
    
    logger = get_logger()
    logger.info('Validating Environment and settings')
    ## validating QGIS ressources
    try:
        isExist = os.path.exists(settings['Qgs_PrefixPath'])
        if not isExist:
            
            logger.error('Qgs_PrefixPath not found')
            logger.critical('Program terminated')
            script_failed()
        else:
            logger.info('Qgs_PrefixPath found')
    except:
        logger.info('Qgs_PrefixPath not configured')
        script_failed()

    try:
        isExist = os.path.exists(settings['QGIS_bin_folder'])
        if not isExist:
            
            logger.error('QGIS_Bin_Folder not found')
            logger.critical('Program terminated')
            script_failed()
        else:
            logger.info('QGIS_Bin_Folder found')
    except : 
        logger.info('QGIS_Bin_Folder Not configured')
        script_failed()

    try:
        isExist = os.path.exists(settings['QGIS_ini_Path'])
        if not isExist:
            
            logger.error('QGIS_ini_Path not found')
            logger.critical('Program terminated')
            script_failed()
        else:
            logger.info('QGIS_ini_Path found')
    except : 
        logger.info('QGIS_ini_Path Not configured')
        script_failed()

    ## Locating the logdir
    
    try:
        isExist = os.path.exists(settings['logdir'])
        if not isExist:
            logger.error('Logdir does not exist')
            logger.critical('Program terminated')
            script_failed()
        else:
            logger.info(f'Logdir is {settings["logdir"]}')

        if settings['logdir'][-1] != '/':
            settings['logdir'] = settings['logdir'] + '/'
    except:
        logger.info('Logdir not configured')
        script_failed()

    ## Locating the temp folder
    try:
        isExist = os.path.exists(settings['TempFolder'])
        if not isExist:
            logger.error('TempFolder does not exist')
            logger.critical('Program terminated')
            script_failed()
        else:
            logger.info(f'TempFolder is {settings["TempFolder"]}')
        if settings['TempFolder'][-1] != '/':
            settings['TempFolder'] = settings['TempFolder'] + '/'
    except: 
        logger.info('TempFolder not configured')
        script_failed()


    logger.info('')  
    logger.info('Environement and settings OK !')     

def describeEngine(scriptfolder, algorithms, version, qetl_version):
    logger = get_logger()
    qgis_supported = get_qgis_support()

    try:
        supported = qgis_supported[version]
    except:
        supported = 'Not tested'
    try:
        import psutil
    except ImportError:
        pip.main(['install', 'psutil'])
        import psutil

    info={}
    info['platform']=platform.system()
    info['platform-release']=platform.release()
    info['platform-version']=platform.version()
    info['architecture']=platform.machine()
    info['hostname']=socket.gethostname()
    info['ip-address']=socket.gethostbyname(socket.gethostname())
    info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
    info['processor']=platform.processor()
    try:
        info['ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        info['cores'] = psutil.cpu_count()
    except:
        info['ram'] ='Not available'

    logger.info("")
    logger.info("##################################################")
    logger.info("Initializing engine:                              ")
    logger.info("Platform: " + info['platform'] + " " + info['platform-release'] + " ")
    logger.info("Platform version: " + info['platform-version'] + " ")
    logger.info("Architecture: " + info['architecture'] + " ")
    logger.info("Processor: " + info['processor'] +  " ")
    logger.info("Number of cores : " + str(info['cores']) + " ")
    logger.info("Available memory: " + info['ram'] + " ")
    logger.info("Memory-profiling : Active ")
    logger.info("")
    logger.info("Q-ETL version: " + str(qetl_version) + "                ")
    logger.info("QGIS version: " + str(version) + "                ")
    logger.info("Q-ETL / QGIS status: " + str(supported) + "                ")
    logger.info("Script folder: " + str(scriptfolder) + "")
    algs = []
    for s in algorithms:
        algs.append(s.displayName()) 
    logger.info("Available custom Scripts : " + str(algs) + "")
    logger.info("##################################################")
    logger.info("Q-ETL engine ready")
    logger.info("")
    logger.info("----- Starting Script -----")


def get_config():
    settings_file =  path.abspath(path.join(argv[0] ,"../..")) + '\\settings.json'

    with open(settings_file, 'r') as file:
        settings = json.load(file)

        ##Setting the plugin path based on Qgs_PrefixPath 
        settings['QGIS_Plugin_Path'] = settings['Qgs_PrefixPath'] + '/python/plugins'

        if not os.path.exists(settings['logdir']):
            settings['logdir'] = path.abspath(path.join(argv[0] ,"../..")) + '/logs'

    return settings

def get_qgis_support():
    inputfile =  path.abspath(path.join(argv[0] ,"../..")) + '\\qgis_versions.json'
    with open(inputfile, 'r') as file:
        qgis_support = json.load(file)
    return qgis_support

def get_postgres_connections(settings):
    ini = QSettings(settings['QGIS_ini_Path'], QSettings.IniFormat)
    connections = []

    keys = ini.allKeys()
    for elm in keys:
        if 'PostgreSQL' in elm:
            if 'port' in elm :
                            
                connection = elm.split('PostgreSQL/connections/')[1].split('/')[0]
                connections.append(connection)

    return connections

def get_bin_folder(settings):
    logger = get_logger()
    if 'OSGeo4W' in settings['Qgs_PrefixPath']:
        logger.info("QGIS installed in OSGeo4W bundle")
        bin = path.abspath(path.join(settings['Qgs_PrefixPath'] ,"../..")) + '\\bin\\'

    else:
        logger.info("QGIS installed standalone")
        bin = settings['Qgs_PrefixPath'] + '\\bin\\'

    return bin

def script_finished():
    logger = get_logger()
    now = datetime.now()
    current, peak = tracemalloc.get_traced_memory()
    jobrun = read_jobrun()
    update_job(jobrun['id'], 'Finished', now)
    logger.info('')
    logger.info('')
    logger.info('##################################################')
    logger.info('JOB: ' + argv[0] + ' FINISHED')
    logger.info('ENDTIME: ' + now.strftime("%d/%m/%Y, %H:%M"))
    logger.info(f'Peak memory usage: {round((peak / 10**7), 2)} GB')
    logger.info('##################################################')

    tracemalloc.stop()

def script_failed():
    logger = get_logger()
    now = datetime.now()
    config = get_config()
    jobrun = read_jobrun()
    update_job(jobrun['id'], 'Failed', now)

    email = bool(config["emailConfiguration"]["emailOnError"])

    if email == True:
        try:
            logger.info('')

            smtp_server = config["emailConfiguration"]["smtp_server"]
            smtp_port = config["emailConfiguration"]["smtp_port"]
            smtp_username = config["emailConfiguration"]["smtp_username"]
            smtp_password = config["emailConfiguration"]["smtp_password"]
            messageFrom = config["emailConfiguration"]["message_from"]
            messageTo = ', '.join(config["emailConfiguration"]["message_to"])

            message = MIMEText(f'The Q-ETL job {argv[0]} has failed. Timestamp: {now}')
            message['Subject'] = 'Q-ETL job FAILED'
            message['From'] = messageFrom
            message['To'] = messageTo

            # Establish a connection to the SMTP server
            if len(smtp_port) > 0:
                smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
                smtp_connection.starttls()

                # # Log in to the SMTP server
                smtp_connection.login(smtp_username, smtp_password)
            else:
                smtp_connection = smtplib.SMTP(smtp_server)

            # Send the email
            smtp_connection.send_message(message)

            # Close the SMTP connection
            smtp_connection.quit()
            logger.info(f'Error Email sent to {message["To"]} with subject {message["Subject"]}' )

        except:
            logger.info(f'An error occured sending error Email to {message["To"]} ' )


    logger.info('')
    logger.info('##################################################')
    logger.info('JOB: ' + argv[0] + ' FAILED')
    logger.info('ENDTIME: ' + now.strftime("%d/%m/%Y, %H:%M"))
    logger.info('##################################################')
    sys.exit()
    



