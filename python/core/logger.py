import logging
from datetime import datetime
import os
from sys import argv
import sys, traceback
import coloredlogs

logfile = None

def initialize_logger(settings):
    logdir = settings['logdir']
    now = datetime.now()
    filename = argv[0].split('\\')[-1].split('.')[0]
    global logfile
    logfile = logdir + '/' +  filename + '_' + now.strftime("%d%m%Y_%H_%M") + '.txt'
    global logger
    logger = logging.getLogger('Q-ETL')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)

    # Updated log format to exclude thread ID
    logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s : %(message)s ')
    fh.setFormatter(logFormatter)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.DEBUG)
    logger.addHandler(consoleHandler)
    logger.addHandler(fh)

    # Integrate coloredlogs with updated format and custom field styles
    field_styles = {
        'asctime': {'color': 'green'},
        'levelname': {'color': 'yellow', 'bold': True},
        'funcName': {'color': 'blue'},
        'thread': {'color': 'magenta'},
    }
    coloredlogs.install(level='DEBUG', logger=logger, fmt='%(asctime)s - %(levelname)s - %(funcName)s : %(message)s ', field_styles=field_styles)

    sys.excepthook = exc_handler

    return logger
    
def exc_handler(exctype, value, tb):
    logger.exception(''.join(traceback.format_exception(exctype, value, tb)))

def start_logfile(now):

    logger.info('##################################################')
    logger.info('Q-ETL JOB LOG')
    logger.info('JOB: ' + argv[0])
    logger.info('STARTTIME: ' + now.strftime("%d/%m/%Y, %H:%M"))
    logger.info('##################################################')
    logger.info('')



def get_logger():
    return logger

def get_logfile():
    return logfile


