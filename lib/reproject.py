#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

import numpy as np
import shutil
import rasterio
import time
from rasterio import transform
from rasterio.warp import reproject, Resampling, calculate_default_transform

def reproject_raster (tif_in, tif_out, epsg='EPSG:54009'):

    start = time.process_time()
    print('Reprojecting...')

    with rasterio.open(tif_in, 'r') as raster:
        t = raster.transform
        rc = raster.count
        crs = raster.crs

        print(raster.crs)

        epsg_origin = raster.crs

        if epsg_origin != 'EPSG:54009' \
                          '':
            print ('The CRS is: ' , epsg_origin, 'the file will be reprojected to ', epsg)
            transform, width, height = calculate_default_transform(
                raster.crs, epsg, raster.width, raster.height, *raster.bounds)
            kwargs = raster.meta.copy()
            kwargs.update({
                'crs': epsg,
                'transform': transform,
                'width': width,
                'height': height
            })
            with rasterio.open (tif_out, 'w', **kwargs) as dst:
                for i in range(1, raster.count +1):
                    reproject(
                        source=rasterio.band(raster, 1),
                        destination=rasterio.band(dst, i),
                        src_transform=raster.transform,
                        src_crs=raster.crs,
                        dst_transform=transform,
                        dst_crs=epsg
                    )

        else:
            print ('No reprojection needed')

        el_time = (time.process_time() - start)
        elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time / 60), el_time % 60)
        print(elapsed_time)

#eg call
# dst_crs = 'EPSG:54009'
# output = os.getcwd() + '/process'
# tiff_in = os.path.join(output,'LC_original_reclassified_.tif')
# tiff_out = os.path.join(output,'LC_original_reprojected_.tif')
#
# reproject_raster (tiff_in, tiff_out, epsg='EPSG:54009')