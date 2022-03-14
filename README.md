# Dissolving of NOAH Hazard Maps

This document contains the workflow for dissolving the hazard maps of the UPRI - NOAH Center. Dissolve is a spatial process in which a map feature is a created by merging features that have a common value for a specified attribute. This is done to compress the file size of the hazard maps so we can efficiently process the data and display it on the NOAH website.

## Dependencies
- Python 3.9

## Installation
> pip install -r requirements.txt

> pipenv install # install dependencies

> pipenv shell # run environment

> pre-commit install # install pre-commit

## Data Requirements
To be able to run the script, you need to prepare the hazard maps (in `.shp` format). The hazard maps must contain the specific hazard field attribute:
1. Flood Hazard - `VAR` or `Var`

2. Storm Surge - `SS`

3. Landslide Hazard - `LH`

4. Unstable Slopes - `GRIDCODE`

## Folder Configuration
The python script is modeled to read multiple input files and produce output files in a structured format. Hence, you need to follow the steps below.

1. Download the python script from this repository.
2. On your machine, identify where you will place the python script and the input files (data required). All of these data must be stored on your base folder path.

    e.g. `/Users/localUser/UPRI/HazardDissolver`

3. Insider this base folder path, create an `input` folder and input the following hazard maps inside the `input` folder:
    - `input`
        - `Province 1.shp`
        - `Province 2.shp`
        - `Province 3.shp`

All output files will be stored inside the `output` folder. This folder is automatically generated from the script.

## Data Processing
The data processing of the hazard maps are the following:
1. The script reads each hazard map inside the `input` folder.

2. The script scans the field attributes of the hazard map to ensure that it contains the required hazard field attribute (See Data Requirements for the list of acceptable hazard field attributes).

3. Once any of the observed variant of hazard attribute is found, it dissolves the hazard field attribute.

4. The dissolved hazard map is saved to the `output` folder and will be upload to the designated google drive. The files in `output` folder will be deleted afterwards.
