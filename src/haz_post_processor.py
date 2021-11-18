import os

import geopandas as gpd

import logging

from os.path import abspath, dirname

logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")
file_handler = logging.FileHandler(dirname(abspath(__file__)) + "/error.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logging.basicConfig(
    filename="info.log", level=logging.INFO, format="%(asctime)s: %(message)s"
)

def make_output_folders(path):  # Create function to create output folders
    # make folder using path
    """
    Create output folder.
    """
    try:
        os.makedirs(output_path, exist_ok=True)
    except Exception as e:
        print(e)


def post_processor(output_path):
    """
    Performs dissolving of the hazard shapefiles.
    """
    # Observed variants of hazard attributes
    haz_cols = ["Var", "VAR", "SS", "GRIDCODE", "LH", "id"]

    for file in shp_files:
        # Gets only the name of the shapefile, will be used as the new filename
        
        hazard_name = file.replace(".shp", "")

        # Reads the file and dissolves it by hazard attributes
        full_file_path = os.path.join(input_path, file)
        logging.info("reading " + hazard_name)
        read_haz = gpd.read_file(full_file_path)

        for haz in haz_cols:
            if haz in read_haz:
                logging.info("start dissolving for " + hazard_name)
                read_haz = read_haz.dissolve(by=haz)
                break
        else:
            logging.info("no haz col found, skipping dissolving for " + hazard_name)
            continue

        # Saves the dissolved file to a new file inside the output folder
        read_haz.to_file(
            os.path.abspath(os.path.join(output_path, hazard_name + "_diss.shp"))
        )

        logging.info("done dissolving for " + hazard_name)


if __name__ == "__main__":
    # Path to directories
    path_to_dir = os.path.dirname(os.path.abspath("__file__"))
    input_path = os.path.join(path_to_dir, "input")
    output_path = os.path.join(path_to_dir, "output")
    make_output_folders(output_path)
    input_files = os.listdir(input_path)

    # Gets only the .shp
    shp_files = [file for file in input_files if file.endswith(".shp")]

    # Runs the post processor function
    post_processor(output_path)
