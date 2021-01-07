#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import shutil
import rasterio
import rasterio.features
from rasterio.enums import Resampling
from rasterio import Affine, MemoryFile
from lib.LC_reclassify import reclassify as rcf
from lib.LC_mode import resample_raster as rsr
from lib.reproject import reproject_raster as rpj

def compute_raster(classification,output_param,input_RST):

    ### classification array   (from value, to value, assign this)
    ##1=Grass/shrubs; 2=Crop; 3=Forest; 4=Urban; 5=Wetlands; 6= Bare and Moss;

    ### folder output


    ######################################## main code cycle

    #default processing folder
    if os.path.splitext(input_RST)[-1] in ['.tif','.tiff']:
        processing_folder = os.path.dirname(input_RST)+'/tmp_processing'
    else:
        processing_folder = input_RST + '/tmp_processing'

    #if processing folder defined then reset to the specified one
    if output_param['processing_folder']:
        processing_folder = output_param['processing_folder']

    # check if output folder exists and cretae if not (!!! NOT subpaths !!!)
    if os.path.splitext(output_param['raster_output'])[-1] in ['.tif','.tiff']:
        if not os.path.exists( os.path.dirname( output_param['raster_output'] ) ):
            os.mkdir( os.path.dirname( output_param['raster_output'] ) )
    # output as folder for tiling
    else:
        if not os.path.exists(output_param['raster_output']):
            os.mkdir( output_param['raster_output'] )

    # for fd in output_param.keys():
    #     if not os.path.exists(output_param[fd]):
    #         os.mkdir(output_param[fd])

    def filePathStep(path, step):
        filename_in = os.path.basename(path)
        step_path = os.path.join(processing_folder, os.path.splitext(filename_in)[0] + '_' + str(step) + '_' + os.path.splitext(filename_in)[-1] )
        return step_path


    def rasterCycle(raster_in):
        """
        Raster Cycle process
        :param raster_in: raster full absolute path
        :return: last rasetr name processed
        """

        # create if not exists the processing folder
        if not os.path.exists(processing_folder):
            os.mkdir(processing_folder)

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

        # if output is a single tif then use output defined
        if os.path.splitext(output_param['raster_output'])[-1] in ['.tif','.tiff']:
            final_output = output_param['raster_output']
        #else use the folder output and create the output name
        else:
            final_output = os.path.join(output_param['raster_output'], os.path.basename(out_n))

        shutil.move(out_n, final_output)
        print('Raster Processing End, final result: ' + final_output)

        #delete processing folder if True
        if output_param['del_process']:
            shutil.rmtree(processing_folder)

        return final_output

    if os.path.splitext(input_RST)[-1] in ['.tif', '.tiff']:
        rasters = [ input_RST ]
    else:
        rasters = [ os.path.join( input_RST , f) for f in os.listdir( input_RST ) if os.path.splitext(f)[-1] == '.tif' ]

    for r in rasters:
        rasterCycle(r)
        #print (r)


#eg Land cover computation
# classification = [(0, 19, 0), (20, 39, 1), (40, 49, 2), (50, 59, 4), (60, 69, 6), (70, 89, 0), (90, 99, 5),
#                   (100, 109, 6), (110, 126, 3), (127, 255, 0)]
# output_param = {
#     'results': os.getcwd() + '/output',
#     'processing': os.getcwd() + '/process'
# }
# input_RST = os.path.join(os.getcwd(), 'input_raster/LC')
#
# compute_raster(classification,output_param,input_RST)