## Manifest

- `prepare_input_files.py`: automatically download and prepare the input files for the force field accuracy
benchmark calculations.
- `docking.py`: module that wraps around OpenEye's FRED to perform docking.
- `mcce.py`: module that wraps around MCCE to identify the most likely protonation state of a protein. This is taken
verbatim from [mmtools](https://github.com/choderalab/mmtools/blob/master/mccetools/mcce.py).
- `rename.py`: utility module for `mcce.py`. This is taken
verbatim from [mmtools](https://github.com/choderalab/mmtools/blob/master/mccetools/rename.py).
