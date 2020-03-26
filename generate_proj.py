import argparse
import json
import os

import gdal

from utils import CustomJsonEncoder

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', help='The inpit file to extract the projection')
    
    return parser.parse_args()

def get_srs(data):
    srs = data.GetSpatialRef()
    
    proj = {'projection': {'proj4':srs.ExportToProj4(),
                          'wkt2':srs.ExportToWkt(),
                          'epsg':srs.AutoIdentifyEPSG()}
            }
    return proj

def main(args):
    if not os.path.exists(args.inputfile):
        raise FileNotFoundError(f'File {args.inputfile} does not exist.')

    data = gdal.Open(args.inputfile)
    proj = get_srs(data)

    # Setup all the paths for reading/writing
    # naive now - output in one dir.
    basename = os.path.basename(args.inputfile)
    filename = os.path.splitext(basename)[0]

    # Write out, handle datetime, profit
    file_metadata = f'{filename}.proj.metadata'
    with open(file_metadata, 'w') as fm:
        json.dump(proj, fm, cls=CustomJsonEncoder, indent=4)

    

if __name__ == '__main__':
    main(parse_args())
