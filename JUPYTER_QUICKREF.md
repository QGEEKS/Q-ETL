# Jupyter Notebooks Quick Reference

## Where are the files located?

### Kernel Batch File
- **Location:** `C:\OSGeo4W\bin\qgis-kernel.bat`
- **Purpose:** Starts Python with QGIS environment variables for Jupyter
- **Template:** `templates/qgis-kernel.bat`

### Kernel JSON Configuration
- **Location:** `%APPDATA%\jupyter\kernels\qgis-python\kernel.json`
- **Full path:** `C:\Users\[USERNAME]\AppData\Roaming\jupyter\kernels\qgis-python\kernel.json`
- **Purpose:** Tells Jupyter how to start the QGIS Python kernel
- **Template:** `templates/kernel.json`

## What do the files do?

### qgis-kernel.bat
1. Calls `o4w_env.bat` which sets up the OSGeo4W environment (PATH, root folder, etc.)
2. Adds QGIS bin folder to PATH
3. Sets QGIS environment variables (PREFIX_PATH, PLUGIN_PATH, PYTHONPATH, etc.)
4. Starts Python Jupyter kernel with all variables set correctly

### kernel.json
Defines how Jupyter should start the kernel:
- Uses `cmd.exe` to run the batch file
- Sends connection file to the kernel
- Gives the kernel the display name "QGIS Python"

## Installation

### Quick Installation (Recommended)
```cmd
setup_jupyter.cmd
```

**What it does:**
- Automatically reads QGIS paths from `settings.json`
- Installs required packages (ipykernel, jupyter, coloredlogs)
- Creates `qgis-kernel.bat` with correct paths
- Registers the "QGIS Python" kernel
- Generates notebook template with your specific paths

**After running:**
1. Restart VS Code
2. Open a `.ipynb` file
3. Select "QGIS Python" kernel
4. Check paths shown by the script and update your initialization cell

### Manual Installation
See `docs/jupyter_setup.md` for detailed manual installation guide.

## Usage in Notebook

### Minimal Initialization
```python
import os, sys

project_root = r'C:\PATH\TO\QGIS_ETL' ## Change your path here
os.chdir(project_root)
sys.argv[0] = os.path.join(project_root, 'python', 'dummy.py')
sys.path.insert(0, os.path.join(project_root, 'python'))

# Import Q-ETL (QGIS initializes automatically in core/__init__.py)
from core import *
from engine import *
```

**Note:** 
- QGIS initialization happens automatically when importing `core`
- Environment variables are already set by `qgis-kernel.bat`
- Only need to configure paths and import modules!

## Verify Installation

### Check if kernel is registered
```cmd
jupyter kernelspec list
```

You should see:
```
qgis-python    C:\Users\[USER]\AppData\Roaming\jupyter\kernels\qgis-python
```

### Test if packages are installed
```cmd
C:\OSGeo4W\bin\python-qgis.bat -m pip list | findstr "ipykernel jupyter coloredlogs"
```

## Troubleshooting

### Kernel doesn't start
1. Check VS Code Output > Jupyter for errors
2. Verify batch file exists: `OSGeo4W\bin\qgis-kernel.bat` 
3. Verify kernel.json exists in `%APPDATA%\jupyter\kernels\qgis-python\`
4. Restart VS Code

### ModuleNotFoundError
Install missing package:
```cmd
C:\OSGeo4W\bin\python-qgis.bat -m pip install [PACKAGE_NAME]
```

### Incorrect QGIS installation path
Edit paths in:
1. `qgis-kernel.bat` - first line
2. `kernel.json` - argv[2]
3. Notebook initialization cell

## Customization for Different Setups

### If OSGeo4W is installed in D:\OSGeo4W

**In qgis-kernel.bat:**
```bat
call "D:\OSGeo4W\bin\o4w_env.bat"
```

**In kernel.json:**
```json
"argv": [
  "cmd.exe",
  "/c",
  "D:\\OSGeo4W\\bin\\qgis-kernel.bat",
  "{connection_file}"
]
```

### If project is located elsewhere

Edit in notebook initialization cell:
```python
project_root = r'D:\My Projects\QGIS_ETL'  # Your path here
```

## Examples

See `demos/` folder for example notebooks:
- `development_notebook.ipynb` - Complete WFS to Geopackage workflow

## Support

- Detailed guide: `docs/jupyter_setup.md`
- Setup script: `setup_jupyter.cmd`
- Templates: `templates/`
