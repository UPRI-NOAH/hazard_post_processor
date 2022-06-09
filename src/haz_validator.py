import os
import geopandas as gpd
import pandas as pd
from datetime import datetime

def shapefile_validator():
    """
    Validates the shapefiles according to its geometries, attributes, and projections. Returns boolean depending on the parameters set.
    """

    # Initialize empty dataframes
    geom_check = []
    attribute_check = []
    prj_check = []
    diss_check = []

    # Observed variants of hazard attributes
    haz_cols = ['Var', 'VAR', 'SS', 'GRIDCODE', 'LH']

    for shp in shp_files:
        # Gets the geometry of the shapefiles
        geometry = gpd.read_file(shp).geometry

        # Reads the shapefiles
        data = gpd.read_file(shp)

        # Counts the number of rows of the shapefile
        count_rows = len(data.index)

        # This is a parameter for checking the validity of the dissolved hazard maps. From the number of rows, this will return True if the row count is less than or equal to 3
        if count_rows <= 3:
            diss_check.append(True)
        else:
            diss_check.append(False)

        # Checks if the shapefile contains a haz col given the different observed variants of haz columns
        for haz in haz_cols:
            if haz in data:
                attribute_check.append(True)
                break
        else:
            attribute_check.append(False)
        
        # Checks if the shapefile has the correct GCS projection. Returns True when projecection is epsg:4326.
        prj = gpd.read_file(shp).crs
        if prj == 'epsg:4326':
            prj_check.append(True)
        else:
            prj_check.append(False)
        
        # Checks if the shapefile contains geometries. Returns True when it contains geometries.
        geom_series = gpd.GeoSeries(geometry)
        if geom_series.shape[0] > 0:
            geom_check.append(True)
        else:
            geom_check.append(False)

    validator = pd.DataFrame(data=zip(hazard_name, geom_check, attribute_check, prj_check, diss_check),columns=['hazard name', 'contains_geometry', 'correct_attribute', 'GCS_prj', 'diss_check'])
    validator['rows'] = len(data.index)

    # Creates a new column indicating overall validation assessment for each shapefile. When it returns False, it means that the shapefile is invalid and needs to be returned to the hazard team for inspection.
    validator['final_check'] = validator.contains_geometry & validator.correct_attribute & validator.GCS_prj & validator.diss_check
    
    # Saves the dataframe into a csv, with current datetime indicator
    validator.to_csv(f'{datetimenow}_results_validation.csv', index=None, encoding="utf-8")

if __name__ == '__main__':
    # Path to directories
    path_to_dir = os.path.dirname(os.path.abspath('__file__'))
    input_path = os.path.join(path_to_dir, "input")
    input_files = os.listdir(input_path)

    # Gets only the .shp
    shp_files = [ file for file in input_files if file.endswith(".shp") ]

    # Extracts the hazard name (from the filename)
    hazard_name = [ shp.replace(".shp", "") for shp in shp_files ]

    # Gets the current date and time
    datetimenow = datetime.now().strftime("%Y%m%d %H:%M:%S")

    shapefile_validator()