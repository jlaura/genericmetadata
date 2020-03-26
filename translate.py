import argparse
import json

from jinja2 import Environment, FileSystemLoader

from utils import find_in_dict, CustomJsonEncoder

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--proj', help='Projection metadata file.')
    parser.add_argument('--image', help='Image metadata file.')
    return parser.parse_args()

def get_start_time(metadata):
    instrument = find_in_dict(metadata, 'Instrument')
    if instrument:
        return find_in_dict(instrument, 'StartTime')

def generate_links():
    return json.dumps([{"rel":i, "href":i} for i in range(3)])

def generate_assets():
    assets = {}
    assets['mock'] = {'href':'url',
                      'title':'fake',
                      'description':'Just a fake asset',
                      'type':'image/tiff; application=geotiff; profile=cloud-optimized'}

    return json.dumps(assets)

def load_proj_properties(payload, file_proj):
    with open(file_proj, 'r') as proj:
        proj_metadata = json.load(proj)
    payload['epsg'] = proj_metadata['projection']['epsg']
    payload['proj4'] = proj_metadata['projection']['proj4']
    payload['wkt2'] = json.dumps(proj_metadata['projection']['wkt2'])

def main(args):
    fs_loader = FileSystemLoader(searchpath="templates")
    template_env = Environment(loader=fs_loader)

    template = template_env.get_template('item.template')
    
   
    with open(args.image, 'r') as image:
        image_metadata = json.load(image)

    # Build the translation dict
    payload = {
            'stac_version':'0.9.0', 
            'productid':image_metadata['productid'],
            'bbox':image_metadata['spatial']['bbox'],
            'geometry':image_metadata['spatial']['geometry'],
            'datetime':get_start_time(image_metadata),
            'links':generate_links(),
            'assets':generate_assets(),
            'properties':{}}
            

    load_proj_properties(payload, args.proj)
    
    print(payload)

    metadata = template.render(**payload)

    print(metadata)

    # Write out, handle datetime, profit
    file_metadata = f'{image_metadata["productid"]}.stac.json'
    with open(file_metadata, 'w') as fm:
        fm.write(metadata)

if __name__ == '__main__':
    main(parse_args())
