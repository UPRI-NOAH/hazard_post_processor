from distutils.command.upload import upload
import os

import geopandas as gpd

import logging

import time

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import io


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

gauth = GoogleAuth()

gauth.LoadCredentialsFile("mycreds.txt")

if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()

# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)  

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
    haz_cols = ["Var", "VAR", "SS", "GRIDCODE", "LH"]

    for file in shp_files:
        # Gets only the name of the shapefile, will be used as the new filename
        
        hazard_name = file.replace(".shp", "")

        # Reads the file and dissolves it by hazard attributes
        full_file_path = os.path.join(input_path, file)
        logging.info(f"reading {hazard_name}")
        read_haz = gpd.read_file(full_file_path)

        for haz in haz_cols:
            if haz in read_haz:
                logging.info(f"start dissolving for {hazard_name}")
                read_haz = read_haz.dissolve(by=haz)
                break
        else:
            logging.info(f"no haz col found, skipping dissolving for {hazard_name}")
            continue

        # Saves the dissolved file to a new file inside the output folder
        read_haz.to_file(
            os.path.abspath(os.path.join(output_path, hazard_name + "_diss.shp"))
        )

        logging.info(f"done dissolving for {hazard_name}")

        gdrive_upload()

        # Sleep for 6 hours then continue upload
        time.sleep(21600)

def gdrive_upload():
    
    for file in os.listdir(output_path):
        gfile = drive.CreateFile({'parents': [{'id': '1o4qeuNEv3sW1Ged0jLecUqDWmUwqhaOt'}]})
        gfile['title'] = file
        gfile.SetContentFile(os.path.join(output_path,file))
        gfile.Upload() # Upload the file.
        logging.info(f"file {file} uploaded")

        os.remove(os.path.join(output_path, file))
        logging.info(f"file {file} deleted in output folder")
        


if __name__ == "__main__":
    # Path to directories
    path_to_dir = os.path.dirname(os.path.abspath("__file__"))
    input_path = os.path.join(path_to_dir, "input")
    output_path = os.path.join(path_to_dir, "output")
    make_output_folders(output_path)
    input_files = os.listdir(input_path)
    output_files = os.listdir(output_path)

    # Gets only the .shp
    shp_files = [file for file in input_files if file.endswith(".shp")]
    shp_out_files = [file for file in output_files if file.endswith(".shp")]
    output_files = [file for file in output_files]

    # Runs the post processor function
    post_processor(output_path)
