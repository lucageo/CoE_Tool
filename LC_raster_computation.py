#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import functions from my library
import os
import shutil
import rasterio
import rasterio.features
from rasterio.enums import Resampling
from rasterio import Affine, MemoryFile
from lib.LC_reclassify import reclassify as rcf
from lib.LC_mode import resample_raster as rsr
from lib.reproject import reproject_raster as rpj

def compute_raster(classification,output_fold,input_RST):

    ### classification array   (from value, to value, assign this)
    ##1=Grass/shrubs; 2=Crop; 3=Forest; 4=Urban; 5=Wetlands; 6= Bare and Moss;

    ### folder output


    ######################################## main code cycle

    for fd in output_fold.keys():
        if not os.path.exists(output_fold[fd]):
            os.mkdir(output_fold[fd])

    def filePathStep(path, step):
        filename_in = os.path.basename(path)
        step_path = os.path.join(output_fold['processing'], os.path.splitext(filename_in)[0] + '_' + str(step) + '_' + os.path.splitext(filename_in)[-1] )
        return step_path


    def rasterCycle(raster_in):
        """
        Raster Cycle process
        :param raster_in: raster full absolute path
        :return: last rasetr name processed
        """

        # reproject step --- Step1
        out_step1 = filePathStep(raster_in, 'reprojected')
        rep = rpj(raster_in, out_step1, epsg='EPSG:54009')

        #reclassify LC --- Step 2
        out_step2 = filePathStep(raster_in, 'reclassified')
        r3 = rcf(out_step1, classification, out_step2)

        #resample the Reclassified LC using Mode and scale 3  --- Step 2
        out_step3 = filePathStep(raster_in, 'resampled')
        res = rsr(out_step2, scale=250, res_type=Resampling.mode, out_tif=out_step3)


        #last step ... TODO .. define here the last output name
        out_n = out_step3


        final_output = os.path.join( output_fold['results'], os.path.basename(out_n))
        shutil.move(out_n, final_output)
        print('Raster Processing End, final result: ' + final_output)
        return final_output

    rasters = [ os.path.join( input_RST , f) for f in os.listdir( input_RST ) if os.path.splitext(f)[-1] == '.tif' ]

    for r in rasters:
        rasterCycle(r)
        #print (r)


#eg Land cover computation
classification = [(0, 19, 0), (20, 39, 1), (40, 49, 2), (50, 59, 4), (60, 69, 6), (70, 89, 0), (90, 99, 5),
                  (100, 109, 6), (110, 126, 3), (127, 255, 0)]
output_fold = {
    'results': os.getcwd() + '/output',
    'processing': os.getcwd() + '/process'
}
input_RST = os.path.join(os.getcwd(), 'input_raster/LC')

compute_raster(classification,output_fold,input_RST)