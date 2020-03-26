import argparse
import datetime
import os
import json

# This is epic jank - don't do this - use ENV variables
os.environ["ISISROOT"] = "/usgs/cpkgs/anaconda3_linux/envs/isis3.9.0"
os.environ["ISIS3DATA"] = "/usgs/cpkgs/isis3/data"

import ogr
import pvl
from pysis import isis
from pysis.exceptions import ProcessError

from utils import find_in_dict, CustomJsonEncoder


def parse_args():
    parser = argparse.ArgumentParser(description='Metadata Processing Engine')
    parser.add_argument('inputfile', help='The PATH to the ISIS cube file.')
    parser.add_argument('caminfopvl', help='The PATH to the caminfo pvl file.')
    return parser.parse_args()

def get_footprint(file_isis, label):
    """
    Get the WKT footprint string from an ISIS cube.

    Parameters
    ----------
    file_isis : str
                PATH to the ISIS cube

    label : obj
            A PVL loaded ISIS label. Ideally from the file_isis cube.
    """
    polygon_pvl = find_in_dict(label, 'Polygon')
    start_polygon_byte = find_in_dict(polygon_pvl, 'StartByte')
    num_polygon_bytes = find_in_dict(polygon_pvl, 'Bytes')
    
    with open(file_isis, 'r') as f:
        f.seek(start_polygon_byte - 1)
        poly_wkt = str(f.read(num_polygon_bytes))

    return poly_wkt

def footprint_to_geojson(footprint):
    fp = ogr.CreateGeometryFromWkt(footprint)
    geojson = {"bbox":fp.GetEnvelope(),
               "geometry":fp.ExportToJson()}
    return geojson

def main(args):
    if not os.path.exists(args.inputfile):
        raise FileNotFoundError(f'File {args.inputfile} does not exist.')
    
    if not os.path.exists(args.caminfopvl):
        raise FileNotFoundError(f'File {args.caminfopvl} does not exist.')
        
    
    # Load the metadata from previous processing
    label_isis = pvl.load(args.inputfile)
    sensorinfo = pvl.load(args.caminfopvl)    
    # 'DataFile' metadata in the UPC parlance
    # Handle newline and bytes to str
    serialnumber = isis.getsn(from_=args.inputfile).rstrip().decode()

    # Grab the 'other' metadata
    productid = find_in_dict(label_isis, 'ProductId')
    footprint = get_footprint(args.inputfile, label_isis)
    geojson = footprint_to_geojson(footprint)
    provenance = pvl.load(isis.cathist(from_=args.inputfile))
    
    # Custom pack in python to ensure we get valid JSON.
    metadata = {"productid":productid,
                "serialnumber":serialnumber,
                "label_isis" : label_isis,
                "sensorinfo" : sensorinfo,
                "provenance" : provenance,
                "spatial" : geojson}  # This is here because we want to use ISIS and not GDAL for coords.
                

    # Setup all the paths for reading/writing
    # naive now - output in one dir.
    basename = os.path.basename(args.inputfile)
    filename = os.path.splitext(basename)[0]

    # Write out, handle datetime, profit
    file_metadata = f'{filename}.metadata'
    with open(file_metadata, 'w') as fm:
        json.dump(metadata, fm, cls=CustomJsonEncoder, indent=4)
    
    return

if __name__ == '__main__':
    main(parse_args())
