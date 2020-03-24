import argparse
import json
import os

# This is epic jank - don't do this - use ENV variables
os.environ["ISISROOT"] = "/usgs/cpkgs/anaconda3_linux/envs/isis3.9.0"
os.environ["ISIS3DATA"] = "/usgs/cpkgs/isis3/data"

from jinja2 import Template
from pysis import isis
from pysis.exceptions import ProcessError


def parse_args():
    parser = argparse.ArgumentParser(description='Metadata Processing Engine')
    parser.add_argument('inputfile', help='The PATH to the PDS file to be processed')
    parser.add_argument('recipe', help='The PATH to the recipe file that defines the processing steps')
    return parser.parse_args()

class Recipe():
    """
    A thin wrapper that renders a Jinja2 template and then
    runs the recipe using ISIS.

    """
    def __init__(self, definition_file):
        """
        Parameters
        ----------
        definition_file : str
                          PATH to a jinja template containing an ISIS 
                          processing pipeline
        """
        if not os.path.exists(definition_file):
            raise FileNotFoundError(f'File {definition_file} does not exist.')
        with open(definition_file, 'r') as df:
            
            self.recipe = Template(df.read())

    def render(self, **kwargs):
        """
        Renders the recipe to a JSON string and then loads it.
        """
        self.rendered = json.loads(self.recipe.render(**kwargs))

    def process(self):
        """
        Iterate over the rendered recipe and perform each processing
        step. Now that python dics are ordered, we have no worries on 
        iterating naively.
        """
        for func, kwargs in self.rendered.items():
            # Get the func from the pysis.isis namespace
            func = getattr(isis, func)

            try:
                func(**kwargs)
            except ProcessError as e:
                print(e)

def main(args):
    if not os.path.exists(args.inputfile):
        raise FileNotFoundError(f'File {args.inputfile} does not exist.')

    # Setup all the paths for reading/writing
    # naive now - output in one dir.
    basename = os.path.basename(args.inputfile)
    filename = os.path.splitext(basename)[0]
    
    file_isis = f'{filename}.cub'
    file_caminfo = f'{filename}_caminfo.pvl'

    # Instantiate the recipe, render, and process
    recipe = Recipe(args.recipe)

    recipe.render(pds_file=args.inputfile, 
                  isis_file=file_isis,
                  caminfo_pvl=file_caminfo)
    
    recipe.process()

if __name__ == '__main__':
    main(parse_args())
