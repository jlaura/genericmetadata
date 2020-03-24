# genericmetadata

This is a super lightweight metadata generation toolkit composed of two
scripts:

- `process.py`: Processes a PDS file and outputs an ISIS cube that has a
  footprint and a caminfo pvl file.

```bash
usage: process.py [-h] inputfile recipe

Metadata Processing Engine

positional arguments:
  inputfile   The PATH to the PDS file to be processed
  recipe      The PATH to the recipe file that defines the processing steps

optional arguments:
  -h, --help  show this help message and exit
(metadataengine) -bash-4.2$
```

- `generate_metadata.py`: Processes the generated ISIS cube file and the sensor
  (camstats) PVL output into a JSON metadata file.

```bash
usage: generate_metadata.py [-h] inputfile caminfopvl

Metadata Processing Engine

positional arguments:
  inputfile   The PATH to the ISIS cube file.
  caminfopvl  The PATH to the caminfo pvl file.

optional arguments:
  -h, --help  show this help message and exit
``` 


