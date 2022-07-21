import geopandas as gpd
import pandas as pd
import os
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
import time
import datetime
import logging

from __init__ import get_str
from os.path import abspath, dirname

s3_client = boto3.client(
    "s3",
    region_name=get_str("REGION"),
    aws_access_key_id=get_str("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=get_str("AWS_SECRET_ACCESS_KEY"),
)

logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")
file_handler = logging.FileHandler(dirname(abspath(__file__)) + "/error.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logging.basicConfig(
    filename="info.log", level=logging.INFO, format="%(asctime)s: %(message)s"
)

def geo_intersect():
    start_time = time.time()

    dir_path = os.getcwd()
    store_path = os.path.join(dir_path, "geojson/")
    Path(store_path).mkdir(exist_ok=True, parents=True)

    bldg_req = 'https://upri-noah.s3.ap-southeast-1.amazonaws.com/critical_facilities/bldgs-qc-faci.geojson'
    bldg_df = gpd.read_file(bldg_req)
    bldg_df = bldg_df.to_crs('EPSG:32651')

    # haz_req = 'https://upri-noah.s3.ap-southeast-1.amazonaws.com/test/qc_brgy_fh_100yr.geojson'
    haz_req = 'https://upri-noah.s3.ap-southeast-1.amazonaws.com/critical_facilities/qc_fh_100yr.geojson'
    haz_df = gpd.read_file(haz_req)
    haz_df = haz_df.to_crs('EPSG:32651')

    df_dict = []
    to_df = []
    for index, bldg_row in bldg_df.iterrows():
        p1 = bldg_row.geometry
        store_dict = {}
        geom = []
        store_dict2 = {"Name":'', "Low Hazard":0,"Medium Hazard":0, "High Hazard":0, "All Hazard":0, "geometry": None}

        for index2, haz_row in haz_df.iterrows():
            p2 = haz_row.geometry
            intersect = p1.intersects(p2)
            haz_lvl = haz_row.Var
            if intersect == True:
                poly_intersect = p1.intersection(p2)
                geom.append(poly_intersect)
                area = (p1.intersection(p2).area)
                area = round(area * 100) / 100
                union = gpd.GeoSeries(geom).unary_union
                store_dict2["Name"] = bldg_row.Name_2
                print(area)
                if haz_lvl == 1.0:
                    store_dict2["Low Hazard"] = area
                    store_dict2["geometry"] = union
                elif haz_lvl == 2.0:    
                    store_dict2["Medium Hazard"] = area
                    store_dict2["geometry"] = union

                elif haz_lvl == 3.0:
                    store_dict2["High Hazard"] = area
                    store_dict2["geometry"] = union
                
                store_dict[bldg_row.Name_2] = store_dict2
        if store_dict:
            overall = store_dict[bldg_row.Name_2]['Low Hazard'] + store_dict[bldg_row.Name_2]['Medium Hazard'] + store_dict[bldg_row.Name_2]['High Hazard']
            store_dict[bldg_row.Name_2]['All Hazard'] = overall
            df_dict.append(store_dict[bldg_row.Name_2])
            polygon_geom2 = store_dict[bldg_row.Name_2]['geometry']
            to_df.append(polygon_geom2)
            
    df = pd.DataFrame(df_dict)
    gdf = gpd.GeoDataFrame(df, geometry=to_df)
    gdf = gdf.set_crs("EPSG:32651")
    gdf = gdf.to_crs("EPSG:4326")
    full_path = os.path.join(store_path, "bldg_haz_intersect.geojson")

    gdf.to_file(full_path, driver='GeoJSON')
    end = (time.time() - start_time)

    td = datetime.timedelta(seconds=end)
    logging.info("done processing geojson")
    logging.info('Time in hh:mm:ss:', td)


def s3_upload():
    dir_path = os.getcwd()
    store_path = os.path.join(dir_path, "geojson/")
    for file in os.listdir(store_path):
        full_path = os.path.join(store_path, file)
        if file == "bldg_haz_intersect.geojson":
            try:
                s3_client.upload_file(
                    full_path,
                    "upri-noah",
                    "test/bldg_haz_intersect.geojson",
                    ExtraArgs={"ContentType": "application/json", "ACL": "public-read"},
                )

            except ClientError as e:  # noqa: F841
                return False
    logging.info("done uploading in s3")



if __name__ == "__main__":
    geo_intersect()
    s3_upload()

