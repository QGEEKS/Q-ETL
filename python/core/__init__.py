import sys, os
from qgis.core import QgsApplication, Qgis
from core.logger import *
from core.misc import get_config, createJobRun
from core.db import *
import atexit
import tracemalloc
import random


tracemalloc.start()
now = datetime.now()

#settings = _local_configuration.loadConfig()
settings = get_config()
logger = initialize_logger(settings)
start_logfile(now)

#Creating job run 
jobrun = random.getrandbits(36)
createJobRun(jobrun)

#Internal DB startup
initdb()

##Write job to db
startjob(jobrun, argv[0], now, get_logfile())

from core.misc import validateEnvironment, describeEngine, get_postgres_connections, get_bin_folder, script_finished
settings['bin_path'] = get_bin_folder(settings)
validateEnvironment(settings)

settings['Postgres_Ponnections'] = get_postgres_connections(settings)

QgsApplication.setPrefixPath(settings["Qgs_PrefixPath"], True)
qgs = QgsApplication([], False)
qgs.initQgis()

## Loading the Processing plugin...
try:
    sys.path.append(settings["QGIS_Plugin_Path"])
    import processing
    from processing.core.Processing import Processing

    from qgis.analysis import QgsNativeAlgorithms
    Processing.initialize()
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    from processing.script import ScriptUtils
    from processing.modeler.ModelerUtils import ModelerUtils
    logger.info('QGIS ressources loaded sucesfully')

except Exception as e :
    logger.error('Error loading QGIS ressources')
    logger.error(e)
    logger.critical('Program terminated')
    sys.exit()

describeEngine(ScriptUtils.scriptsFolders(), ModelerUtils.modelsFolders(), QgsApplication.processingRegistry().providerById("script").algorithms(), Qgis.QGIS_VERSION)


atexit.register(script_finished)
