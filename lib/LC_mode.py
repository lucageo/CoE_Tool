# coding: utf-8

import os

import rasterio
import rasterio.warp
import rasterio.features
from rasterio.enums import Resampling
from rasterio import Affine, MemoryFile
import time

def resample_raster(filepath, scale=250, res_type=Resampling.mode, out_tif=False):
    """Resample raster, input: ('/folder/tifpath.tif',scale=3,out='/folder/outpath.tif',res_type=Resampling.<method>)

default scale = 3 if not assigned
default outfile = 'out.tif' 
default res_type = Resampling.mode
--------------
# Eg.          
#r = resample_raster('LC_rec_padova.tif', scale=2,out_tif='s2_mode.tif',res_type=Resampling.mode)
#r = resample_raster('LC_rec_padova.tif', scale=3,out_tif='s3_mode.tif',res_type=Resampling.mode)    
"""    
    start = time.process_time()
    print('Computing mode...')

    with rasterio.open(filepath, 'r') as raster:
        t = raster.transform
        rc = raster.count
        crs = raster.crs


        #Check Pixel Size
        pixelSizeX = t[0]
        pixelSizeY = -t[4]
        print("Pixel Size: ", pixelSizeX, " x ", pixelSizeY)

        scale_f = float(scale / float(pixelSizeX))
        scale_fy = float(scale / float(pixelSizeY))

        # rescale the metadata
        transform = Affine(t.a * scale_f, t.b, t.c, t.d, t.e * scale_fy, t.f)
        height = int(raster.height / scale_fy)
        width = int(raster.width / scale_f)

        profile = raster.profile
        profile.update(transform=transform, driver='GTiff', height=height, width=width)

        data = raster.read( # Note changed order of indexes, arrays are band, row, col order not row, col, band
                out_shape=(rc, height, width),
                resampling=res_type,
            )

        ##..to read only the data without writing to file system
        if not out_tif:
            #.. to test: return a memory obj to use in next step
#             with MemoryFile() as memfile:
#                 with memfile.open(**profile) as dataset: # Open as DatasetWriter
#                     dataset.write(data)
#                     del data

#                 with memfile.open() as dataset:  # Reopen as DatasetReader
#                     yield dataset  # Note yield not return
            return "Not implemented yet"

        else:
            with rasterio.open(
                        out_tif, 'w',
                        driver='GTiff', width=width, height=height, compress='lzw',
                        count=rc,
                        crs = crs,
                        transform = transform,
                        dtype=data.dtype) as dst:
                    dst.write(data[0], indexes=1)

        el_time = (time.process_time() - start)
        elapsed_time = "CPU process time: %.1f [min] %.1f [s]" % (int(el_time/60), el_time % 60)
        print(elapsed_time)

