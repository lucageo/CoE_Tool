#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import rasterio
import time
import numpy as np


start = time.process_time()
print('Starting raster sum...')

path = os.getcwd() + '/indicator/'

indicator = []
for r, d, f in os.walk(path):
    for file in f:
        if '.tif' in file:
            indicator.append(os.path.join(r, file))

for f in indicator:
    print(f)

# initializate var sum as none to be checked later if still none then no sum calculated
sum = None

with rasterio.open(indicator[0]) as src:
    #sum = np.zeros[src.shape]
    out_meta = src.meta.copy()

    sum = src.read()
    print(sum.shape)
    print(np.sum(sum))

for raster_path in indicator[1:]:
    with rasterio.open(raster_path) as src:
        sum += src.read()
        print(np.sum(sum))

out_meta.update({"driver": "GTiff",
                 "dtype":rasterio.uint8,
                 "count": 1,
                 "compress": 'lzw',
                 "BIGTIFF": "IF_SAFER"
                 })

with rasterio.open('convergence.tif', "w", **out_meta) as summed:
    summed.write(sum)

    print("convergence computed")


el_time = (time.process_time() - start)
elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time/60), el_time % 60)
print(elapsed_time)
