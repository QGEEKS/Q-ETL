from core.logger import *
from core.misc import script_failed
import sys, os
import shutil
import sqlite3
from core.misc import get_config, layerHasFeatures
from qgis.analysis import QgsNativeAlgorithms
from qgis.core import QgsCoordinateReferenceSystem, QgsVectorLayer, QgsProcessingFeedback, QgsProperty
from qgis import processing
import requests


class Worker:
    '''
    Base class for transforming data.
    '''

    ## Method that draws the progress bar
    def printProgressBar(value,label):
        n_bar = 40 #size of progress bar
        max = 100
        j= value/max
        sys.stdout.write('\r')
        bar = '█' * int(n_bar * j)
        bar = bar + '-' * int(n_bar * (1-j))
        sys.stdout.write(f"{label.ljust(10)} | [{bar:{n_bar}s}] {int(100 * j)}% ")
        sys.stdout.flush()
        sys.stdout.write('')        

    ## The progress bar function
    def progress_changed(progress):
        Worker.printProgressBar(progress, '%')

    ## The shared element for progress across all workers
    progress = QgsProcessingFeedback()
    progress.progressChanged.connect(progress_changed)

    ## The shared element for logging across all workers
    logger = get_logger() 


    class Vector:
        '''
        A Worker subclass that contains methods to transform vector data or their attributes.
        '''

        def attributeindex(layer: QgsVectorLayer, field: str):
            """
            Creates an index to speed up queries made against a field in a table.
            Support for index creation is dependent on the layer's data provider and the field type.

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem
                field (string): The field to base the index on

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Crating attribute index on " + layer + " on filed " + field)
            try:
                parameter = {
                    'INPUT': field,
                    'FIELD': field,
                    'OUTPUT': 'memory:extracted'
                }
                result = processing.run('native:createattributeindex', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info(f'Parameters: {str(parameter)}')
                logger.info("createattributeindex  finished")
                return result
            except Exception as error:
                logger.error("An error occured in createattributeindex")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def addxyfieldstolayer(layer: QgsVectorLayer, crs: str):
            """
            Adds X and Y (or latitude/longitude) fields to a point layer. The X/Y fields can be calculated in a different CRS to the layer (e.g. creating latitude/longitude fields for a layer in a projected CRS).

            Args:
                layer (QgsVectorLayer): The input layer.
                crs (string): Coordinate reference system to use for the generated x and y fields.

            Returns:
                layer (QgsVectorLayer): Specify the output layer.
            """

            logger.info(f"Adding X/Y fields to {layer}" )
            try:
                parameter = {
                    'INPUT': layer,
                    'CRS': crs,
                    'OUTPUT': 'memory:output_from_addxyfieldstolayer'
                }
                result = processing.run('native:addxyfieldstolayer', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info(f'Parameters: {str(parameter)}')
                logger.info("addxyfieldstolayer  finished")
                return result
            except Exception as error:
                logger.error("An error occured in addxyfieldstolayer")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def convexhull(layer: QgsVectorLayer):
            """
            Calculates the convex hull for each feature in an input layer.

            Args:
                layer (QgsVectorLayer): Input vector layer

            Returns:
                layer (QgsVectorLayer): Specify the output vector layer.
            """

            logger.info(f" Calculating convexhull for layer {layer}")
            try:
                parameter = {
                    'INPUT': layer,
                    'OUTPUT': 'memory:output_from_convexhull'
                }
                result = processing.run('native:convexhull', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info(f'Parameters: {str(parameter)}')
                logger.info("convexhull  finished")
                return result
            except Exception as error:
                logger.error("An error occured in convexhull")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def concavehull(inputlayer:QgsVectorLayer, alpha: float, holes: bool, multigeom: bool ):
            """
            Computes the concave hull of the features from an input point layer.

            Args:
                inputlayer (QgsVectorLayer): Input point vector layer
                alpha (float): Number from 0 (maximum concave hull) to 1 (convex hull).
                holes (boolean): Choose whether to allow holes in the final concave hull
                multigeom (boolean): Check if you want to have singlepart geometries instead of multipart ones.

            Returns:
                layer (QgsVectorLayer): Specify the output vector layer
            """

            logger.info('calcualting concavehull')
            try:
                parameters = {
                    'INPUT': inputlayer,
                    'ALPHA' : alpha,
                    'HOLES' : holes,
                    'NO_MULTIGEOMETRY' : multigeom,
                    'OUTPUT': 'memory:output_from_concavehull'
                }
                logger.info(f'Parameters: {str(parameters)}')
                result = processing.run('native:concavehull', parameters, feedback=Worker.progress)['OUTPUT']
                logger.info('concavehull finished')
                return result
            except Exception as error:
                logger.error("An error occured in concavehull")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()            

        def extractvertices(inputlayer:QgsVectorLayer):
            """
            Takes a vector layer and generates a point layer with points representing the vertices in the input geometries.
            The attributes associated to each point are the same ones associated to the feature that the vertex belongs to.
            Additional fields are added to the vertices indicating the vertex index (beginning at 0), the feature’s part and its index within the part
            (as well as its ring for polygons), distance along original geometry and bisector angle of vertex for original geometry.

            Args:
                inputlayer (QgsVectorLayer): Input vector layer

            Returns:
                layer (QgsVectorLayer): Specify the output vector layer
            """

            logger.info('Extracting vertices')
            try:
                parameters = {
                    'INPUT': inputlayer,
                    'OUTPUT': 'memory:output_from_extractvertices'
                }
                logger.info(f'Parameters: {str(parameters)}')
                result = processing.run('native:extractvertices', parameters, feedback=Worker.progress)['OUTPUT']
                logger.info('extractvertices finished')
                return result
            except Exception as error:
                logger.error("An error occured in extractvertices")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()    

        def multiringconstantbuffer(inputlayer:QgsVectorLayer, rings: int, distance : str):
            """
            Computes multi-ring (donut) buffer for the features of the input layer, using a fixed or dynamic distance and number of rings.

            Args:
                inputlayer (QgsVectorLayer): Input vector layer
                rings (integer): The number of rings. It can be a unique value (same number of rings for all the features) or it can be taken from features data (the number of rings depends on feature values).
                distance (string): Distance between the rings. It can be a unique value (same distance for all the features) or it can be taken from features data (a field in the input data layer).

            Returns:
                layer (QgsVectorLayer): Specify the output polygon vector layer
            """

            logger.info('Creating multiringconstantbuffer')
            try:
                dist = float(distance)
                logger.info('Using distance value')
            except:
                dist = QgsProperty.fromExpression(f'"{distance}"')
                logger.info('Using distance from field')
            
            try:
                parameters = {
                    'INPUT': inputlayer,
                    'RINGS': rings,
                    'DISTANCE': distance,
                    'OUTPUT': 'memory:output_from_multiringconstantbuffer'
                }
                logger.info(f'Parameters: {str(parameters)}')
                result = processing.run('native:multiringconstantbuffer', parameters, feedback=Worker.progress)['OUTPUT']
                logger.info('multiringconstantbuffer finished')
                return result
            except Exception as error:
                logger.error("An error occured in multiringconstantbuffer")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed() 

        def poleofinaccessibility(inputlayer:QgsVectorLayer, tolerance: int):
            """
            Calculates the pole of inaccessibility for a polygon layer, which is the most distant internal point from the boundary of the surface. 
            This algorithm uses the ‘polylabel’ algorithm (Vladimir Agafonkin, 2016), which is an iterative approach guaranteed to find the true pole of inaccessibility within
            a specified tolerance. A more precise tolerance (lower value) requires more iterations and will take longer to calculate. 
            The distance from the calculated pole to the polygon boundary will be stored as a new attribute in the output layer.

            Args:
                inputlayer (QgsVectorLayer): Input vector layer
                tolerance (integer): Set the tolerance for the calculation. Default 1

            Returns:
                layer (QgsVectorLayer): Specify the output polygon vector layer.
            """

            logger.info('calcualting poleofinaccessibility')
            try:
                parameters = {
                    'INPUT': inputlayer,
                    'TOLERANCE' : tolerance,
                    'OUTPUT': 'memory:output_from_poleofinaccessibility'
                }
                logger.info(f'Parameters: {str(parameters)}')
                result = processing.run('native:poleofinaccessibility', parameters, feedback=Worker.progress)['OUTPUT']
                logger.info('poleofinaccessibility finished')
                return result
            except Exception as error:
                logger.error("An error occured in poleofinaccessibility")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()


        def symmetricaldifference(inputlayer: QgsVectorLayer, overlay_layer: QgsVectorLayer):
            """
            Creates a layer containing features from both the input and overlay layers but with the overlapping areas between the two layers removed.
            The attribute table of the symmetrical difference layer contains attributes and fields from both the input and overlay layers.

            Args:
                inputlayer (QgsVectorLayer): First layer to extract (parts of) features from.
                overlay_layer (QgsVectorLayer): Second layer to extract (parts of) features from. Ideally the geometry type should be the same as input layer.

            Returns:
                layer (QgsVectorLayer): Specify the layer to contain (the parts of) the features from the input and overlay layers that do not overlap features from the other layer
            """

            logger.info('calcualting symetrical difference')
            try:
                parameters = {
                    'INPUT': inputlayer,
                    'OVERLAY' : overlay_layer,
                    'OUTPUT': 'memory:output_from_symmetricaldifference'
                }
                logger.info(f'Parameters: {str(parameters)}')
                result = processing.run('native:symmetricaldifference', parameters, feedback=Worker.progress)['OUTPUT']
                logger.info('Symmetricaldifference finished')
                return result
            except Exception as error:
                logger.error("An error occured in symmetricaldifference")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()

        def lineintersections(inputlayer: QgsVectorLayer, split_layer: QgsVectorLayer, input_fields: list, intersect_fields: list):
            """
            Splits the lines or polygons in one layer using the lines or polygon rings in another layer to define the breaking points. Intersection between geometries in both layers are considered as split points.
            Output will contain multi geometries for split features.

            Args:
                inputlayer (QgsVectorLayer): Input line layer.
                split_layer (QgsVectorLayer): Layer to use to find line intersections.
                input_fields (list of strings): Field(s) of the input layer to keep in the output. If no fields are chosen all fields are taken.
                intersect_fields (list of strings): Field(s) of the intersect layer to keep in the output. If no fields are chosen all fields are taken. Duplicate field names will be appended a count suffix to avoid collision

            Returns:
                layer (QgsVectorLayer): Specify the layer to contain the intersection points of the lines from the input and overlay layers.
            """

            logger.info('Performing line intersections')
            try:
                parameters = {
                    'INPUT': inputlayer,
                    'INTERSECT': split_layer,
                    'INPUT_FIELDS' : input_fields, 
                    'INTERSECT_FIELDS' : intersect_fields,
                    'OUTPUT': 'memory:output_from_lineintersections'
                }
                logger.info(f'Parameters: {str(parameters)}')
                result = processing.run('native:lineintersections', parameters, feedback=Worker.progress)['OUTPUT']
                logger.info('Lineintersections finished')
                return result
            except Exception as error:
                logger.error("An error occured in Lineintersections")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()

        def kmeansclustering(inputlayer: QgsVectorLayer, clusters: int):
            """
            Calculates the 2D distance based k-means cluster number for each input feature.
            K-means clustering aims to partition the features into k clusters in which each feature belongs to the cluster with the nearest mean. The mean point is represented by the barycenter of the clustered features.
            If input geometries are lines or polygons, the clustering is based on the centroid of the feature.

            Args:
                inputlayer (QgsVectorLayer): Layer to analyze
                clusters (integer): Number of clusters to create with the features

            Returns:
                layer (QgsVectorLayer): Specify the output vector layer for generated the clusters.
            """

            logger.info('Calculating clusters')
            try:
                parameters = {
                    'INPUT': inputlayer,
                    'CLUSTERS' : clusters,
                    'OUTPUT': 'memory:output_from_kmeansclustering'
                }
                logger.info(f'Parameters: {str(parameters)}')
                result = processing.run('native:kmeansclustering', parameters, feedback=Worker.progress)['OUTPUT']
                logger.info('Kmeansclustering finished')
                return result
            except Exception as error:
                logger.error("An error occured in Kmeansclustering")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()

        def dbscanclustering(inputlayer: QgsVectorLayer, min_clusters: int, max_dist: int ):
            """
            Clusters point features based on a 2D implementation of Density-based spatial clustering of applications with noise (DBSCAN) algorithm.
            The algorithm requires two parameters, a minimum cluster size, and the maximum distance allowed between clustered points.

            Args:
                inputlayer (QgsVectorLayer): Layer to analyze
                min_clusters (integer): Minimum number of features to generate a cluster
                max_dist (integer): Distance beyond which two features can not belong to the same cluster (eps)

            Returns:
                layer (QgsVectorLayer): Specify the vector layer for the result of the clustering.
            """

            logger.info('Performing DBScan clustering')
            try:
                parameters = {
                    'INPUT': inputlayer,
                    'MIN_SIZE' : min_clusters,
                    'EPS': max_dist,
                    'OUTPUT': 'memory:output_from_dbscanclustering'
                }
                logger.info(f'Parameters: {str(parameters)}')
                result = processing.run('native:dbscanclustering', parameters, feedback=Worker.progress)['OUTPUT']
                logger.info('Dbscanclustering finished')
                return result
            except Exception as error:
                logger.error("An error occured in Dbscanclustering")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()

        def countpointsinpolygon(polygons: QgsVectorLayer, points: QgsVectorLayer, weight : str, fieldname: str):
            """
            Takes a point and a polygon layer and counts the number of points from the point layer in each of the polygons of the polygon layer.
            A new polygon layer is generated, with the exact same content as the input polygon layer, but containing an additional field with the points count corresponding to each polygon.

            Args:
                polygons (QgsVectorLayer): Polygon layer whose features are associated with the count of points they contain
                points (QgsVectorLayer): Point layer with features to count
                weight (string): A field from the point layer. The count generated will be the sum of the weight field of the points contained by the polygon. If the weight field is not numeric, the count will be 0.
                fieldname (string): The name of the field to store the count of points

            Returns:
                layer (QgsVectorLayer): Specification of the output layer.
            """

            logger.info('Conducting point in polygon')
            try:
                if isinstance(weight, int):
                    value = weight
                else:
                    value = 0

                parameters = {
                    'POLYGONS': polygons,
                    'POINTS': points,
                    'WEIGHT': value,
                    'FIELD' : fieldname,
                    'OUTPUT': 'memory:output_from_countpointsinpolygon'
                }
                logger.info(f'Parameters: {str(parameters)}')
                result = processing.run('native:Countpointsinpolygon', parameters, feedback=Worker.progress)['OUTPUT']
                logger.info('Promote to multipart finished')
                return result
            except Exception as error:
                logger.error("An error occured in Countpointsinpolygon")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()  

        def promoteToMultipart(layer: QgsVectorLayer):
            """
            Generates a vectorlayer in which all geometries are multipart.

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer that is used as input.

            Returns:
                layer (QgsVectorLayer): The QgsVectorLayer containing multi geometries.
            """

            logger.info('Collecting geometries')
            try:
                parameters = {
                    'INPUT': layer,
                    'OUTPUT': 'memory:multipart'
                }
                logger.info(f'Parameters: {str(parameters)}')
                result = processing.run('native:promotetomulti', parameters, feedback=Worker.progress)['OUTPUT']
                logger.info('Promote to multipart finished')
                return result
            except Exception as error:
                logger.error("An error occured in promoteToMultipart")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()

        def extractByExpression(layer: QgsVectorLayer, expression: str):
            """
            Creates a vector layer from an input layer, containing only matching features.
            The criteria for adding features to the resulting layer is based on a QGIS expression.

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer that is used as input.
                expression (string): Expression to filter the vector layer

            Returns:
                layer (QgsVectorLayer): The QgsVectorLayer output layer.
            """

            logger.info("Extracting by expression")
            try:
                parameter = {
                    'INPUT': layer,
                    'EXPRESSION': expression,
                    'OUTPUT': 'memory:extracted'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:extractbyexpression', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("Extractbyexpression  finished")
                return result
            except Exception as error:
                logger.error("An error occured in extractByExpression")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def renameTableField (layer: QgsVectorLayer, field: str, newname: str):
            """
            Renames an existing field from a vector layer.  
            The original layer is not modified. A new layer is generated where the attribute table contains the renamed field.
            QGIS processing algorithem: native:renametablefield

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem
                field (string): The field that is to be renamed
                newname (string): New name for the field

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Renaming field")
            try:
                parameter = {
                    'INPUT': layer,
                    'FIELD': field,
                    'NEW_NAME': newname,
                    'OUTPUT': 'memory:extracted'
                }
                result = processing.run('native:renametablefield', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info(f'Parameters: {str(parameter)}')
                logger.info("renameTableField  finished")
                return result
            except Exception as error:
                logger.error("An error occured in renameTableField")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def timeStamper(layer: QgsVectorLayer, ts_fieldname: str):
            """
            Create an attribute woth current timestamp on features.

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem
                ts_fieldname (string): The name of the new timestamp field

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info(f'Creating timestamp {ts_fieldname} using fieldCalculator')
            newLayer = Worker.fieldCalculator(layer, ts_fieldname, 5, 0, 0, ' now() ')
            return newLayer

        def fieldCalculator (layer: QgsVectorLayer, fieldname: str, fieldtype: int, fieldlength: int, fieldprecision: int, formula: str):
            """
            Scripting the field calcualtor
            You can use all the supported expressions and functions.
            The original layer is not modified. A new layer is generated where the attribute table contains the calucalted field
            QGIS processing algorithem: native:fieldcalculator

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem
                fieldname (string): The name of the new calcualted field
                fieldtype (integer): Type of the field,  Default: 0  (0 — Float, 1 — Integer, 2 — String, 3 — Date)
                fieldlength (integer): Lenght of the field, Default: 10.
                fieldprecision (integer): Precision of the field, Default: 3.
                formula (string): The expression that populates the values of the field.

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Calculating field")
            try:
                parameter = {
                    'INPUT': layer,
                    'FIELD_NAME': fieldname,
                    'FIELD_TYPE': fieldtype,
                    'FIELD_LENGTH': fieldlength,
                    'FIELD_PRECISION': fieldprecision,
                    'FORMULA': formula,
                    'OUTPUT': 'memory:extracted'
                }
                result = processing.run('native:fieldcalculator', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info(f'Parameters: {str(parameter)}')
                logger.info("fieldCalculator  finished")
                return result
            except Exception as error:
                logger.error("An error occured in fieldCalculator")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def deleteColumns (layer: QgsVectorLayer, columns: list):
            """
            Takes a vector layer and generates a new one that has the same features but without the selected columns.

            Args:
                layer (QgsVectorLayer): Input vector layer to drop field(s) from
                columns (list of strings): The field(s) to drop

            Returns:
                layer (QgsVectorLayer): The QgsVectorLayer output layer.
            """

            logger.info("deleting fields")

            try:
                parameter = {
                    'INPUT': layer,
                    'COLUMN':columns,
                    'OUTPUT': 'memory:extracted'
                }
                result = processing.run('native:deletecolumn', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info(f'Parameters: {str(parameter)}')
                logger.info("deleteColumns  finished")
                return result
            except Exception as error:
                logger.error("An error occured in deleteColumns")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def addAutoIncrementalField(layer: QgsVectorLayer, fieldname: str, start: int):
            """
            Adds a new integer field to a vector layer, with a sequential value for each feature.
            This field can be used as a unique ID for features in the layer. The new attribute is not added to the input layer but a new layer is generated instead.
            The initial starting value for the incremental series can be specified. Optionally, the incremental series can be based on grouping 
            fields and a sort order for features can also be specified.

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer that is used as input.
                fieldname (string): Name of the field with autoincremental values.
                start (integer): Choose the initial number of the incremental count, Default: 0.

            Returns
                layer (QgsVectorLayer): The QgsVectorLayer output layer.
            """

            logger.info("Adding incremental field")
            try:
                parameter = {
                    'INPUT': layer,
                    'FIELD_NAME': fieldname,
                    'START':start,
                    'MODULUS':0,
                    'GROUP_FIELDS':[],
                    'SORT_EXPRESSION':'',
                    'SORT_ASCENDING':True,
                    'SORT_NULLS_FIRST':False,
                    'OUTPUT': 'memory:extracted'
                }
                result = processing.run('native:addautoincrementalfield', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info(f'Parameters: {str(parameter)}')
                logger.info("addAutoIncrementalField  finished")
                return result
            except Exception as error:
                logger.error("An error occured in addAutoIncrementalField")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()
    
        def spatialindex(layer: QgsVectorLayer):
            """
            Creates an index to speed up access to the features in a layer based on their spatial location.
            Support for spatial index creation is dependent on the layer's data provider.

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """
            
            logger.info("Crating spatial index on " + layer)
            try:
                parameter = {
                    'INPUT': layer,
                    'OUTPUT': 'memory:extracted'
                }
                result = processing.run('native:createspatialindex', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info(f'Parameters: {str(parameter)}')
                logger.info("createspatialindex  finished")
                return result
            except Exception as error:
                logger.error("An error occured in createspatialindex")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()
            
        def clip(layer: QgsVectorLayer, overlay: str):
            """
            Clips a vector layer using the features of an additional polygon layer.
            Only the parts of the features in the input layer that fall within the polygons of 
            the overlay layer will be added to the resulting layer.

            Args:
                layer (QgsVectorLayer): Layer containing the features to be clipped
                overlay (QgsVectorLayer): Layer containing the clipping features

            Returns:
                layer (QgsVectorLayer): Layer to contain the features from the input layer that are inside the overlay (clipping) layer
            """

            logger.info("Clipping layers")
            try:
                parameter = {
                    'INPUT': layer,
                    'OVERLAY': overlay,
                    'OUTPUT': 'memory:extracted'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:clip', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("Clip  finished")
                return result
            except Exception as error:
                logger.error("An error occured in Clip")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def joinByLocation(layer: QgsVectorLayer, predicate: int, join: str, join_fields: list, method: int, discard_nomatching: bool, prefix: str):
            """
            Takes an input vector layer and creates a new vector layer that is an extended version of
            the input one, with additional attributes in its attribute table.
            The additional attributes and their values are taken from a second vector layer.
            A spatial criteria is applied to select the values from the second layer that are added to each 
            feature from the first layer.
            
            Args:
                layer (QgsVectorLayer): Input vector layer. The output layer will consist of the features of this layer with attributes from matching features in the second layer.
                predicate (integer): Type of spatial relation the source feature should have with the target feature so that they could be joined. One or more of: 0 — intersect, 1 — contain, 2 — equal, 3 — touch, 4 — overlap, 5 — are within 6 — cross.
                join (QgsVectorLayer): The join layer. Features of this vector layer will add their attributes to the source layer attribute table if they satisfy the spatial relationship.
                join_fields (list of strings): Select the specific fields you want to add from the join layer. By default all the fields are added.
                method (integer): The type of the final joined layer. One of: 0 — Create separate feature for each matching feature (one-to-many) 1 — Take attributes of the first matching feature only (one-to-one) 2 — Take attributes of the feature with largest overlap only (one-to-one)
                discard_nomatching (boolean): Remove from the output the input layer’s features which could not be joined
                prefix (string): Add a prefix to joined fields in order to easily identify them and avoid field name collision

            Returns:
                layer (QgsVectorLayer): the output vector layer for the join.
            """

            logger.info("Clipping layers")
            try:
                parameter = {
                    'INPUT': layer,
                    'PREDICATE':predicate,
                    'JOIN':join,
                    'JOIN_FIELDS':join_fields,
                    'METHOD':method,
                    'DISCARD_NONMATCHING':discard_nomatching,
                    'PREFIX':prefix,
                    'OUTPUT': 'memory:extracted'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:joinattributesbylocation', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("joinByLocation finished")
                return result
            except Exception as error:
                logger.error("An error occured in joinByLocation")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def extractByLocation(layer: QgsVectorLayer, predicate: int, intersect: str):
            """_summary_

            Args:
                layer (QgsVectorLayer): Input vector layer. 
                predicate (integer): Type of spatial relation the source feature should have with the target feature so that they could be joined. One or more of: 0 — intersect, 1 — contain, 2 — equal, 3 — touch, 4 — overlap, 5 — are within 6 — cross.
                intersect (QgsVectorLayer): Intersection vector layer

            Returns:
                layer (QgsVectorLayer): the output vector layer for the join.
            """

            logger.info("Extracting by location")
            try:
                parameter = {
                    'INPUT': layer,
                    'PREDICATE':predicate,
                    'INTERSECT':intersect,
                    'OUTPUT': 'memory:extracted'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:extractbylocation', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("extractByLocation finished")
                return result
            except Exception as error:
                logger.error("An error occured in extractByLocation")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def randomExtract(layer: QgsVectorLayer, method: int, number: int):
            """
            Takes a vector layer and generates a new one that contains only a subset of the features in the input layer.
            The subset is defined randomly, based on feature IDs, using a percentage or count value to define 
            the total number of features in the subset.

            Args:
                layer (QgsVectorLayer): Input vector layer. 
                method (integer): Random selection method. One of: 0 — Number of selected features 1 — Percentage of selected features
                number (integer): Number or percentage of features to select

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Extracting random features")
            try:
                parameter = {
                    'INPUT': layer,
                    'METHOD':method,
                    'NUMBER':number,
                    'OUTPUT': 'memory:extracted'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:randomextract', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("randomExtract finished")
                return result
            except Exception as error:
                logger.error("An error occured in randomExtract")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def difference(layer: QgsVectorLayer, overlay: QgsVectorLayer):
            """
            Extracts features from the input layer that don’t fall within the boundaries of the overlay layer.
            Input layer features that partially overlap the overlay layer feature(s) are split along the 
            boundary of those feature(s.

            Args:
                layer (QgsVectorLayer): Layer to extract (parts of) features from.
                overlay (QgsVectorLayer): Layer containing the geometries that will be subtracted from the iniput layer geometries

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Finding differences")
            try:
                parameter = {
                    'INPUT': layer,
                    'OVERLAY': overlay,
                    'OUTPUT': 'memory:extracted'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:difference', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("Difference  finished")
                return result
            except Exception as error:
                logger.error("An error occured in Difference")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def reproject(layer: QgsVectorLayer, targetEPSG: int):
            """
            Reprojects a vector layer in a different CRS.
            The reprojected layer will have the same features and attributes of the input layer.
            QGIS processing algorithem: native:reprojectlayer.

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem
                targetEPSG (integer): The EPSG code og the target coordinate system.

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Running reporjector V2")
            if layerHasFeatures(layer):
                logger.info("Processing " + str(layer.featureCount()) +" features")
            try:
                parameter = {
                    'INPUT': layer,
                    'TARGET_CRS': QgsCoordinateReferenceSystem(targetEPSG),
                    'OUTPUT': 'memory:Reprojected'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:reprojectlayer', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("Reproject finished")
                return result
            except Exception as error:
                logger.error("An error occured reprojectiong layer")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def simplify(layer: QgsVectorLayer, method: int, tolerance:int):
                """
                Simplifies the geometries in a line or polygon layer. 
                It creates a new layer with the same features as the ones in the input layer, but with geometries containing a lower number of vertices.
                QGIS processing algorithem: native:simplifygeometries.

                Args:
                    layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem
                    method (integer): Simplification method. One of: 0 — Distance (Douglas-Peucker), 1 — Snap to grid, 2 — Area (Visvalingam)
                    tolerance (integer): Threshold tolerance (in units of the layer): if the distance between two nodes is smaller than the tolerance value, the segment will be simplified and vertices will be removed.

                Returns:
                    layer (QgsVectorLayer): The result output from the algorithem
                """

                logger.info("Running simplify")
                if layerHasFeatures(layer):
                    logger.info("Processing " + str(layer.featureCount()) +" features")
                try:
                    parameter = {
                        'INPUT': layer,
                        'METHOD':method,
                        'TOLERANCE':tolerance,
                        'OUTPUT': 'memory:simplify'
                    }
                    logger.info(f'Parameters: {str(parameter)}')
                    result = processing.run('native:simplifygeometries', parameter, feedback=Worker.progress)['OUTPUT']
                    logger.info("Simplifygeometries finished")
                    return result
                except Exception as error:
                    logger.error("An error occured in simplifygeometries")
                    logger.error(f'{type(error).__name__}  –  {str(error)}')
                    logger.critical("Program terminated" )
                    sys.exit()

        def forceRHR(layer: QgsVectorLayer):
            """
            Forces polygon geometries to respect the Right-Hand-Rule, in which the area that is bounded
            by a polygon is to the right of the boundary. 
            In particular, the exterior ring is oriented in a clockwise direction and any interior
            rings in a counter-clockwise direction.
            QGIS processing algorithem: native:forcerhr

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Running force right-hand rule")
            if layerHasFeatures(layer):
                logger.info("Processing " + str(layer.featureCount()) +" features")
            try:
                parameter = {
                    'INPUT': layer,
                    'OUTPUT': 'memory:forced'
                }
                result = processing.run('native:forcerhr', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("forceRHR finished")
                return result
            except Exception as error:
                logger.error("An error occured in forceRHR")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def join_by_attribute(layer1: QgsVectorLayer, layer1_field:str, layer2: QgsVectorLayer, layer2_field: str, fields_to_copy: list, method:int, discard: bool, prefix:str):
            """
            Takes an input vector layer and creates a new vector layer that is an extended version of the input one, 
            with additional attributes in its attribute table.
            The additional attributes and their values are taken from a second vector layer. An attribute is selected in each of them 
            to define the join criteria.
            QGIS processing algorithem: native:joinattributestable.

            Args:
                layer1 (QgsVectorLayer): The 1. QgsVectorLayer input for the algorithem
                layer1_field (string): Field of the source layer to use for the join
                layer2 (QgsVectorLayer): The 2. QgsVectorLayer input for the algorithem
                layer2_field (string): Field of the source layer to use for the join
                fields_to_copy (list of strings): Select the specific fields you want to add. By default all the fields are added. Default []
                method (integer): The type of the final joined layer. One of: 0 — Create separate feature for each matching feature (one-to-many) 1 — Take attributes of the first matching feature only (one-to-one)
                discard (boolean): Check if you don’t want to keep the features that could not be joined
                prefix (string): Add a prefix to joined fields in order to easily identify them and avoid field name collision

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Joining features features")
            if layerHasFeatures(layer1):
                logger.info("Processing " + str(layer1.featureCount()) +" features")
            try:
                parameter = {
                    'INPUT':layer1,
                    'FIELD':layer1_field,
                    'INPUT_2':layer2,
                    'FIELD_2':layer2_field,
                    'FIELDS_TO_COPY':fields_to_copy,
                    'METHOD':method,
                    'DISCARD_NONMATCHING':discard,
                    'PREFIX':prefix,
                    'OUTPUT': 'memory:joined'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:joinattributestable', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("Joinattributestable finished")
                if layerHasFeatures(result):
                    logger.info("Returning " + str(result.featureCount()) +" features")
                return result
            except Exception as error:
                logger.error("An error occured in joinattributestable")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def dissolveFeatures(layer: QgsVectorLayer, fieldList: list, disjoined: bool):
            """
            Takes a vector layer and combines its features into new features. 
            One or more attributes can be specified to dissolve features belonging to the same class 
            (having the same value for the specified attributes), alternatively all features can be dissolved to a single feature.
            All output geometries will be converted to multi geometries. 
            QGIS processing algorithem: native:dissolve.

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem
                fieldList (list of strings): List of fields to dissolve on. Default []
                disjoined (boolean): Keep disjoint features separate ? Default: False

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem

            """
            logger.info("Dissolving features")
            if layerHasFeatures(layer):
                logger.info("Processing " + str(layer.featureCount()) +" features")
            try:
                parameter = {
                    'INPUT': layer,
                    'FIELD' : fieldList,
                    'SEPARATE_DISJOINT' : False,
                    'OUTPUT': 'memory:dissolved'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:dissolve', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("DissolveFeatures finished")
                if layerHasFeatures(result):
                    logger.info("Returning " + str(result.featureCount()) +" features")
                return result
            except Exception as error:
                logger.error("An error occured in dissolveFeatures")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def bufferLayer(layer: QgsVectorLayer, distance: int, segements: int, endcapStyle: int, joinStyle: int, miterLimit: int, dissolve: bool):
            """
            Computes a buffer area for all the features in an input layer, using a fixed or data defined distance.
            It is possible to use a negative distance for polygon input layers.
            In this case the buffer will result in a smaller polygon (setback).
            QGIS processing algorithem: native:buffer

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem
                distance (integer): The buffer distance. Default: 10.0
                segements (integer): Number og segments. Default: 5
                endcapStyle (integer): Controls how line endings are handled in the buffer. Default: 0 (One of: 0 — Round, 1 — Flat, 2 — Square)
                joinStyle (integer): Specifies whether round, miter or beveled joins should be used when offsetting corners in a line. Default: 0 (Options are: 0 — Round, 1 — Miter, 2 — Bevel)
                miterLimit (integer): Sets the maximum distance from the offset geometry to use when creating a mitered join as a factor of the offset distance Default: 0, Minimum: 1
                dissolve (boolean): Dissolve the final buffer. Default: false.

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Creating buffer layer")
            if layerHasFeatures(layer):
                logger.info("Processing " + str(layer.featureCount()) +" features")
            try:
                parameter = {
                    'INPUT': layer,
                    'DISTANCE': distance,
                    'SEGMENTS': segements,
                    'END_CAP_STYLE': endcapStyle,
                    'JOIN_STYLE': joinStyle,
                    'MITER_LIMIT': miterLimit,
                    'DISSOLVE': dissolve,
                    'OUTPUT': 'memory:buffer'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:buffer', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("BufferLayer finished")
                return result
            except Exception as error:
                logger.error("An error occured in BufferLayer")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def fixGeometry(layer: QgsVectorLayer):
            """
            Attempts to create a valid representation of a given invalid geometry without losing any of the input vertices.
            Already valid geometries are returned without further intervention. Always outputs multi-geometry layer.
            QGIS processing algorithem: native:fixgeometries

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Fixing geometries")
            if layerHasFeatures(layer):
                logger.info("Processing " + str(layer.featureCount()) +" features")
            try:
                parameter = {
                    'INPUT': layer,
                    'OUTPUT': 'memory:buffer'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:fixgeometries', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("FixGeometry finished")
                return result
            except Exception as error:
                logger.error("An error occured in FixGeometry")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def createCentroids(layer: str):
            """
            Creates a new point layer, with points representing the centroids of the geometries of the input layer.
            The centroid is a single point representing the barycenter (of all parts) of the feature, so it can be outside the feature borders. But can also be a point on each part of the feature.
            The attributes of the points in the output layer are the same as for the original features.

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Creating centroids")
            if layerHasFeatures(layer):
                logger.info("Processing " + str(layer.featureCount()) +" features")
            try:
                parameter = {
                    'INPUT': layer,
                    'ALL_PARTS':False,
                    'OUTPUT': 'memory:buffer'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:centroids', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("Centroids finished")
                return result
            except Exception as error:
                logger.error("An error occured in createCentroids")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()

        def randomselection(layer: QgsVectorLayer, method: int, number: int):
            """
            Takes a vector layer and selects a subset of its features. No new layer is generated by this algorithm.
            The subset is defined randomly, based on feature IDs, using a percentage or count value to define the 
            total number of features in the subset.

            Args:
                layer (QgsVectorLayer): The QgsVectorLayer input for the algorithem
                method (integer): Random selection method. One of: 0 — Number of selected features, 1 — Percentage of selected features
                number (integer): Number or percentage of features to select

            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Performing random selection")
            if layerHasFeatures(layer):
                logger.info("Processing " + str(layer.featureCount()) +" features")
            try:
                parameter = {
                    'INPUT': layer,
                    'METHOD':method,
                    'NUMBER':number,
                    'OUTPUT': 'memory:buffer'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:randomextract', parameter, feedback=Worker.progress)['OUTPUT']
                if layerHasFeatures(result):
                    logger.info("Returning " + str(result.featureCount()) +" features")
                logger.info("randomextract finished")
                return result
            except Exception as error:
                logger.error("An error occured in FixGeometry")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def execute_sql(connection, databasetype, sql_expression, pgdb_name=None, driver=None):
            """
            Execute an SQL query against a database. 
            This can be used to create tables, truncate, build indexes etc.
            The database type must be specified in the 'database' parameter (one of 'Mssql' or 'Postgres')
            The default Mssql driver is 'SQL Server' - if this needs to be overwritten, specify the parameter driver, else leave it empty.
            SQL statments must be trippel double-quoted - prepare the statement in the QGIS sql executor tool for testing. 

            Args:
                connection (string): Name of a database connection from settings.json
                databasetype (string): The database type, one of 'Mssql' or 'Postgres'.
                sql_expression (string): The SQL expression to be executed. Use trippel double-quotes arraound the expression
                pgdb_name (string): Name of postgres database if databasetype is  Postgres. Defaults to None.
                driver (string): Defaults to None. The name of the Mssql driver, if 'SQL Server' is not working.

            Returns:
                Errorcode (integer): Returns 0 if the SQL is executed without errors.

            """

            config = get_config()
            if databasetype in ('Postgres', 'Mssql'):
                logger.info(f'Running SQL executor on {databasetype}' )
            else :
                logger.info(f'Unsupported database: {databasetype}, use one of "Mssql" or "Postgres"' )
                logger.critical("Program terminated" )
                sys.exit()
            try:
                dbconnection = config['DatabaseConnections'][connection]
                if databasetype == 'Mssql':
                    import pyodbc 
                    if driver == "":
                        mssqldriver = 'SQL Server'
                    else :
                        mssqldriver = 'driver'
                    cnxn = pyodbc.connect('DRIVER={'+mssqldriver+'};Server='+dbconnection['host']+';Database='+dbconnection['databasename']+';User ID='+dbconnection['user']+';Password='+dbconnection['password'])
                    logger.info("Using connection :" + 'DRIVER={'+mssqldriver+'};Server='+dbconnection['host']+';Database='+dbconnection['databasename']+';User ID='+dbconnection['user']+';Password=xxxxxxxx')
                    cursor = cnxn.cursor()
                    logger.info(f'Query: {sql_expression}' )
                    cursor.execute(sql_expression) 
                    logger.info("SQL executor finished")
                    return 0
                
                if databasetype == 'Postgres':
                    import psycopg2
                    connection = psycopg2.connect(user=dbconnection['user'], password=dbconnection['password'], host=dbconnection['host'], port=dbconnection['port'], database=pgdb_name)
                    logger.info("Using connection : user="+ dbconnection['user']+", password=xxxxxx, host="+dbconnection['host']+", port="+dbconnection['port']+", database="+pgdb_name )
                    cursor = connection.cursor()
                    logger.info(f'Query: {sql_expression}' )
                    cursor.execute(sql_expression)
                    connection.commit()
                    cursor.close()
                    connection.close()
                    logger.info("SQL executor finished")
                    return 0
                    
            except Exception as error:
                logger.error("An error occured running SQL executor")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def mergeVectorLayers(layers: list, crs: str ):
            """
            Combines multiple vector layers of the same geometry type into a single one.
            The attribute table of the resulting layer will contain the fields from all input layers. 
            If fields with the same name but different types are found then the exported field will be automatically 
            converted into a string type field. New fields storing the original layer name and source are also added.

            Optionally, the destination coordinate reference system (CRS) for the merged layer can be set. If it is 
            not set, the CRS will be taken from the first input layer. All layers will be reprojected to match this CRS.

            Args:
                layer (QgsVectorLayer): The layers that are to be merged into a single layer. Layers should be of the same geometry type.
                CRS (Crs): Choose the CRS for the output layer. If not specified, the CRS of the first input layer is used.
                
            Returns:
                layer (QgsVectorLayer): The result output from the algorithem
            """

            logger.info("Performing mergeVectorLayers")
            logger.info(f'Processing {str(len(layers))} layers')
            try:
                parameter = {
                    'LAYERS': layers,
                    'CRS':crs,
                    'OUTPUT': 'memory:buffer'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:mergevectorlayers', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info("Returning " + str(result.featureCount()) +" features")
                logger.info("mergeVectorLayers finished")
                return result
            except Exception as error:
                logger.error("An error occured in mergeVectorLayers")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()

        def delete_geopacakge_layers(geopackage: str, layernames: list):
            """
            Deletes one or more tables from a geopackage

            Args:
                geopackage (string): The full path for the geopackage file
                layernames (list of strings): List of layernames to be deleted
            """

            logger.info("Performing delete_geopacakge_layer")
            logger.info(f"Deleting layers {layernames}")

            if os.path.isfile(geopackage):
                try:
                    for layer in layernames:
                        logger.info(f"Deleting layer {layer}")
                        parameter = {'DATABASE':'{0}|layername={1}'.format(geopackage, layer),
                        'SQL':'drop table {0}'.format(layer)}
                        logger.info(f'Parameters: {str(parameter)}')
                        processing.run("native:spatialiteexecutesql", parameter )
                        logger.info(f"Layer deleted")
                    logger.info(f"Finished deleting layers")

                    
                except Exception as error:
                    logger.error("An error occured in delete_geopacakge_layer")
                    logger.error(f'{type(error).__name__}  –  {str(error)}')
                    logger.critical("Program terminated" )
                    script_failed()
            else:    
                pass

        def assign_projection(layer: QgsVectorLayer, targetEPSG: int):
            """
            Assign a new projection on a layer. The returned layer is precisely the same layer but assigned a new CRS.

            Args:
            layer : (QgsVectorLayer)Q The layer to be assigned a new CRS.
            targetEPSG (integer): The EPSG code og the target coordinate system.

            Returns:
                layer (QgsVectorLayer): Layer with the new projection assigned
            """

            logger.info(f'Assigning CRS EPSG:{targetEPSG} to {layer.name()}')
            try:
                parameter = {
                    'INPUT': layer,
                    'CRS': QgsCoordinateReferenceSystem(targetEPSG),
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }
                logger.info(f'Parameters: {str(parameter)}')
                result = processing.run('native:assignprojection', parameter, feedback=Worker.progress)['OUTPUT']
                logger.info('Assigning projection finished')
                return result
            except Exception as error:
                logger.error("An error occured assigning a new crs to layer")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

    class File:
        '''
        A Worker subclass that contains methods to work with the filesystem.
        '''

        def download_file(url, local_filename):
            """
            Downloads a file from the given URL and saves it locally.

            Args:
                url (string): The URL of the file to download
                local_filename (string): The local path where the file should be saved.

            Returns:
                boolean (boolean): True if download is succesful, otherwise False.
            """

            logger.info(f'Downloading file from {url}')
            try:
                with requests.get(url, stream=True) as response:
                    response.raise_for_status()
                    with open(local_filename, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                
                logger.info(f'Download completed: {local_filename}')
                return True
            
            except Exception as error:
                logger.error('An error occurred when downloading the file')
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()
            
            return False

        def folderTruncator(folder: str):
            """
            Deletes all contents of a folder (files and directories), but not the folder it self.

            Args:
                folder (string): Full path to the folder to be truncated

            Returns:
                None
            """

            logger.info(f'Truncating folder {folder}')
            try:
                for root, dirs, files in os.walk(folder):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                logger.info(f'Folder {folder} truncated')

                return None
            except Exception as error:
                logger.error("An error occured truncating folder")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                script_failed()

        def deleter(filepath : str):
            """
            A worker that deletes a specific file.

            Args:
                filepath (string): The full path to the file to delete
            """

            logger.info(f'Deleting file {filepath}')
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.info(f'File found and deleted')
                else:
                    logger.info(f'File does not exist, skipping delete.')
            
            except Exception as error:
                logger.error(f"An error occured deleting file {filepath}")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()
        
        def mover(input_filepath : str, output_filepath : str):
            """
            Moves a file from one location to another.
            Can also be used for renaming.

            Args:
                input_filepath (string): The full path to the file to move 
                output_filepath (string): The full path to the target file
            """

            logger.info(f'Moving file {input_filepath} to {output_filepath}')
            try:
                if os.path.exists(input_filepath):
                    shutil.copyfile(input_filepath, output_filepath)
                    logger.info(f'File moved')
                else:
                    logger.info(f'Input file does not exist, skipping move.')
            
            except Exception as error:
                logger.error(f"An error occured moving file {input_filepath}")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def lister(input_folder : str, file_extension : str):
            """
            Creates a python list of files with a specific extension, from an input location.
            Returns the full path to the files. 

            Args:
                input_folder (string): The full path to teh input folder.
                file_extension (string): The file extension to search for.

            Returns:
                list (list of strings): A list of file paths derived from the input directory of the specified file type
            """

            filelist = []
            logger.info(f'Building filelist of {file_extension}-files from directory {input_folder}')
            try:
                for root, dirs, files in os.walk(input_folder):          
                    for file in files:
                        if file.endswith(file_extension):
                            filelist.append(os.path.join(root, file))
                if len(filelist) > 0:
                    logger.info(f'Filelist returning {len(filelist)} elements')
                    return filelist
                else:
                    logger.info(f'Returning empty filelist for destinateion {input_folder}')
                    return []
            except Exception as error:
                logger.error(f"An error occured listing files from folder {input_folder}")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()

        def existence_checker(input_path : str):
            """
            Checks if a specific file exists. Returns True if file exists, False if not.

            Args:
                input_folder (string): The full path to the input folder.

            Returns:
                boolean (boolean): True/False if file exists.
            """

            logger.info(f'Checking if file {input_path} exists')
            try:
                if os.path.exists(input_path):
                    logger.info(f'File exists, returning True')
                    return True
                else:
                    logger.info(f'File does not exist, returning False')
                    return False
            except Exception as error:
                logger.error(f"An error occured checking if file {input_path} exists")
                logger.error(f'{type(error).__name__}  –  {str(error)}')
                logger.critical("Program terminated" )
                sys.exit()