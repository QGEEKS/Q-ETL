@echo off
REM ============================================================================
REM Q-ETL Jupyter Notebook Setup Script
REM ============================================================================
REM This script sets up Jupyter Notebook support for Q-ETL in VS Code
REM It reads paths from settings.json to automatically detect QGIS installation
REM ============================================================================

echo.
echo ============================================================================
echo Q-ETL Jupyter Notebook Setup
echo ============================================================================
echo.

REM Check if settings.json exists
if not exist "settings.json" (
    echo ERROR: settings.json not found in current directory.
    echo Please make sure you run this script from the Q-ETL root folder.
    echo.
    pause
    exit /b 1
)

REM Read QGIS paths from settings.json using PowerShell
echo [1/5] Reading QGIS paths from settings.json...
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "$json = Get-Content 'settings.json' -Raw | ConvertFrom-Json; $binFolder = $json.QGIS_bin_folder -replace '/', '\'; Write-Output $binFolder"`) do set QGIS_BIN_FOLDER=%%i
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "$json = Get-Content 'settings.json' -Raw | ConvertFrom-Json; $prefixPath = $json.Qgs_PrefixPath -replace '/', '\'; Write-Output $prefixPath"`) do set QGIS_PREFIX_PATH=%%i

REM Derive OSGEO4W_ROOT by removing \apps\qgis\bin from QGIS_bin_folder
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "$json = Get-Content 'settings.json' -Raw | ConvertFrom-Json; $binFolder = $json.QGIS_bin_folder -replace '/', '\'; $root = $binFolder -replace '\\apps\\qgis\\bin$', ''; Write-Output $root"`) do set OSGEO4W_ROOT=%%i

REM Verify paths (adjusted to ensure correct path resolution)
if not exist "%OSGEO4W_ROOT%\bin\python-qgis.bat" (
    echo ERROR: Could not find python-qgis.bat at: %OSGEO4W_ROOT%\bin\python-qgis.bat
    echo.
    echo Please verify your settings.json has correct paths:
    echo   QGIS_bin_folder: %QGIS_BIN_FOLDER%
    echo   Detected OSGEO4W_ROOT: %OSGEO4W_ROOT%
    echo.
    pause
    exit /b 1
) else (
    echo Successfully found python-qgis.bat at: %OSGEO4W_ROOT%\bin\python-qgis.bat
)

echo    Detected OSGeo4W: %OSGEO4W_ROOT%
echo    QGIS bin folder: %QGIS_BIN_FOLDER%
echo    QGIS prefix: %QGIS_PREFIX_PATH%
echo.

REM Install Python packages
echo [2/5] Installing Python packages (ipykernel, jupyter, coloredlogs)...
echo.
call "%OSGEO4W_ROOT%\bin\python-qgis.bat" -m pip install ipykernel jupyter coloredlogs
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Something went wrong during package installation.
    echo Continuing anyway...
    echo.
)

REM Create QGIS kernel batch file
echo.
echo [3/5] Creating QGIS Jupyter kernel batch file...

set KERNEL_BAT=%OSGEO4W_ROOT%\bin\qgis-kernel.bat

(
echo @echo off
echo call "%%~dp0o4w_env.bat"
echo @echo off
echo path %%OSGEO4W_ROOT%%\apps\qgis\bin;%%PATH%%
echo set QGIS_PREFIX_PATH=%%OSGEO4W_ROOT:\=/%%/apps/qgis
echo set GDAL_FILENAME_IS_UTF8=YES
echo set VSI_CACHE=TRUE
echo set VSI_CACHE_SIZE=1000000
echo set QT_PLUGIN_PATH=%%OSGEO4W_ROOT%%\apps\qgis\qtplugins;%%OSGEO4W_ROOT%%\apps\qt5\plugins
echo set PYTHONPATH=%%OSGEO4W_ROOT%%\apps\qgis\python;%%PYTHONPATH%%
echo python -m ipykernel_launcher -f %%1
) > "%KERNEL_BAT%"

echo    Created: %KERNEL_BAT%
echo.

REM Create and register Jupyter kernel
echo [4/5] Registering QGIS Python kernel in Jupyter...

set KERNEL_DIR=%APPDATA%\jupyter\kernels\qgis-python

if not exist "%KERNEL_DIR%" (
    mkdir "%KERNEL_DIR%"
)

REM Replace backslashes with escaped backslashes for JSON
set KERNEL_BAT_JSON=%KERNEL_BAT:\=\\%

(
echo {
echo  "argv": [
echo   "cmd.exe",
echo   "/c",
echo   "%KERNEL_BAT_JSON%",
echo   "{connection_file}"
echo  ],
echo  "display_name": "QGIS Python",
echo  "language": "python",
echo  "metadata": {
echo   "debugger": true
echo  },
echo  "kernel_protocol_version": "5.5"
echo }
) > "%KERNEL_DIR%\kernel.json"

echo    Created: %KERNEL_DIR%\kernel.json
echo.

REM Update notebook initialization cell guide
echo [5/5] Updating notebook template...
set PROJECT_ROOT=%CD%
set PROJECT_ROOT_ESCAPED=%PROJECT_ROOT:\=\\%

(
echo # In your notebook initialization cell, use these paths:
echo import os
echo project_root = r'%PROJECT_ROOT%'
echo os.environ['OSGEO4W_ROOT'] = r'%OSGEO4W_ROOT%'
echo # ... rest of initialization
) > "%KERNEL_DIR%\notebook_template.txt"

REM Verify installation
echo ============================================================================
echo Verifying installation...
echo ============================================================================
echo.

call "%OSGEO4W_ROOT%\bin\python-qgis.bat" -m jupyter kernelspec list
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Could not list Jupyter kernels.
    echo.
)

echo.
echo ============================================================================ 
echo Installation complete! 
echo ============================================================================ 
echo.
echo Detected paths from settings.json:
echo   OSGeo4W Root: [%OSGEO4W_ROOT%]
echo   Project Root: [%PROJECT_ROOT%]
echo.
echo Next steps:
echo   1. Restart VS Code
echo   2. Open a .ipynb file in the demos/ folder
echo   3. Select "QGIS Python" kernel from the kernel selector
echo   4. In the initialization cell, update paths:
echo      - project_root = r^'%PROJECT_ROOT%^'
echo      - os.environ['OSGEO4W_ROOT'] = r^'%OSGEO4W_ROOT%^'
echo.
echo See docs\jupyter_setup.md for full documentation.
echo.
pause
