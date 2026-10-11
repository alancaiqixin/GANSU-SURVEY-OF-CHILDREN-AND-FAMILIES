# a py script for downloading UTCI from ERA5-HEAT
# data in hourly structure
import os
import cdsapi
import urllib.request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from netCDF4 import Dataset, date2num, num2date
from zipfile import ZipFile

#######################################################################################################
# A. Folders

# where to store data
spt_root = 'C:/Users/Kaifs/OneDrive/Documents/dropbox_penn/GitHub/ClimateDataIntro'

# pick year 
year = '2023' 

# pick date
ar_days = ['12', '13', '14','15'] 

# pick region, corresponds to Northest latitude, Westest longitude, Southest latitude, East longitude.
# Longitude: West(-), East(+); Latitude:South(-), North(+)
ar_coordiantes_area = [41, -76, 39, -74] 

# pick months
for month in range(2, 4): #stop at second number (month) minus 1
    # Format month as two-digit string with leading zeros
    formatted_month = f"{month:02d}"
    
    # Data retrieval for the current month
    c = cdsapi.Client()
    res = c.retrieve(
        'derived-utci-historical',
        {
            'product_type': 'consolidated_dataset',
            'variable': 'universal_thermal_climate_index', # pick variables
            'version': '1_1',
            'year': year,
            'month': formatted_month,
            'day': ar_days,
            'area': ar_coordiantes_area,
            'grid': [0.25, 0.25],
            'format': 'zip',
        },
        f'C:/Users/Kaifs/OneDrive/Documents/dropbox_penn/Dropbox/GitHub/ClimateDataIntro/utci_philly/{year}_{formatted_month}_utci.zip'
    )
    
    # Show progress
    print(f'Downloaded data for {year}-{formatted_month}')

# End of loop
print('Data download complete!')

