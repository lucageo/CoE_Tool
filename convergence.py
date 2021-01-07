#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import functions from my library
import os
import full_raster_computation as frc
#
# ### computing Aridity ##################
# classification_aridity = [(0, 1, 0), (2, 5, 1), (6, 8, 0)]
# output_param = {
# #     'results': os.getcwd() + '/output_ar',
# #     'processing': os.getcwd() + '/process_ar',
#
#      'raster_output' : os.getcwd() + '/finalout/aridity.tif', #folders must exists
#      'processing_folder': False, # false use the default one or specify a folder path here eg. "../out1",
#      'del_process': False # by default process raster wil be deleted if True
#  }
#
# # input raster folder (all rasters contained in the folder will be processed
# #input_RST = os.path.join(os.getcwd(), 'input_raster/Aridity')
# input_RST = os.path.join(os.getcwd(), 'input_raster/Aridity/ai10class.tif')
#
# frc.compute_raster(classification_aridity,output_param,input_RST)


### computing Land Cover ###############

classification_LC = [(0, 19, 0), (20, 39, 1), (40, 49, 2), (50, 59, 4), (60, 69, 6), (70, 89, 0), (90, 99, 5),
                  (100, 109, 6), (110, 126, 3), (127, 255, 0)]
output_fold = {
#     'results': os.getcwd() + '/output_LC',
#     'processing': os.getcwd() + '/process_LC'

    'raster_output': os.getcwd() + '/finalout/LC', #output as folder because processing tiles, finalouts must exists before
    'processing_folder': False,  # false use the default one or specify a folder path here eg. "../out1",
    'del_process': False  # by default process raster wil be deleted if True
}
input_RST = os.path.join(os.getcwd(), 'input_raster/LC')
frc.compute_raster(classification_LC,output_fold,input_RST)


### computing Population###############

import lib.tiling as tiling

input_indicator_path = os.getcwd() + "/input_raster/POP/pop2015.tif"
input_LC = os.getcwd() + "/output/"
output_indicator = os.getcwd() + '/indicator_median/'
resolution = 250
classes = [1, 2, 3, 4, 5, 6]
indicator_name = 'population'
stat_method = 'greater'
stat_stat = 'median'

tiling.stratification (input_indicator_path,input_LC,output_indicator,resolution,classes,indicator_name,stat_method,stat_stat)

##...merge
import lib.merge as merge

input_folder = os.getcwd() + '/indicator_median/'
resolution=250
merged_out_path="merged_pop.tif"

merge.merge_raster(input_folder, resolution, merged_out_path)

### computing Built-up ###############

import lib.tiling as tiling

input_indicator_path = os.getcwd() + "/input_raster/BUILT_UP/builtup.tif"
input_LC = os.getcwd() + "/output/"
output_indicator = os.getcwd() + '/indicator_median/'
resolution = 250
classes = [1, 2, 3, 4, 5, 6]
indicator_name = 'builtup'
stat_method = 'greater'
stat_stat = 'median'

tiling.stratification (input_indicator_path,input_LC,output_indicator,resolution,classes,indicator_name,stat_method,stat_stat)

##...merge
import lib.merge as merge

input_folder = os.getcwd() + '/indicator_median/'
resolution=250
merged_out_path="merged_builtup.tif"

merge.merge_raster(input_folder, resolution, merged_out_path)
