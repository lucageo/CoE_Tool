#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import rasterio
import numpy as np
import time

#def reclassify(tif_in, class, tif_out=False):
def reclassify(tif_in, classi, tif_out):
    """Reclassify raster, input: ('mypath.tif',[(downValue,topValue,classValue),(0,10,1),..],'outpath.tif')
-------------
#eg. reclassify usage, 3 input mandatory
#p = reclassify('input_raster.tif','output_raster.tif',[ (1, 10, 1), (11, 20, 2), (21,30,1) ])
"""
    start = time.process_time()
    print('Reclassifing...')
    with rasterio.open(tif_in) as src:
        # Read as numpy array
        array = src.read()
        profile = src.profile

        # Reclassify
        for c in classi:
            array[np.where((array >= c[0]) & (array <= c[1]))] = c[2]

        # if not tif_out:
        #     #..save to memory data and return memory data obj for next step TODO
        #     return "to do!"
        # else:
        #     with rasterio.open(tif_out, 'w', **profile) as dst:
        #         # Write to disk
        #         dst.write(array)
        #     return "Raster reclissified to " + tif_out + " file."

        with rasterio.open(tif_out, 'w', **profile) as dst:
            # Write to disk
            dst.write(array)
            print("Raster reclissified to " + tif_out + " file.")

        el_time = (time.process_time() - start)
        elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time/60), el_time % 60)
        print(elapsed_time)

#eg. reclassify usage, 3 input mandatory
#p = reclassify('input_raster.tif','output_raster.tif',[ (1, 10, 1), (11, 20, 2), (21,30,1) ])
