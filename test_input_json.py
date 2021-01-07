#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

#import functions from my library
import full_raster_computation as frc
import lib.tiling as tiling
import lib.merge as merge

# ### computing Aridity ##################
param_file = os.getcwd()+'/params.json'

#### computing
with open(param_file, 'r') as f:
    json_in = json.load(f)
    #for each indicator
    for obj in json_in:
        #compute each process
        for prc in obj['processes']:
            if prc['PROCESS_ID'] == 0:
                frc.compute_raster(prc['PARAMS']['classification'],
                                   prc['PARAMS']['output_param'],
                                   prc['PARAMS']['input_RST'])
            elif prc['PROCESS_ID'] == 1:
                tiling.stratification (
                    prc['PARAMS']['input_RST'],
                    prc['PARAMS']['LC_output_data'],
                    prc['PARAMS']['median_folder'],
                    prc['PARAMS']['resolution'],
                    prc['PARAMS']['classes'],
                    prc['PARAMS']['indicator_name'],
                    prc['PARAMS']['stat_method'],
                    prc['PARAMS']['stat_stat'])
            elif prc['PROCESS_ID'] == 2:
                merge.merge_raster(prc['PARAMS']['input_folder'],
                                   prc['PARAMS']['resolution'],
                                   prc['PARAMS']['merged_out_path'])

