from core.logger import *
from core.misc import get_config
import sys
import shutil
from core.misc import get_config, create_tempfile, delete_tempfile, kommunekodeToLokalId
from qgis.analysis import QgsNativeAlgorithms
from qgis.core import QgsCoordinateReferenceSystem, QgsVectorLayer, QgsVectorFileWriter, QgsProject, QgsFeatureRequest, QgsProcessingContext, QgsField, QgsFeature, QgsGeometry
from PyQt5.QtCore import QVariant
from qgis import processing
from random import randrange
import geopandas as gpd
from core.misc import script_failed
import time
import os
from dotenv import load_dotenv, find_dotenv
import re
import requests
import zipfile
import ijson
from typing import Iterator
from datetime import date
from pathlib import Path




class Integrations:
    logger = get_logger() 
    load_dotenv(find_dotenv())
    
    class Datafordeler:


                             

        def getDarAdresser(kommunekoder: list):
            dagilokailid = kommunekodeToLokalId(kommunekoder)
            config = get_config()
            logger.info(f'Getting DAR get_dar_adresse from Datafordeler.dk for municipalities {kommunekoder}')
            logger.info(f'Using Datafordeler tjenestebruger {os.environ.get("DATAFORDELER_TJENESTEBRUGER")}')
            ## Preparing adressepunkter first
            try:
                logger.info(f'Step 1: Getting adressepunkter')            
                adressepunkt_file = f'{config["TempFolder"]}/df_temp/DAR_V1_Adressepunkt_TotalDownload_json_Current_169.json'
                if os.path.exists(adressepunkt_file):
                    path = Path(adressepunkt_file)
                    timestamp = date.fromtimestamp(path.stat().st_mtime)
                    if date.today() == timestamp:
                        pass
                        logger.info(f'Skipping download, using existing copy of Adressepunkt with thimestamp {timestamp}')
                    else:
                        os.remove(adressepunkt_file)
                        logger.info(f'Downloading {"https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adressepunkt_TotalDownload_json_Current_169.zip"}')
                        url = f'https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adressepunkt_TotalDownload_json_Current_169.zip&username={os.environ.get("DATAFORDELER_TJENESTEBRUGER")}&password={os.environ.get("DATAFORDELER_PASSWORD")}'
                        tmpfile = f'{config["TempFolder"]}QETL_dar_adressepunkt_{str(randrange(1000))}.zip'
                        with requests.get(url, stream=True) as response:
                            response.raise_for_status()
                            with open(tmpfile, 'wb') as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)
                        logger.info(f'Step 1: Preparing adressepunkter')
                        adressepunkter = {}

                        if not os.path.exists(f'{config["TempFolder"]}/df_temp'):
                            os.makedirs(f'{config["TempFolder"]}/df_temp')

                        with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                            zip_ref.extractall(f'{config["TempFolder"]}/df_temp')
                        os.remove(tmpfile)
                else :
                    logger.info(f'Downloading {"https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adressepunkt_TotalDownload_json_Current_169.zip"}')
                    url = f'https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adressepunkt_TotalDownload_json_Current_169.zip&username={os.environ.get("DATAFORDELER_TJENESTEBRUGER")}&password={os.environ.get("DATAFORDELER_PASSWORD")}'
                    tmpfile = f'{config["TempFolder"]}QETL_dar_adressepunkt_{str(randrange(1000))}.zip'
                    with requests.get(url, stream=True) as response:
                        response.raise_for_status()
                        with open(tmpfile, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)
                    logger.info(f'Step 1: Preparing adressepunkter')
                    adressepunkter = {}

                    if not os.path.exists(f'{config["TempFolder"]}/df_temp'):
                        os.makedirs(f'{config["TempFolder"]}/df_temp')

                    with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                        zip_ref.extractall(f'{config["TempFolder"]}/df_temp')
                    os.remove(tmpfile)

                adressepunkter = {}
                with open(adressepunkt_file, "rb") as f:
                    for elm in ijson.items(f, 'item'):
                        adressepunkter[elm['id_lokalId']]= elm['position']
                
                logger.info(f'Step 1: Got {len(adressepunkter.keys())} adressepunkter')
            except Exception as error:
                logger.error("Error getting Adressepunkter from Dataforsyningen")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()
            
            try:
                logger.info(f'Step 2: Getting DAR Husnummer')
                husnummer_file = f'{config["TempFolder"]}/df_temp/DAR_V1_Husnummer_TotalDownload_json_Current_169.json'
                
                if os.path.exists(husnummer_file):
                    path = Path(husnummer_file)
                    timestamp = date.fromtimestamp(path.stat().st_mtime)
                    if date.today() == timestamp:
                        pass
                        logger.info(f'Skipping download, using existing copy of Husnummer with thimestamp {timestamp}')
                    else:
                        os.remove(husnummer_file)
                        logger.info(f'Downloading {"https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Husnummer_TotalDownload_json_Current_169.zip"}')
                        url = f'https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Husnummer_TotalDownload_json_Current_169.zip&username={os.environ.get("DATAFORDELER_TJENESTEBRUGER")}&password={os.environ.get("DATAFORDELER_PASSWORD")}'
                        tmpfile = f'{config["TempFolder"]}QETL_dar_Husnummer{str(randrange(1000))}.zip'
                        with requests.get(url, stream=True) as response:
                            response.raise_for_status()
                            with open(tmpfile, 'wb') as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)

                        with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                            zip_ref.extractall(f'{config["TempFolder"]}/df_temp')
                        os.remove(tmpfile)
                else:
                    logger.info(f'Downloading {"https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Husnummer_TotalDownload_json_Current_169.zip"}')
                    url = f'https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Husnummer_TotalDownload_json_Current_169.zip&username={os.environ.get("DATAFORDELER_TJENESTEBRUGER")}&password={os.environ.get("DATAFORDELER_PASSWORD")}'
                    tmpfile = f'{config["TempFolder"]}QETL_dar_Husnummer{str(randrange(1000))}.zip'
                    with requests.get(url, stream=True) as response:
                        response.raise_for_status()
                        with open(tmpfile, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)

                    with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                        zip_ref.extractall(f'{config["TempFolder"]}/df_temp')
                    os.remove(tmpfile)


                husnummre = {}
                logger.info(f'Step 2: Processing husnumre')
                with open(husnummer_file, "rb") as f:
                    for elm in ijson.items(f, 'item'):
                        if elm['kommuneinddeling'] in dagilokailid:
                            id = elm['id_lokalId']
                            punkt = elm['adgangspunkt']
                            wkt = adressepunkter[punkt]
                            husnummre[id] = wkt

                logger.info(f'Step 2: Got {len(husnummre)} husnumre after filtering')
            except Exception as error:
                logger.error("Error getting Husnumre from Dataforsyningen")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

            ## STEP 3
            try:
                logger.info(f'Step 3: Getting DAR adresse')
                adresser_file = f'{config["TempFolder"]}/df_temp/DAR_V1_Adresse_TotalDownload_json_Current_169.json'
                
                if os.path.exists(adresser_file):
                    path = Path(adresser_file)
                    timestamp = date.fromtimestamp(path.stat().st_mtime)
                    if date.today() == timestamp:
                        pass
                        logger.info(f'Skipping download, using existing copy of Adresse with thimestamp {timestamp}')
                    else:
                        os.remove(adresser_file)
                        logger.info(f'Downloading {"https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adresse_TotalDownload_json_Current_169.zip"}')
                        url = f'https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adresse_TotalDownload_json_Current_169.zip&username={os.environ.get("DATAFORDELER_TJENESTEBRUGER")}&password={os.environ.get("DATAFORDELER_PASSWORD")}'
                        tmpfile = f'{config["TempFolder"]}QETL_dar_Adresse{str(randrange(1000))}.zip'
                        with requests.get(url, stream=True) as response:
                            response.raise_for_status()
                            with open(tmpfile, 'wb') as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)

                        with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                            zip_ref.extractall(f'{config["TempFolder"]}/df_temp')
                        os.remove(tmpfile)
                else:
                    logger.info(f'Downloading {"https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adresse_TotalDownload_json_Current_169.zip"}')
                    url = f'https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adresse_TotalDownload_json_Current_169.zip&username={os.environ.get("DATAFORDELER_TJENESTEBRUGER")}&password={os.environ.get("DATAFORDELER_PASSWORD")}'
                    tmpfile = f'{config["TempFolder"]}QETL_dar_Adresse{str(randrange(1000))}.zip'
                    with requests.get(url, stream=True) as response:
                        response.raise_for_status()
                        with open(tmpfile, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)

                    with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                        zip_ref.extractall(f'{config["TempFolder"]}/df_temp')
                    os.remove(tmpfile)

                adresser = []
                logger.info(f'Step 3: Processing adresser')
                with open(adresser_file, "rb") as f:
                    for elm in ijson.items(f, 'item'):
                        if elm['husnummer'] in husnummre.keys():

                            elm['geometri'] = husnummre[elm['husnummer']]
                            adresser.append(elm)

                logger.info(f'Step 3: Got {len(adresser)} adresser after filtering')
            except Exception as error:
                logger.error("Error getting adresser from Dataforsyningen")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

            try:
                logger.info(f'Step 3: Building layer')
                keyslist = []
                for key in adresser[0]:
                    keyslist.append(key)

                layer = QgsVectorLayer("Point?crs=EPSG:25832", "adresselayer", "memory")
                provider = layer.dataProvider()
                attributes = []
                for attribute in keyslist:
                    attributes.append(QgsField(attribute, QVariant.String))   
                provider.addAttributes(attributes)
                layer.updateFields() 

                logger.info(f'Step 3: Adding features')   
                for feature in adresser:
                    attribute_list = []
                    for attribute in keyslist:
                        attribute_list.append(feature[attribute])
                    layerfeature = QgsFeature()
                    layerfeature.setAttributes(attribute_list)
                    layerfeature.setGeometry(QgsGeometry.fromWkt(feature['geometri']))
                    provider.addFeature(layerfeature)
            except Exception as error:
                logger.error("Error building adresse layer")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()
            return layer



        def getDarHusnummer(kommunekoder: list):
            config = get_config()
            dagilokailid = kommunekodeToLokalId(kommunekoder)
            logger.info(f'Getting DAR husnummer from Datafordeler.dk for municipalities {kommunekoder}')
            logger.info(f'Using Datafordeler tjenestebruger {os.environ.get("DATAFORDELER_TJENESTEBRUGER")}')
            ## Preparing adressepunkter first
            try:
                logger.info(f'Step 1: Getting adressepunkter')            
                adressepunkt_file = f'{config["TempFolder"]}/df_temp/DAR_V1_Adressepunkt_TotalDownload_json_Current_169.json'
                if os.path.exists(adressepunkt_file):
                    path = Path(adressepunkt_file)
                    timestamp = date.fromtimestamp(path.stat().st_mtime)
                    if date.today() == timestamp:
                        pass
                        logger.info(f'Skipping download, using existing copy of Adressepunkt with thimestamp {timestamp}')
                    else:
                        os.remove(adressepunkt_file)
                        logger.info(f'Downloading {"https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adressepunkt_TotalDownload_json_Current_169.zip"}')
                        url = f'https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adressepunkt_TotalDownload_json_Current_169.zip&username={os.environ.get("DATAFORDELER_TJENESTEBRUGER")}&password={os.environ.get("DATAFORDELER_PASSWORD")}'
                        tmpfile = f'{config["TempFolder"]}QETL_dar_adressepunkt_{str(randrange(1000))}.zip'
                        with requests.get(url, stream=True) as response:
                            response.raise_for_status()
                            with open(tmpfile, 'wb') as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)
                        logger.info(f'Step 1: Preparing adressepunkter')
                        adressepunkter = {}

                        if not os.path.exists(f'{config["TempFolder"]}/df_temp'):
                            os.makedirs(f'{config["TempFolder"]}/df_temp')

                        with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                            zip_ref.extractall(f'{config["TempFolder"]}/df_temp')
                        os.remove(tmpfile)
                else :
                    logger.info(f'Downloading {"https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adressepunkt_TotalDownload_json_Current_169.zip"}')
                    url = f'https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Adressepunkt_TotalDownload_json_Current_169.zip&username={os.environ.get("DATAFORDELER_TJENESTEBRUGER")}&password={os.environ.get("DATAFORDELER_PASSWORD")}'
                    tmpfile = f'{config["TempFolder"]}QETL_dar_adressepunkt_{str(randrange(1000))}.zip'
                    with requests.get(url, stream=True) as response:
                        response.raise_for_status()
                        with open(tmpfile, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)
                    logger.info(f'Step 1: Preparing adressepunkter')
                    adressepunkter = {}

                    if not os.path.exists(f'{config["TempFolder"]}/df_temp'):
                        os.makedirs(f'{config["TempFolder"]}/df_temp')

                    with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                        zip_ref.extractall(f'{config["TempFolder"]}/df_temp')
                    os.remove(tmpfile)

                adressepunkter = {}
                with open(adressepunkt_file, "rb") as f:
                    for elm in ijson.items(f, 'item'):
                        adressepunkter[elm['id_lokalId']]= elm['position']
                
                logger.info(f'Step 1: Got {len(adressepunkter.keys())} adressepunkter')
            except Exception as error:
                logger.error("Error getting Adressepunkter from Dataforsyningen")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()
            try:
                logger.info(f'Step 2: Getting DAR Husnummer')
                husnummer_file = f'{config["TempFolder"]}/df_temp/DAR_V1_Husnummer_TotalDownload_json_Current_169.json'
                
                if os.path.exists(husnummer_file):
                    path = Path(husnummer_file)
                    timestamp = date.fromtimestamp(path.stat().st_mtime)
                    if date.today() == timestamp:
                        pass
                        logger.info(f'Skipping download, using existing copy of Husnummer with thimestamp {timestamp}')
                    else:
                        os.remove(husnummer_file)
                        logger.info(f'Downloading {"https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Husnummer_TotalDownload_json_Current_169.zip"}')
                        url = f'https://api.datafordeler.dk/FileDownloads/GetFile?Filename=DAR_V1_Husnummer_TotalDownload_json_Current_169.zip&username={os.environ.get("DATAFORDELER_TJENESTEBRUGER")}&password={os.environ.get("DATAFORDELER_PASSWORD")}'
                        tmpfile = f'{config["TempFolder"]}QETL_dar_Husnummer{str(randrange(1000))}.zip'
                        with requests.get(url, stream=True) as response:
                            response.raise_for_status()
                            with open(tmpfile, 'wb') as file:
                                for chunk in response.iter_content(chunk_size=8192):
                                    file.write(chunk)

                        with zipfile.ZipFile(tmpfile, 'r') as zip_ref:
                            zip_ref.extractall(f'{config["TempFolder"]}/df_temp')
                        os.remove(tmpfile)

                husnummre = []
                logger.info(f'Step 2: Processing husnumre')
                with open(husnummer_file, "rb") as f:
                    for elm in ijson.items(f, 'item'):
                        if elm['kommuneinddeling'] in dagilokailid:
                            id = elm['id_lokalId']
                            punkt = elm['adgangspunkt']
                            wkt = adressepunkter[punkt]
                            elm['geometri'] = wkt
                            husnummre.append(elm)

                logger.info(f'Step 2: Got {len(husnummre)} husnumre after filtering')
            except Exception as error:
                logger.error("Error getting Husnumre from Dataforsyningen")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()
            try:
                logger.info(f'Step 3: Building layer')
                keyslist = []
                for key in husnummre[0]:
                    keyslist.append(key)

                layer = QgsVectorLayer("Point?crs=EPSG:25832", "husnummerlayer", "memory")
                provider = layer.dataProvider()
                attributes = []
                for attribute in keyslist:
                    attributes.append(QgsField(attribute, QVariant.String))   
                provider.addAttributes(attributes)
                layer.updateFields() 

                logger.info(f'Step 3: Adding features')   
                for feature in husnummre:
                    attribute_list = []
                    for attribute in keyslist:
                        attribute_list.append(feature[attribute])
                    layerfeature = QgsFeature()
                    layerfeature.setAttributes(attribute_list)
                    layerfeature.setGeometry(QgsGeometry.fromWkt(feature['geometri']))
                    provider.addFeature(layerfeature)
            except Exception as error:
                logger.error("Error building husnummer layer")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()
            return layer

                    

        """
        def dagi_selector(dagi_type: str, codes: list):
            
            Retrieve a polygon for one or more DAGI units - kommune or Sogn from Datafordeleren by wfs

            Parameters
            ----------
            dagi_type : str
                Type of DAGI unit, one of (kommune, sogn)    
            
            code : list
                List of codes to retrieve

            Returns
            -------
            QgsVectorLayer
            A QgsVectorLayer object containing DAGI data from Datafordler.dk.

            

            logger.info(f'Getting DAGI geometry from {dagi_type}, codes {codes}')
            logger.info(f'Using Datafordeler user {os.environ.get("DATAFORDELER_TJENESTEBRUGER")}')
            pattern = r'^0\d{3}$'

            for elm in codes:

                invalid = 0
                if not bool(re.match(pattern, elm)):
                    invalid +=1 

            if invalid == 0:
                if dagi_type.lower() not in ('kommune', 'sogn'):
                    logger.error("Unsupported DAGI type {dagi_type}")
                    logger.critical("Program terminated")
                    script_failed()
                else:
                    if dagi_type.lower() == 'kommune':
                        pass
                    elif dagi_type.lower() == 'sogn':
                        pass
                    else:
                        pass
            else:
                logger.error("Non-conform DAGI codes: {invalid}")
                logger.critical("Program terminated")
                script_failed()

             """


    ## ##################################
    ## Geopandas import / export
    ## ##################################

    def to_geopandas_df(layer: str):
        """
        Convert a QGIS layer to a Geopandas dataframe for further processing

        Parameters
        ----------
        layer : str
            The QGIS layer to be converted to dataframe

        Returns
        -------
        Dataframe
            The GeoPandas dataframe from the input layer
        """

        logger.info(f'Creating Geopandas dataframe from layer  {str(layer)}')
        config = get_config()
        try:
            tmp_path = create_tempfile(layer, 'to_dataframe')
            logger.info('Creating dataframe')
            df = gpd.read_file(tmp_path)
            logger.info('Dataframe creation finished')
            delete_tempfile(tmp_path)
            return df

        except Exception as error:
            logger.error("An error occured exporting layer to Pandas dataframe")
            logger.error(f'{type(error).__name__}  –  {str(error)}')
            logger.critical("Program terminated")
            script_failed()

    def from_geopandas_df(dataframe: str):
        """
        Convert a  a Geopandas dataframe ton QGIS layer

        Parameters
        ----------
        dataframe : str
            The dataframe to be converted to QGIS layer

        Returns
        -------
        QgsVectorLayer
            The QGIS layer from the input dataframe
        """

        logger.info(f'Creating layer from Geopandas dataframe ')
        config = get_config()
        try:
            logger.info(f'Creating temporary layer in Temp folder')
            tmp_path = f'{config["TempFolder"]}Q-ETL_from_dataframe_{str(randrange(1000))}.fgb'
            dataframe.to_file(tmp_path, driver='FlatGeobuf')
            logger.info('Temporary layer created')

            logger.info('Creating QGIS layer')
            tmp_layer =  QgsVectorLayer(tmp_path, f'QgsLayer_ {str(randrange(1000))}', "ogr")
            #layer = tmp_layer.materialize(QgsFeatureRequest().setFilterFids(tmp_layer.allFeatureIds()))

            tmp_layer.selectAll()
            
            context  = QgsProcessingContext()
            layer = processing.run("native:saveselectedfeatures", {'INPUT': tmp_layer, 'OUTPUT': 'memory:'}, context=context)['OUTPUT']
            layer.removeSelection()
            try:
                QgsProject.instance().removeMapLayer(tmp_layer.id())
                context.temporaryLayerStore().removeAllMapLayers()   
                tmp_layer = None
                del tmp_layer, dataframe
                os.remove(tmp_path)
            except:
                logger.info('Could not delete temporary layer - manual cleanup is required')

            logger.info('Layer creation finished')
            return layer

        except Exception as error:
            logger.error("An error occured exporting layer to Pandas dataframe")
            logger.error(f'{type(error).__name__}  –  {str(error)}')
            logger.critical("Program terminated")
            script_failed()