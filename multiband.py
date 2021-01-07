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

# Read metadata of first file
with rasterio.open(indicator[0]) as src0:
    meta = src0.meta

# Update meta to reflect the number of layers
meta.update(count = len(indicator))

meta.update({"driver": "GTiff",
                 "dtype":rasterio.uint8,
                 "compress": 'lzw',
                 "BIGTIFF": "IF_SAFER"
                 })

# Read each layer and write it to stack
with rasterio.open('stack.tif', 'w', **meta) as dst:
    for id, layer in enumerate(indicator, start=1):
        with rasterio.open(layer) as src1:
            dst.write(src1.read(1), id)

    print("convergence computed")


el_time = (time.process_time() - start)
elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time/60), el_time % 60)
print(elapsed_time)
