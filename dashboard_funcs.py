import pooch
from pooch import Unzip
import yaml
import xarray as xr
import hvplot.xarray
import holoviews as hv
import glob
import os

# Set up the pooch file fetching all the files from Zenodo
CSE_pooch = pooch.create(base_url = "doi:10.5281/zenodo.8134869/",
                         path = pooch.os_cache("CSE"),
                         registry = {"land.zip": "85b5baf3fef43605e1a367475bea4c11c10de30fe429d7bcc78ad06615d1d5d1",
                                     "temperature.zip": "33362b67823cc6b9e510fda03555f3cc6c968c41760a7378ef6939331dabdc6a",
                                     "precipitation.zip": "f24f38e2d32f7ec3337b15b5186b90c127a903e1f0441de0a87f1d31ef9344b1",
                                     "hydrology.zip": "555e14b7a378d356cab4c3c4f550ac3cdc1c0b40786b69ffa6793fc5913fac77",
                                     "energy.zip": "9dd901b6981365dbf02beaf023c9e0cb3cc13f61d244bd10e92e605cc9193eb9",
                                     "air_pollution.zip": "ba208c2b057250f3741bbb3b89d9ff257e66230383542622d99107ade02a015d",
                                     },
                        )

def get_info():
    '''
    Read information from the yaml file into a dictionary.
    '''
    with open('indicator_info.yml', 'r') as f:
            return yaml.full_load(f)

def get_all_files():
    '''
    Download and cache all the files from Zenodo.
    '''
    all_folders = ['precipitation.zip', 'temperature.zip', 'energy.zip', 'hydrology.zip', 'air_pollution.zip', 'land.zip']
    for folder in all_folders:
        CSE_pooch.fetch(folder, processor = Unzip())

def make_ds(type,
            ind, 
            vars = ['abs', 'diff', 'score']
            ):
    ''' 
    Make a dataset of the given indicator.    
    '''
    
    files = dfs.CSE_pooch.fetch(type + '.zip', 
                processor = Unzip())
    fp = os.path.dirname(files[1])
    ds = xr.merge([xr.concat([xr.open_dataarray(f).rename(f'{ind}_{var}')
                              for f in glob.glob(fp + fr'\{ind}*{var}.nc4')], dim='threshold') for var in vars])
    return ds