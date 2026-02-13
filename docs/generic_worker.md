## Guide: Using ProcessingRunner

The `ProcessingRunner` method is a generic utility for running QGIS processing algorithms in Q-ETL worflows. It is part of the `Worker.Generic` class and is designed to simplify the execution of QGIS algorithms by handling progress feedback and logging automatically.

### How to Use

1. **Import the Worker class:**
	Ensure you have imported the `Worker` class from your project.

2. **Get the code from QGIS**
    When you want to use a tool from the QGIS Processing toolbox, that has not been ported to Q-ETL, you can fill in the dialog en QGIS, and have the code that you need be generated for you.

    Open the tool you want, and fill in the dialog:

    <img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/images/quickstart/generic_dialog.png" width="75%" height="50%"> 

    When you have choosen your parameters, select **Export to Python Script**

    <img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/images/quickstart/generic_copy.png" width="75%" height="50%"> 

    If you paste the code into a text editor, you can see the parameters you have selected :

    <img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/images/quickstart/generic_code.png" width="75%" height="50%"> 

3. **Parameters:**
	- `algName` (str): The QGIS algorithm ID (e.g., 'native:buffer').
	- `parameters` (dict): The parameters required by the algorithm. Refer to QGIS documentation for details.

4. **Call ProcessingRunner:**
	Use the method by specifying the algorithm name and a dictionary of parameters.

    You call the worker, at put in your python script - adjusting for input layers to amatch your Q-ETL variables:

    <img src="https://github.com/QGEEKS/Q-ETL/raw/ressources/images/quickstart/generic_usage.png" width="75%" height="50%"> 

4. **Output:**
	The method returns the output layer produced by the algorithm.

### Notes
- The method handles progress bar updates and logging automatically.
- Errors are logged and will terminate the script if encountered.


### Typical Use Cases

This is used, if a tool has not been portet to Q-ETL. Then you can use this tool, to run it anyways. 


