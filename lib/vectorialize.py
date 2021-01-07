import argparse
import logging
import subprocess
import sys
import os

import fiona
import rasterio
from rasterio.features import shapes
import time

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger('rasterio_polygonize')

def main(raster_file, vector_file, driver, mask_value):

    start = time.process_time()
    print('Vectorializing...')

    with rasterio.Env():

        with rasterio.open(raster_file) as src:
            image = src.read(1)

        if mask_value is not None:
            mask = image == mask_value
        else:
            mask = None

        results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v)
            in enumerate(
                shapes(image, mask=mask, transform=src.transform)))


        crs_epsg = src.crs.to_epsg()

        if crs_epsg == None:
            crs_str = src.crs.to_string()
            #print (crs_str)
            if 'World_Mollweide' in crs_str:
                 epsg_crs = 'EPSG:54009'
            #elif 'other not recognized epsg' in crs_str:
            #   epsg_crs = 'EPSG:xxxx'
            else:
                print ('CRS not defined or available.')
                return 'Error'

        with fiona.open(
                vector_file, 'w',
                driver=driver,
                crs=crs_epsg,
                schema={'properties': [('raster_val', 'int')],
                        'geometry': 'Polygon'}) as dst:
            dst.writerecords(results)

        el_time = (time.process_time() - start)
        elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time / 60), el_time % 60)
        print(elapsed_time)

        print ('Vector data generated: ' + dst.name)
        return dst.name


#EG.
output = 'D:/Python_projects/git/convergence/output/'
raster_file = os.path.join(output, 'LC_original_reprojected_.tif')
mask_value = 2 #None
vector_file = os.path.join(output, 'LC_vector3.shp')
driver = 'ESRI Shapefile'

pol = main(raster_file, vector_file, driver, mask_value)