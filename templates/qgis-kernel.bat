REM ============================================================================
REM QGIS Jupyter Kernel Batch File
REM ============================================================================
REM This file is used to start a Jupyter kernel with QGIS environment.
REM It should be placed in C:\OSGeo4W\bin\qgis-kernel.bat
REM ============================================================================

@echo off

REM Load OSGeo4W environment
call "%~dp0o4w_env.bat"
@echo off

REM Set QGIS specific environment variables
path %OSGEO4W_ROOT%\apps\qgis\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis
set GDAL_FILENAME_IS_UTF8=YES
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis\python;%PYTHONPATH%

REM Start Jupyter kernel
python -m ipykernel_launcher -f %1
