### Imports
# from Nazar Khalid
import os
import urllib.request
from bs4 import BeautifulSoup
import gzip
import shutil

### PART I: Downloading rainfall files from the CHIRPS website

# Define the base URL
 base_url = 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_dekad/tifs/'

# Define the directory to store the data
data_dir = '/Users/nazar/Downloads/rainfall_data'

# Create the directory if it doesn't exist
 if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Get the HTML content of the directory
 response = urllib.request.urlopen(base_url)
     soup = BeautifulSoup(response, 'html.parser')

# Loop over the links in the HTML content
 for link in soup.find_all('a'):
    # Get the href attribute of the link
    href = link.get('href')

    # If the href attribute is a compressed GeoTIFF file, download it
    if href.endswith('.tif.gz'):
        # Get the URL of the compressed GeoTIFF file
        url = base_url + href

        # Download the compressed GeoTIFF file
           urllib.request.urlretrieve(url, os.path.join(data_dir, href))

### PART II: Automating the extraction

# Define the directories
 source_dir = '/Users/nazar/Downloads/rainfall_data/rainfall_1990_2012'
    target_dir = '/Users/nazar/Dropbox/Courses/Fall2023/Spatial Data Analysis/practice/rainfall'

# Create the target directory if it doesn't exist
 if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# Loop over the files in the source directory
 for filename in os.listdir(source_dir):
    # If the file is a compressed GeoTIFF file, extract it
    if filename.endswith('.tif.gz'):
        # Define the full paths to the source and target files
        source_file = os.path.join(source_dir, filename)
           target_file = os.path.join(target_dir, filename[:-3])  # remove the .gz extension

        # Open the compressed file, extract the GeoTIFF file, and save it to the target directory
        with gzip.open(source_file, 'rb') as f_in:
            with open(target_file, 'wb') as f_out:
                   shutil.copyfileobj(f_in, f_out)