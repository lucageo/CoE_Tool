#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import rasterio
from rasterio.merge import merge
import time

def merge_raster(input_folder,resolution,merged_out_path):

    start = time.process_time()
    print('Start merging tiles...')


    tiles_path = [ os.path.join(input_folder, f) for f in os.listdir(input_folder) if os.path.splitext(f)[-1] == '.tif' ]
    input_tiles = [rasterio.open(f) for f in tiles_path]
    
    dest, output_transform = rasterio.merge.merge(input_tiles, bounds=None, res=resolution, nodata=0, precision=7, indexes=None)
    
    with rasterio.open(tiles_path[0]) as src:
        out_meta = src.meta.copy()
    
    out_meta.update({"driver": "GTiff",
                     "height": dest.shape[1],
                     "width": dest.shape[2],
                     "transform": output_transform,
                     "dtype":rasterio.uint8,
                     "count": 1,
                     "compress": 'lzw',
                     "BIGTIFF": "IF_SAFER"
                     })
    
    # out_meta.update(
    #         dtype=rasterio.uint8,
    #         count=1,
    #         compress='lzw',
    #         BIGTIFF="IF_SAFER")
    
    
    with rasterio.open(merged_out_path, "w", **out_meta) as dest1:
        dest1.write(dest)
        print("merged")
    
    
    el_time = (time.process_time() - start)
    elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time/60), el_time % 60)
    print(elapsed_time)

### example ###
# input_folder = os.getcwd() + '/indicator_median/'
# # resolution=250
# # merged_out_path="merged_builtup.tif"
# #
# # merge_raster(input_folder, resolution, merged_out_path)
