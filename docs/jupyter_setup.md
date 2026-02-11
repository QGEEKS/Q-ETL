# QGIS ETL Jupyter Notebook Setup Guide

This guide shows how to set up Jupyter Notebook support for the Q-ETL project in VS Code.

## Prerequisites

- OSGeo4W installation with QGIS (default: `C:\OSGeo4W`)
- VS Code with Jupyter extension installed
- Q-ETL project cloned

## Quick Start - Automatic Installation

Run the following command in a PowerShell terminal from the project root:

```powershell
.\setup_jupyter.cmd
```

This script will:
1. **Read QGIS paths from `settings.json`** - No manual path editing needed!
2. Install required Python packages (ipykernel, jupyter, coloredlogs)
3. Create QGIS Jupyter kernel batch file with correct paths
4. Register the kernel in Jupyter
5. Generate a notebook template with your specific paths
6. Verify the installation

**After the script completes:**
- Restart VS Code to detect the new kernel
- Open a notebook (e.g., `demos/development_notebook.ipynb`)
- Select "QGIS Python" kernel from the kernel selector
- Check the paths shown at the end of the script output and update your initialization cell if needed
- The script creates `%APPDATA%\jupyter\kernels\qgis-python\notebook_template.txt` with your specific paths

## Manual Installation

If you prefer to set it up manually, follow these steps:

### Step 1: Install Python Packages

Open a terminal and run:

```cmd
C:\OSGeo4W\bin\python-qgis.bat -m pip install ipykernel jupyter coloredlogs
```

### Step 2: Create QGIS Kernel Batch File

Create the file `C:\OSGeo4W\bin\qgis-kernel.bat` with the following content:

```bat
@echo off
call "%~dp0o4w_env.bat"
@echo off
path %OSGEO4W_ROOT%\apps\qgis\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis
set GDAL_FILENAME_IS_UTF8=YES
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis\python;%PYTHONPATH%
python -m ipykernel_launcher -f %1
```

### Step 3: Register the Kernel

Create the folder and kernel.json:

```cmd
mkdir "%APPDATA%\jupyter\kernels\qgis-python"
```

Create the file `%APPDATA%\jupyter\kernels\qgis-python\kernel.json` with:

```json
{
 "argv": [
  "cmd.exe",
  "/c",
  "C:\\OSGeo4W\\bin\\qgis-kernel.bat",
  "{connection_file}"
 ],
 "display_name": "QGIS Python",
 "language": "python",
 "metadata": {
  "debugger": true
 },
 "kernel_protocol_version": "5.5"
}
```

### Step 4: Restart VS Code

Close and restart VS Code to load the new kernel.

## Using Jupyter Notebooks with Q-ETL

### Open a Notebook

1. Open VS Code in the project folder
2. Open or create a `.ipynb` file (e.g., `demos/development_notebook.ipynb`)
3. Click the kernel selector at the top right
4. Select **"QGIS Python"** from the list

### Initialize QGIS in Notebook

In the first code cell, initialize the QGIS environment:

```python
import os
import sys

# Change to project root directory
project_root = r'C:\App\Github\QGIS_ETL'  # Adjust to your path
os.chdir(project_root)

# Set sys.argv[0] (so get_config() finds settings.json)
sys.argv[0] = os.path.join(project_root, 'python', 'dummy.py')

# Add project Python folder to sys.path
sys.path.insert(0, os.path.join(project_root, 'python'))

# Import Q-ETL (QGIS initializes automatically in core/__init__.py)
from core import *
from engine import *

print(f"✓ QGIS initialized (version {qgs.applicationVersion()})")
print(f"✓ Working directory: {os.getcwd()}")
```

**Important:** 
- QGIS initialization happens automatically when importing `core` (see `python/core/__init__.py`)
- Environment variables are already set by `qgis-kernel.bat`
- You only need to set up paths and import the modules!

### Import Q-ETL Modules

After initialization, you can import Q-ETL modules:

```python
from core import *
from engine import *

# Create aliases for ETL components
reader = Input_Reader
worker = Worker
output = Output_Writer
constructor = Constructor
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'ipykernel'"

**Solution:** Install ipykernel in the QGIS Python environment:
```cmd
C:\OSGeo4W\bin\python-qgis.bat -m pip install ipykernel jupyter
```

### Problem: Kernel keeps "spinning" and never starts

**Solution:** 
1. Check that you have selected the **"QGIS Python"** kernel (not "Python 3")
2. Check the VS Code Output panel (Ctrl+Shift+U) under "Jupyter" for error messages
3. Try reloading the VS Code window (`Ctrl+Shift+P` > "Developer: Reload Window")

### Problem: "FileNotFoundError: settings.json"

**Solution:** Make sure to run the initialization cell that sets `os.chdir()` and `sys.argv[0]` correctly.

### Problem: QGIS Python kernel not found in list

**Solution:**
1. Verify that `kernel.json` exists: `%APPDATA%\jupyter\kernels\qgis-python\kernel.json`
2. Run: `jupyter kernelspec list` to see all registered kernels
3. Restart VS Code

## Customization for Other Installations

If your QGIS/OSGeo4W installation is in a different location than `C:\OSGeo4W`, you need to edit:

1. In `qgis-kernel.bat`: First line should point to the correct `o4w_env.bat`
2. In `kernel.json`: Fix the path to `qgis-kernel.bat`
3. In notebook initialization cell: Fix `OSGEO4W_ROOT` and related paths

## Example Notebooks

See `demos/development_notebook.ipynb` for a complete example of how to use Q-ETL in Jupyter.

## Support

For issues, also see:
- Q-ETL main documentation: `README.md`
- QGIS installation guide: `docs/getting_started.md`
