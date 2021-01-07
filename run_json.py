#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import sys, getopt

#import functions from my library
import full_raster_computation as frc
from lib import tiling as tiling
from lib import merge as merge


# ### computing ##################
param_file = os.path.dirname(os.path.abspath(__file__))+'/total_params_europe.json'



def computing(param_file):
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

    print('###END###')

def main(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print ('test.py -i <inputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg

    computing(inputfile)


if __name__ == "__main__":
   main(sys.argv[1:])